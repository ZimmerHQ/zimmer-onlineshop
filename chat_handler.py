from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Dict, Any, List
from services.chat.state import ConversationState, Slots, merge_slots, find_by_index, missing_fields, ListItem
from services.chat.ner import extract_slots
from services.chat.agent import call_llm
from gpt_service import ask_gpt
from product_handler import search_products_by_name
from order_handler import create_simple_order
from database import get_db
from app_logging.chat_log import log_message
from sqlalchemy.orm import Session
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])

# MVP in-memory store (replace with Redis/DB later)
CONV_STORE: Dict[str, ConversationState] = {}

# Generic list request phrases
GENERIC_LIST_PHRASES = ["لیست", "لیست بفرست", "چه محصولاتی داری", "محصولات", "لیست محصولات", "show list", "list"]

def _looks_like_list_request(text: str) -> bool:
    t = (text or "").strip()
    return any(p in t for p in GENERIC_LIST_PHRASES)

def _direct_match_product(user_text: str, products) -> int | None:
    """
    Try to map free text to a single product by name contains.
    Returns product_id if unique match, else None.
    """
    t = (user_text or "").strip()
    if not t or not products:
        return None
    matches = []
    for p in products:
        name = str(getattr(p, "name", "") or "")
        if name and t in name:
            matches.append(p)
    if len(matches) == 1:
        return int(getattr(matches[0], "id"))
    return None

class ChatRequest(BaseModel):
    conversation_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str
    slots: Slots

def _get_state(cid: str) -> ConversationState:
    if cid not in CONV_STORE:
        CONV_STORE[cid] = ConversationState()
    return CONV_STORE[cid]

def _render_list_and_store(state: ConversationState, products, prefix: str = "") -> ChatResponse:
    state.last_list = []
    if not products:
        return ChatResponse(reply=prefix + "فعلاً محصولی مطابق جستجو پیدا نشد. نام یا دستهٔ دیگری را بفرست.", slots=state.slots)
    lines = [prefix + "محصولات موجود:"]
    for i, p in enumerate(products[:5], start=1):
        li = ListItem(
            idx=i,
            product_id=int(getattr(p, "id", i)),
            name=str(getattr(p, "name", "محصول")),
            price=float(getattr(p, "price", 0.0)),
            sizes=[str(s) for s in getattr(p, "sizes", [])] if hasattr(p,"sizes") else None,
            colors=[str(c) for c in getattr(p, "colors", [])] if hasattr(p,"colors") else None,
        )
        state.last_list.append(li)
        sizes = ",".join(li.sizes or [])
        colors = ",".join(li.colors or [])
        lines.append(f"{i}) {li.name} — {li.price:.0f} تومان — سایزها: {sizes or '-'} — رنگ‌ها: {colors or '-'}")
    lines.append("برای انتخاب، فقط شماره را بفرست.")
    return ChatResponse(reply="\n".join(lines), slots=state.slots)

