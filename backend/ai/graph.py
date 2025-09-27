from typing import TypedDict, Optional, List, Dict, Any
import re
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from database import SessionLocal
from backend.ai.tools import tool_search_products, tool_get_product_by_code, tool_create_order

CODE_RE = re.compile(r"[A-Za-z]{1,4}\d{3,6}")
CONFIRM_RE = re.compile(r"(تایید|تایید می‌کنم|باشه|اوکی|بله|ok|yes)", re.I)
QTY_RE = re.compile(r"(\d+)\s*(عدد|تا)?", re.I)

def _normalize_digits(s: str) -> str:
    # Persian/Arabic → ASCII
    trans = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
    return s.translate(trans)

def _extract_qty(msg: str, default: int = 1) -> int:
    m = QTY_RE.search(_normalize_digits(msg))
    return int(m.group(1)) if m else default

class ChatState(TypedDict, total=False):
    msg: str
    reply: str
    stage: str                 # "idle" | "have_product" | "need_attrs" | "await_confirm"
    product: Optional[Dict[str, Any]]
    candidates: List[Dict[str, Any]]
    qty: int
    size: Optional[str]
    color: Optional[str]
    order: Optional[Dict[str, Any]]

def _fmt_details(p: Dict[str, Any]) -> str:
    return f"مشخصات:\n• {p['name']} (کد {p['code']})\nقیمت: {p['price']}\nموجودی: {p['stock']}\nتایید می‌کنی؟"

def node_by_code(state: ChatState) -> ChatState:
    msg = state.get("msg") or ""
    m = CODE_RE.search(msg)
    if not m:
        state["reply"] = "کد محصول نامعتبر است. لطفاً کد صحیح را ارسال کنید. 😊"
        return state
    code = m.group(0)
    with SessionLocal() as db:
        p = tool_get_product_by_code(db, code)
    if not p:
        state["reply"] = "متاسفانه محصولی با این کد موجود نیست. لطفاً کد صحیح را وارد کنید."
        return state
    if p["stock"] <= 0:
        state["reply"] = "متاسفانه این محصول موجود نیست. 😔"
        return state
    state["product"] = p
    state["stage"] = "have_product"
    state["reply"] = f"عالی! این مشخصات رو دیدم: ✨\n• {p['name']} (کد {p['code']})\nقیمت: {p['price']}\nموجودی: {p['stock']}\nمی‌خوای چند عدد بفرستم؟ اگه سایز/رنگ داری بگو (مثلاً: ۲ مشکی M)."
    return state

def node_search(state: ChatState) -> ChatState:
    msg = state.get("msg") or ""
    with SessionLocal() as db:
        items = tool_search_products(db, q=msg, limit=5)
    state["candidates"] = items
    if not items:
        state["reply"] = "متاسفانه محصولی با این مشخصات موجود نیست. لطفاً کد محصول را ارسال کنید."
        return state
    if len(items) == 1:
        p = items[0]
        if p["stock"] <= 0:
            state["reply"] = "این گزینه موجود نیست. محصول دیگری را امتحان کنید. 😔"
            return state
        state["product"] = p
        state["stage"] = "have_product"
        state["reply"] = f"عالی! این مشخصات رو دیدم: ✨\n• {p['name']} (کد {p['code']})\nقیمت: {p['price']}\nموجودی: {p['stock']}\nمی‌خوای چند عدد بفرستم؟ اگه سایز/رنگ داری بگو (مثلاً: ۲ مشکی M)."
        return state
    lines = [f"{i+1}) {p['name']} (کد {p['code']}) - {p['price']}" for i, p in enumerate(items)]
    state["reply"] = "چند گزینه پیدا کردم: 🔍\n" + "\n".join(lines) + "\nکد محصول را بفرست."
    return state

