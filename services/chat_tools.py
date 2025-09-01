from typing import Tuple, Dict, Any, Optional, List
from sqlalchemy.orm import Session
import re, logging

from .product_service import search_products, get_by_code, to_product_out
from .chat_order import create_order_from_chat

log = logging.getLogger("services.chat_tools")

# In-memory state
_LAST_SELECTED: Dict[str, int] = {}        # conv_id -> product_id
_LAST_RESULTS: Dict[str, List[int]] = {}   # conv_id -> [product_id...]

# Allow A0001, PRD-1234, T-0002, etc. (letters 1-4 + optional dash + 3-6 digits)
CODE_RE    = re.compile(r"(?<![A-Za-z0-9])([A-Za-z]{1,4}-?\d{3,6})(?![A-Za-z0-9])", re.IGNORECASE)
OPTION_RE  = re.compile(r"گزینه\s*(\d+)", re.IGNORECASE)
CONFIRM_RE = re.compile(r"(تایید|تاییدش|بله|اوکی|ok|باشه|همینو\s*می\s*خوام|همینو)", re.IGNORECASE)
NUMBER_RE  = re.compile(r"\b(\d{1,3})\b")

# Persian digits → Latin
P2L = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")  # Persian to Latin digits

# Add greeting detection
GREETING_RE = re.compile(r"(سلام|درود|هلا|هی|hi|hello|hey)", re.IGNORECASE)

def _norm(s: str) -> str:
    return (s or "").translate(P2L).strip()

def _ensure_dict(obj):
    if hasattr(obj, "model_dump"): return obj.model_dump()
    if hasattr(obj, "dict"):       return obj.dict()
    return obj

def _debug(prefix: str, **kw):
    log.info("%s %s", prefix, kw)

def extract_code(text: str) -> Optional[str]:
    t = _norm(text)
    m = CODE_RE.search(t)
    return m.group(1).upper() if m else None

def extract_option_index(text: str) -> Optional[int]:
    t = _norm(text)
    m = OPTION_RE.search(t)
    if not m: return None
    try:
        i = int(m.group(1))
        return i if i >= 1 else None
    except:
        return None

def extract_qty(text: str) -> int:
    t = _norm(text)
    m = NUMBER_RE.search(t)
    if not m: return 1
    try:
        return max(1, int(m.group(1)))
    except:
        return 1

def product_summary(po: Dict[str, Any]) -> str:
    name  = po.get("name") or "-"
    code  = po.get("code") or "-"
    price = po.get("price")
    stock = po.get("total_stock", po.get("stock"))
    lines = [f"• {name} (کد {code})"]
    if price is not None: lines.append(f"قیمت: {price}")
    if stock is not None: lines.append(f"موجودی: {stock}")
    return "مشخصات محصول:\n" + "\n".join(lines)