def _summary(state: ConversationState, name_override: str | None = None) -> str:
    name = name_override or next((it.name for it in state.last_list if it.product_id == state.slots.product_id), "-")
    return f"خلاصه سفارش: {name}، سایز {state.slots.size}، رنگ {state.slots.color}، تعداد {state.slots.qty or 1}"

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest, raw: Request, db: Session = Depends(get_db)):
    try:
        # Debug log raw request for troubleshooting
        raw_body = await raw.body()
        logging.info(f"📥 Raw request body: {raw_body.decode(errors='ignore')}")
        logging.info(f"✅ Parsed: conversation_id={req.conversation_id}, message={req.message}")

        state = _get_state(req.conversation_id)
        user_text = (req.message or "").strip()

        # Log user message
        try:
            log_message(db, req.conversation_id, role="user", text=user_text, intent=None, slots=state.slots.model_dump())
        except Exception as e:
            print("⚠️ failed to log incoming message:", repr(e))

        # Fallback GPT response if LLM agent fails
        fallback_gpt_response = None
        try:
            fallback_gpt_response = ask_gpt(user_text)
        except Exception as e:
            print(f"Error in GPT service: {e}")
            fallback_gpt_response = "متاسفم، خطایی رخ داد. لطفاً دوباره تلاش کنید."

        # remember last query candidates
        if user_text and not user_text.isdigit():
            state.last_query = user_text

        # 1) lightweight NER first (size/color)
        ner_slots = extract_slots(user_text)
        state.slots = merge_slots(state.slots, ner_slots)

        # If user explicitly asked for a list, do a search using last_query or fallback keyword
        if _looks_like_list_request(user_text):
            q = state.last_query or "جدید"
            products = search_products_by_name(db, q) or []
            resp = _render_list_and_store(state, products)
            
            # Log assistant reply
            try:
                log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="LIST_PRODUCTS", slots=state.slots.model_dump())
            except Exception as e:
                print("⚠️ failed to log assistant message:", repr(e))
            
            return resp

        # 2) LLM decides action
        agent = call_llm([], state, user_text)
        state.slots = merge_slots(state.slots, agent.slots)
        action = agent.action.upper()

        # 3) Handle actions
        if action == "SEARCH_PRODUCTS":
            q = state.last_query or user_text or "محصول"
            products = search_products_by_name(db, q) or []

            # Try direct match by name
            pid = _direct_match_product(user_text, products)
            if pid:
                state.slots.product_id = pid
                need = missing_fields(state.slots)
                if "size" in need or "color" in need:
                    resp = ChatResponse(reply="سایز و رنگ مورد نظرت را بگو (مثلاً: 43 مشکی).", slots=state.slots)
                    # Log assistant reply
                    try:
                        log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="COLLECT_VARIANTS", slots=state.slots.model_dump())
                    except Exception as e:
                        print("⚠️ failed to log assistant message:", repr(e))
                    return resp
                resp = ChatResponse(reply=_summary(state) + "\nتایید می‌کنی؟", slots=state.slots)
                # Log assistant reply
                try:
                    log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="CONFIRM_ORDER", slots=state.slots.model_dump())
                except Exception as e:
                    print("⚠️ failed to log assistant message:", repr(e))
                return resp

            # If exactly one product found, auto-select it
            if len(products) == 1:
                only = products[0]
                state.last_list = [
                    ListItem(idx=1,
                             product_id=int(getattr(only, "id", 1)),
                             name=str(getattr(only, "name", "محصول")),
                             price=float(getattr(only, "price", 0.0)),
                             sizes=[str(s) for s in getattr(only, "sizes", [])] if hasattr(only,"sizes") else None,
                             colors=[str(c) for c in getattr(only, "colors", [])] if hasattr(only,"colors") else None)
                ]
                state.slots.product_id = int(getattr(only, "id", 1))
                need = missing_fields(state.slots)
                if "size" in need or "color" in need:
                    resp = ChatResponse(reply=f"{_summary(state, name_override=state.last_list[0].name)}\nسایز و رنگ را بگو (مثلاً: 43 مشکی).", slots=state.slots)
                    # Log assistant reply
                    try:
                        log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="COLLECT_VARIANTS", slots=state.slots.model_dump())
                    except Exception as e:
                        print("⚠️ failed to log assistant message:", repr(e))
                    return resp
                resp = ChatResponse(reply=_summary(state) + "\nتایید می‌کنی؟", slots=state.slots)
                # Log assistant reply
                try:
                    log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="CONFIRM_ORDER", slots=state.slots.model_dump())
                except Exception as e:
                    print("⚠️ failed to log assistant message:", repr(e))
                return resp

            # Otherwise render a list (top 5)
            resp = _render_list_and_store(state, products)
            # Log assistant reply
            try:
                log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="LIST_PRODUCTS", slots=state.slots.model_dump())
            except Exception as e:
                print("⚠️ failed to log assistant message:", repr(e))
            return resp

        if action == "SELECT_PRODUCT":
            # User sent a number - select from last_list
            if not state.last_list:
                resp = ChatResponse(reply="لطفاً اول محصول را انتخاب کن. اگر لیست می‌خواهی اسم محصول یا دسته را بفرست.", slots=state.slots)
                # Log assistant reply
                try:
                    log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="CLARIFY", slots=state.slots.model_dump())
                except Exception as e:
                    print("⚠️ failed to log assistant message:", repr(e))
                return resp
            
            try:
                idx = int(user_text) - 1
                if 0 <= idx < len(state.last_list):
                    selected = state.last_list[idx]
                    state.slots.product_id = selected.product_id
                    need = missing_fields(state.slots)
                    if "size" in need or "color" in need:
                        resp = ChatResponse(reply=f"{_summary(state, name_override=selected.name)}\nسایز و رنگ را بگو (مثلاً: 43 مشکی).", slots=state.slots)
                        # Log assistant reply
                        try:
                            log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="COLLECT_VARIANTS", slots=state.slots.model_dump())
                        except Exception as e:
                            print("⚠️ failed to log assistant message:", repr(e))
                        return resp
                    resp = ChatResponse(reply=_summary(state) + "\nتایید می‌کنی؟", slots=state.slots)
                    # Log assistant reply
                    try:
                        log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="CONFIRM_ORDER", slots=state.slots.model_dump())
                    except Exception as e:
                        print("⚠️ failed to log assistant message:", repr(e))
                    return resp
                else:
                    resp = ChatResponse(reply="شماره نامعتبر است. لطفاً شماره صحیح را انتخاب کن.", slots=state.slots)
                    # Log assistant reply
                    try:
                        log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="CLARIFY", slots=state.slots.model_dump())
                    except Exception as e:
                        print("⚠️ failed to log assistant message:", repr(e))
                    return resp
            except ValueError:
                resp = ChatResponse(reply="لطفاً فقط شماره محصول را بفرست.", slots=state.slots)
                # Log assistant reply
                try:
                    log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="CLARIFY", slots=state.slots.model_dump())
                except Exception as e:
                    print("⚠️ failed to log assistant message:", repr(e))
                return resp

        if action == "COLLECT_VARIANTS":
            # Extract size/color from user input
            ner_slots = extract_slots(user_text)
            state.slots = merge_slots(state.slots, ner_slots)
            
            need = missing_fields(state.slots)
            if need:
                # ask only for missing piece
                if "product" in need:
                    resp = ChatResponse(reply="لطفاً اول محصول را انتخاب کن. اگر لیست می‌خواهی اسم محصول یا دسته را بفرست.", slots=state.slots)
                    # Log assistant reply
                    try:
                        log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="CLARIFY", slots=state.slots.model_dump())
                    except Exception as e:
                        print("⚠️ failed to log assistant message:", repr(e))
                    return resp
                if "size" in need and "color" in need:
                    resp = ChatResponse(reply="سایز و رنگ مورد نظرت را بگو (مثلاً: 43 مشکی).", slots=state.slots)
                    # Log assistant reply
                    try:
                        log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="COLLECT_VARIANTS", slots=state.slots.model_dump())
                    except Exception as e:
                        print("⚠️ failed to log assistant message:", repr(e))
                    return resp
                if "size" in need:
                    resp = ChatResponse(reply="سایز مدنظر را بفرست (مثلاً: 43).", slots=state.slots)
                    # Log assistant reply
                    try:
                        log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="COLLECT_VARIANTS", slots=state.slots.model_dump())
                    except Exception as e:
                        print("⚠️ failed to log assistant message:", repr(e))
                    return resp
                if "color" in need:
                    resp = ChatResponse(reply="رنگ مدنظر را بگو (مثلاً: مشکی).", slots=state.slots)
                    # Log assistant reply
                    try:
                        log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="COLLECT_VARIANTS", slots=state.slots.model_dump())
                    except Exception as e:
                        print("⚠️ failed to log assistant message:", repr(e))
                    return resp
            
            # All slots filled, move to confirmation
            resp = ChatResponse(reply=_summary(state) + "\nتایید می‌کنی؟", slots=state.slots)
            # Log assistant reply
            try:
                log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="CONFIRM_ORDER", slots=state.slots.model_dump())
            except Exception as e:
                print("⚠️ failed to log assistant message:", repr(e))
            return resp

        if action == "CONFIRM_ORDER":
            # User confirmed - create order
            if user_text.lower() in ["بله", "yes", "تایید", "ok", "باشه"]:
                try:
                    order = create_simple_order(
                        product_id=state.slots.product_id,
                        size=state.slots.size,
                        color=state.slots.color,
                        qty=state.slots.qty or 1,
                        meta={"source":"dashboard_chat"}
                    )
                    
                    # Log order creation audit
                    try:
                        log_message(db, req.conversation_id, role="system", text=f"ORDER_CREATED id={order.get('id')}", intent="ORDER_CREATED", slots=state.slots.model_dump())
                    except Exception as e:
                        print("⚠️ failed to log order audit:", repr(e))
                    
                    # reset slots for next order, keep last_list for convenience
                    pid = state.slots.product_id
                    state.slots = Slots(product_id=pid, size=None, color=None, qty=1)
                    resp = ChatResponse(reply=f"سفارش با موفقیت ثبت شد ✅ کد سفارش: {order.get('id','-')}", slots=state.slots)
                    # Log assistant reply
                    try:
                        log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="ORDER_CREATED", slots=state.slots.model_dump())
                    except Exception as e:
                        print("⚠️ failed to log assistant message:", repr(e))
                    return resp
                except Exception as e:
                    print("Order error:", repr(e))
                    resp = ChatResponse(reply="متأسفانه هنگام ثبت سفارش خطایی رخ داد. لطفاً دوباره امتحان کن.", slots=state.slots)
                    # Log assistant reply
                    try:
                        log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="ERROR", slots=state.slots.model_dump())
                    except Exception as e:
                        print("⚠️ failed to log assistant message:", repr(e))
                    return resp
            else:
                # User didn't confirm - ask again
                resp = ChatResponse(reply=_summary(state) + "\nتایید می‌کنی؟ (بله/خیر)", slots=state.slots)
                # Log assistant reply
                try:
                    log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="CONFIRM_ORDER", slots=state.slots.model_dump())
                except Exception as e:
                    print("⚠️ failed to log assistant message:", repr(e))
                return resp

        if action == "CREATE_ORDER":
            # Direct order creation (all slots ready)
            need = missing_fields(state.slots)
            if need:
                # ask only for missing piece
                if "product" in need:
                    resp = ChatResponse(reply="لطفاً اول محصول را انتخاب کن. اگر لیست می‌خواهی اسم محصول یا دسته را بفرست.", slots=state.slots)
                    # Log assistant reply
                    try:
                        log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="CLARIFY", slots=state.slots.model_dump())
                    except Exception as e:
                        print("⚠️ failed to log assistant message:", repr(e))
                    return resp
                if "size" in need and "color" in need:
                    resp = ChatResponse(reply="سایز و رنگ مورد نظرت را بگو (مثلاً: 43 مشکی).", slots=state.slots)
                    # Log assistant reply
                    try:
                        log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="COLLECT_VARIANTS", slots=state.slots.model_dump())
                    except Exception as e:
                        print("⚠️ failed to log assistant message:", repr(e))
                    return resp
                if "size" in need:
                    resp = ChatResponse(reply="سایز مدنظر را بفرست (مثلاً: 43).", slots=state.slots)
                    # Log assistant reply
                    try:
                        log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="COLLECT_VARIANTS", slots=state.slots.model_dump())
                    except Exception as e:
                        print("⚠️ failed to log assistant message:", repr(e))
                    return resp
                if "color" in need:
                    resp = ChatResponse(reply="رنگ مدنظر را بگو (مثلاً: مشکی).", slots=state.slots)
                    # Log assistant reply
                    try:
                        log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="COLLECT_VARIANTS", slots=state.slots.model_dump())
                    except Exception as e:
                        print("⚠️ failed to log assistant message:", repr(e))
                    return resp
            
            try:
                order = create_simple_order(
                    product_id=state.slots.product_id,
                    size=state.slots.size,
                    color=state.slots.color,
                    qty=state.slots.qty or 1,
                    meta={"source":"dashboard_chat"}
                )
                
                # Log order creation audit
                try:
                    log_message(db, req.conversation_id, role="system", text=f"ORDER_CREATED id={order.get('id')}", intent="ORDER_CREATED", slots=state.slots.model_dump())
                except Exception as e:
                    print("⚠️ failed to log order audit:", repr(e))
                
                # reset slots for next order, keep last_list for convenience
                pid = state.slots.product_id
                state.slots = Slots(product_id=pid, size=None, color=None, qty=1)
                resp = ChatResponse(reply=f"سفارش با موفقیت ثبت شد ✅ کد سفارش: {order.get('id','-')}", slots=state.slots)
                # Log assistant reply
                try:
                    log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="ORDER_CREATED", slots=state.slots.model_dump())
                except Exception as e:
                    print("⚠️ failed to log assistant message:", repr(e))
                return resp
            except Exception as e:
                print("Order error:", repr(e))
                resp = ChatResponse(reply="متأسفانه هنگام ثبت سفارش خطایی رخ داد. لطفاً دوباره امتحان کن.", slots=state.slots)
                # Log assistant reply
                try:
                    log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="ERROR", slots=state.slots.model_dump())
                except Exception as e:
                    print("⚠️ failed to log assistant message:", repr(e))
                return resp

        if action == "SMALL_TALK":
            resp = ChatResponse(reply="در خدمتم. اگر محصول خاصی مدنظرته بگو تا راهنمایی کنم.", slots=state.slots)
            # Log assistant reply
            try:
                log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="SMALL_TALK", slots=state.slots.model_dump())
            except Exception as e:
                print("⚠️ failed to log assistant message:", repr(e))
            return resp

        # CLARIFY or unknown - try fallback GPT response first
        if fallback_gpt_response and not agent.clarify:
            resp = ChatResponse(reply=fallback_gpt_response, slots=state.slots)
            # Log assistant reply
            try:
                log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="gpt_fallback", slots=state.slots.model_dump())
            except Exception as e:
                print("⚠️ failed to log assistant message:", repr(e))
            return resp
        
        # Use agent clarification or default message
        resp = ChatResponse(reply=agent.clarify or "منظورت از محصول یا ویژگی دقیق‌تر چیه؟", slots=state.slots)
        # Log assistant reply
        try:
            log_message(db, req.conversation_id, role="assistant", text=resp.reply, intent="CLARIFY", slots=state.slots.model_dump())
        except Exception as e:
            print("⚠️ failed to log assistant message:", repr(e))
        return resp

    except Exception as e:
        logging.error(f"❌ Chat endpoint error: {e}")
        import traceback
        logging.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 