def node_refine(state: ChatState) -> ChatState:
    msg = state.get("msg") or ""
    p = state.get("product")
    if not p:
        state["reply"] = "محصولی انتخاب نشده. کد محصول را ارسال کنید. 😊"
        return state
    
    # Handle "همینو می‌خوام" - keep qty=1 and proceed
    if "همینو می‌خوام" in msg or "همینو میخوام" in msg:
        state["qty"] = 1
    else:
        # Extract quantity
        state["qty"] = _extract_qty(msg, state.get("qty", 1))
    
    # Extract color - Persian tokens
    if "مشکی" in msg:
        state["color"] = "black"
    elif "سفید" in msg:
        state["color"] = "white"
    
    # Extract size - Persian tokens
    size_map = {"کوچک": "S", "مدیوم": "M", "بزرگ": "L"}
    for persian_size, english_size in size_map.items():
        if persian_size in msg:
            state["size"] = english_size
            break
    
    # Also support English sizes
    if any(k in msg.lower() for k in ["medium", "m"]):
        state["size"] = "M"
    if any(k in msg.lower() for k in ["small", "s"]):
        state["size"] = "S"
    if any(k in msg.lower() for k in ["large", "l"]):
        state["size"] = "L"
    
    # Check what's still needed
    attrs = p.get("attributes") or {}
    need_size = bool(attrs.get("size"))
    need_color = bool(attrs.get("color"))
    
    missing = []
    if need_size and not state.get("size"):
        missing.append("سایز")
    if need_color and not state.get("color"):
        missing.append("رنگ")
    
    if missing:
        state["stage"] = "need_attrs"
        missing_str = " و ".join(missing)
        state["reply"] = f"لطفاً {missing_str} رو هم مشخص کن. 😊\nمثال: {state['qty']} عدد {missing_str} مورد نظرت رو بگو."
        return state
    
    # All attributes collected, ready for confirmation
    state["stage"] = "await_confirm"
    summary = f"خلاصه سفارش: 📋\n• {p['name']} (کد {p['code']})\n• تعداد: {state['qty']}"
    if state.get("size"):
        summary += f"\n• سایز: {state['size']}"
    if state.get("color"):
        summary += f"\n• رنگ: {state['color']}"
    summary += f"\n• قیمت کل: {p['price'] * state['qty']}\nآیا تایید می‌کنی؟ ✨"
    state["reply"] = summary
    return state

def node_maybe_confirm(state: ChatState) -> ChatState:
    msg = state.get("msg") or ""
    p = state.get("product")
    if not p:
        state["reply"] = "محصولی انتخاب نشده. کد محصول را ارسال کنید. 😊"
        return state
    
    # Check for confirmation
    if CONFIRM_RE.search(msg):
        # Create the order
        with SessionLocal() as db:
            o = tool_create_order(db, product_id=p["id"], qty=state.get("qty", 1),
                                  size=state.get("size"), color=state.get("color"))
        state["order"] = o
        state["reply"] = f"سفارش ثبت شد ✅\nکد سفارش: {o['order_number']}\nوضعیت: {o['status']}\nممنون از خرید شما! 😊"
        return state
    else:
        # Not confirmed, ask again
        state["stage"] = "await_confirm"
        state["reply"] = "برای ثبت، فقط بگو «تایید» یا اگر تغییری می‌خوای وارد کن. 😊"
        return state

# Routing logic functions
def route_after_search(state: ChatState) -> str:
    """Route after search - if we have a product, go to refine"""
    if state.get("product") and state.get("stage") == "have_product":
        return "refine"
    return "end"

def route_after_refine(state: ChatState) -> str:
    """Route after refine - if awaiting confirmation, go to maybe_confirm"""
    if state.get("stage") == "await_confirm":
        return "maybe_confirm"
    return "refine"  # Stay in refine if still missing attributes

def route_after_confirm(state: ChatState) -> str:
    """Route after maybe_confirm - always end"""
    return "end"

# Build the graph
graph = StateGraph(ChatState)

# Add nodes
graph.add_node("search", RunnableLambda(node_search))
graph.add_node("by_code", RunnableLambda(node_by_code))
graph.add_node("refine", RunnableLambda(node_refine))
graph.add_node("maybe_confirm", RunnableLambda(node_maybe_confirm))

# Set entry point
graph.set_entry_point("search")

# Add edges
graph.add_conditional_edges(
    "search",
    lambda state: "by_code" if CODE_RE.search(state.get("msg", "")) else "end",
    {"by_code": "by_code", "end": END}
)

graph.add_conditional_edges("by_code", route_after_search, {"refine": "refine", "end": END})
graph.add_conditional_edges("refine", route_after_refine, {"refine": "refine", "maybe_confirm": "maybe_confirm"})
graph.add_conditional_edges("maybe_confirm", route_after_confirm, {"end": END})

app = graph.compile()