def handle_chat_turn(
    db: Session,
    conv_id: str,
    message_text: str
) -> Tuple[str, Dict[str, Any]]:
    msg = (message_text or "")
    _debug("turn:start", conv_id=conv_id, msg=msg)

    # 0) Greeting branch - handle first
    if GREETING_RE.search(msg):
        _debug("greeting:detected", msg=msg)
        return ("سلام! 🌟 به فروشگاه ما خوش آمدید! 👔\n\nمن آماده‌ام تا در انتخاب محصولات مورد نظرتان کمکتان کنم. 💡\n\nچه محصولی مدنظرتان است؟ (مثل شلوار، پیراهن، کت و...) یا کد محصول را بفرستید.", {"slots": {}})

    # 1) Confirm branch
    if CONFIRM_RE.search(msg):
        pid = _LAST_SELECTED.get(conv_id)
        _debug("confirm:check", selected_pid=pid)
        if not pid:
            return ("محصولی انتخاب نشده. ابتدا کد محصول را ارسال کنید.", {"slots": {}})
        qty = extract_qty(msg)
        try:
            order = create_order_from_chat(db, product_id=pid, quantity=qty)
            _LAST_SELECTED.pop(conv_id, None)
            _debug("confirm:created", order_id=getattr(order, "id", None), order_number=getattr(order, "order_number", None))
            reply = f"سفارش شما ثبت شد ✅\nکد سفارش: #{getattr(order, 'order_number', getattr(order, 'id', ''))}\nوضعیت: در انتظار تایید"
            return (reply, {"order_id": getattr(order, "id", None), "status": "pending", "slots": {}})
        except Exception:
            log.exception("confirm/create failed")
            return ("در ثبت سفارش مشکلی پیش آمد. لطفاً دوباره تلاش کنید.", {"slots": {}})

    # 2) Code-first path
    code = extract_code(msg)
    _debug("code:extract", code=code)
    if code:
        p = get_by_code(db, code)
        if p:
            po = _ensure_dict(to_product_out(p))
            _LAST_SELECTED[conv_id] = po["id"]
            _debug("code:match", product_id=po["id"], conv_id=conv_id)
            return (product_summary(po) + "\n\nتایید می‌کنی؟", {"slots": {"code": code}})
        return ("محصولی با این کد پیدا نشد.", {"slots": {}})

    # 3) Option "گزینه 1"
    opt = extract_option_index(msg)
    _debug("option:extract", option=opt)
    if opt:
        ids = _LAST_RESULTS.get(conv_id) or []
        _debug("option:ids", ids=ids)
        if 1 <= opt <= len(ids):
            pid = ids[opt - 1]
            # We need the full product; reuse search and pick by id
            items = search_products(db, q=None, code=None, category_id=None, limit=50) or []
            picked = None
            for it in items:
                if getattr(it, "id", None) == pid:
                    picked = it
                    break
            if picked:
                po = _ensure_dict(to_product_out(picked))
                _LAST_SELECTED[conv_id] = po["id"]
                _debug("option:pick", product_id=po["id"])
                return (product_summary(po) + "\n\nتایید می‌کنی؟", {"slots": {"code": po.get("code")}})
            return ("نتوانستم گزینه انتخابی را پیدا کنم. لطفاً کد محصول را بفرستید.", {"slots": {}})

    # 4) Text search - only if it looks like a product query
    if len(msg.strip()) > 2 and not msg.strip().lower() in ["سلام", "hi", "hello", "hey"]:
        items = search_products(db, q=msg, code=None, category_id=None, limit=5) or []
        _debug("search:results", count=len(items))
        if len(items) == 0:
            return ("محصولی مطابق جستجو پیدا نشد. می‌تونید کد محصول را بفرستید.", {"slots": {}})

        if len(items) == 1:
            po = _ensure_dict(to_product_out(items[0]))
            _LAST_SELECTED[conv_id] = po["id"]
            _LAST_RESULTS[conv_id] = [po["id"]]
            _debug("search:single", product_id=po["id"])
            return (product_summary(po) + "\n\nتایید می‌کنی؟", {"slots": {"code": po.get("code")}})

        # multiple → cache for "گزینه N"
        ids = []
        lines = []
        for i, p in enumerate(items[:5], start=1):
            ids.append(getattr(p, "id", None))
            code_i = getattr(p, "code", None) or "-"
            name_i = getattr(p, "name", "")
            price_i = getattr(p, "price", None)
            lines.append(f"{i}) {name_i} (کد {code_i}) - قیمت: {price_i if price_i is not None else 'نامشخص'}")
        _LAST_RESULTS[conv_id] = ids
        _debug("search:multi", ids=ids)
        return ("🌟 چند گزینه پیدا کردم:\n" + "\n".join(lines) + "\n\nبرای دریافت جزئیات، کد محصول را بفرستید یا «گزینه 1» را بنویسید.", {"slots": {"results_count": len(items)}})
    
    # 5) Default response for short/non-product messages
    return ("سلام! 🌟\n\nچطور می‌تونم کمکتون کنم؟\n\n• کد محصول را بفرستید (مثل A0001)\n• نام محصول را جستجو کنید (مثل شلوار)\n• یا بپرسید چه محصولاتی داریم", {"slots": {}})

# Router entry point
def handle_tool(action: Optional[str], slots: Dict[str, Any], db: Session, rid: str, conv_id: str, message_text: str):
    _debug("router:enter", rid=rid, conv_id=conv_id, action=action, msg=message_text)
    reply, extra = handle_chat_turn(db, conv_id, message_text)
    _debug("router:exit", rid=rid, conv_id=conv_id, extra_keys=list(extra.keys()))
    return reply, extra 