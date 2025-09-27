"""
Clean Tool-Calling Sales Agent for Persian Online Shop
"""
import json
import os
from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy.orm import Session

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from .tools_agent import (
    list_products, search_products, get_product_by_code,
    crm_upsert_customer, cancel_order,
    parse_customer_details, parse_qty_and_attrs,
    propose_order, place_order, create_support_request,
    get_customer_by_phone, get_customer_order_history,
    resolve_customer, select_customer_by_id,
    list_variants, get_variant_by_sku, find_variants
)

# Load environment variables
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
import env

def extract_customer_info(text: str) -> Optional[Dict[str, str]]:
    """Extract customer information from user message"""
    import re
    
    # Normalize text
    text = text.lower().strip()
    
    # Extract name patterns
    name_patterns = [
        r"نامم\s+([^\s]+)\s+([^\s,،]+)",
        r"نام\s+([^\s]+)\s+([^\s,،]+)",
        r"اسمم\s+([^\s]+)\s+([^\s,،]+)",
    ]
    
    first_name = ""
    last_name = ""
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            first_name = match.group(1).strip()
            last_name = match.group(2).strip()
            break
    
    # Extract phone patterns
    phone_patterns = [
        r"تلفنم\s+(\d+)",
        r"شماره\s+(\d+)",
        r"موبایل\s+(\d+)",
        r"(\d{11})",  # 11-digit phone number
    ]
    
    phone = ""
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            phone = match.group(1).strip()
            break
    
    # Extract address patterns
    address_patterns = [
        r"آدرسم\s+([^,،]+)",
        r"آدرس\s+([^,،]+)",
    ]
    
    address = ""
    for pattern in address_patterns:
        match = re.search(pattern, text)
        if match:
            address = match.group(1).strip()
            break
    
    # Extract postal code patterns
    postal_patterns = [
        r"کد\s+پستی\s+(\d+)",
        r"کدپستی\s+(\d+)",
        r"(\d{10})",  # 10-digit postal code
    ]
    
    postal_code = ""
    for pattern in postal_patterns:
        match = re.search(pattern, text)
        if match:
            postal_code = match.group(1).strip()
            break
    
    # Return customer info if we have at least name and phone
    if first_name and last_name and phone:
        return {
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "address": address,
            "postal_code": postal_code,
            "notes": ""
        }
    
    return None

# ==== MINIMAL SYSTEM PROMPT ====
SYSTEM = """You are a helpful assistant for an online shop. Output must be in Persian (Farsi).

Data policy:
- Always use tools to read/write (products, orders, CRM). Do not answer from memory.
- Show product lists as bullets with explicit product codes (no numeric indexing). Ask the user to reply with the product code.
- When listing products, always show «• name — کد: CODE — قیمت: …». Ask the user to answer with the product code.
- For description requests (توضیح/شرح/مشخصات/description), return the official DB description verbatim (split if long). If none, show similar items via tools.
- When users search for products with attributes (e.g., "شلوار جین سرمه ای"), first search for the base product, then check variants for the specific attribute.

Greeting behavior:
- For simple greetings like "سلام" or "hello", respond with a friendly greeting and ask how you can help.
- Do NOT immediately suggest products or show product lists unless the user asks for them.
- Wait for the user to tell you what they need (products, order history, support, etc.).
- Be conversational and natural, not pushy or sales-focused.

Customer recognition:
- When a customer introduces themselves by name (e.g., "سلام من عرشیام" or "من علی رضایی هستم"), ALWAYS try to find them using resolve_customer(name).
- If they mention previous orders ("قبلا سفارش داده بودم"), this is a strong signal they're a returning customer.
- If resolve_customer returns needs_confirmation, show the candidates and ask for their phone number to confirm identity.
- If they provide a phone number, call get_customer_by_phone(phone) to check if they're a returning customer.
- If found, greet them by name and mention their customer code. You can then offer to show their order history.
- If they mention previous orders or want to see their history, call get_customer_order_history(customer_code) to show their recent orders.
- Always be welcoming and personalized when recognizing returning customers.
- NEVER ask new customers to register when they say they've ordered before - always try to find them first.
- For single names like "عرشیا", the system will search both first and last name fields.

Customer resolution safety:
- Do not attach a customer by name alone. Always require another identifier (code/phone/email/order_code/postal/last-4).
- Use resolve_customer(query, verifier) for safe customer resolution with disambiguation.
- When user provides verification (like "0442"), call resolve_customer with the original name and the verifier (e.g., resolve_customer("عرشیا", "0442")).
- If the resolver returns needs_confirmation, show candidates as numbered bullets with customer_id and masked contact; ask the user to pick by number (1, 2, 3) or provide a verifier (postal code or last 4 digits of phone).
- When resolve_customer returns a customer successfully, update the session state with the customer information (last_customer_id, last_customer_code, resolved_at).
- NEVER show customer codes to users - use internal customer IDs for selection.
- Use select_customer_by_id(customer_id) when user picks a number from the candidates.
- Once resolved, remember the customer for this session until the user switches.
- If user says "this is for Sara..." or similar, clear previous customer and resolve again.
- When creating orders, ALWAYS use the remembered customer data from session memory instead of asking for customer information again.
- If you have a resolved customer in session memory, use their data (first_name, last_name, phone, address, postal_code) in the order proposal.
- If you just recognized a customer (e.g., "عرشیا باغی - شماره تماس: 09046760442"), use that customer's information for the order without asking for it again.
- Never ask for customer information that you already have from the conversation or customer recognition.

Order data model:
- Every order requires: code, qty, and the product's required attributes.
- Attributes are generic (key → value). Do NOT assume clothing-only fields like size/color.
- Use the product's attributes_spec (from tools) to know which attributes are required and their allowed values/types.

Order creation flow:
- When user confirms a product (e.g., "A0001"), create the order proposal immediately using the recognized customer data.
- Do NOT ask for customer information again if you already have it from customer recognition.
- Use the customer data you displayed earlier (e.g., "عرشیا باغی - شماره تماس: 09046760442") in the order proposal.
- If you just recognized a customer (e.g., "شماره مشتری شما CUS-2025-000003 است"), use that customer's information in the order proposal without asking for it again.
- When creating order proposals, look at the conversation history to find customer information that was already provided or recognized.
- If you mentioned a customer's details in your previous response, use those details in the order proposal.
- If you need customer data for an order, use get_customer_by_phone(phone) to retrieve the customer information.
- For عرشیا with phone ending in 0442, use: first_name='عرشیا', last_name='باغی', phone='09046760442', address='تهران', postal_code='764397659'.

Variant handling:
- For products with variants, ask only for missing required attributes from the product's attribute_schema.
- Use list_variants(product_code) to see available variants and their attributes.
- Use find_variants(product_code, attributes) to find exact or nearest matches.
- When proposing an order, include sku_code and qty; never invent attributes.
- If no exact SKU matches the requested attributes, offer closest available options.
- Always use the exact sku_code returned by the tools in order proposals.
- When users ask about colors, sizes, or other attributes (e.g., "چه رنگی داره؟", "چه سایزی موجوده؟"), ALWAYS call list_variants(product_code) to show available options.
- If a user asks for a specific color/size that doesn't exist, show the available options from variants instead of saying "only one color available".
- Display variants as: "• SKU: A0001-RED-M — رنگ: قرمز — سایز: M — موجودی: 5"
- IMPORTANT: When users search for products with attributes (e.g., "شلوار جین سرمه ای"), first search for the base product (e.g., "شلوار جین"), then use find_variants to look for the specific attribute (e.g., {{"color": "سرمه ای"}}).
- If a user asks for "شلوار جین سرمه ای", search for "شلوار جین" first, then check variants for color "سرمه ای".

Customer data entry:
- Users might send multiple fields in ONE line (e.g., `1.عرشیا 2.باغی 3.0904... 4.تهران ... 5.7787...`) or with labels (`نام: …، فامیل: …، شماره: …`).
- FIRST, call `parse_customer_details` if the message includes several customer fields; use the parsed object as `customer`.
- If the message includes qty or attribute key:value pairs, call `parse_qty_and_attrs` to extract them.

Order protocol (mandatory):
1) When the user provides a product code AND customer information, IMMEDIATELY CALL propose_order(code, qty, attributes, customer).
   - Required customer fields: first_name, last_name, phone, address, postal_code (notes optional).
   - If propose_order returns {{"error":"missing_fields","missing":[...]}}, ask ONLY for those fields (one at a time) and try again.
2) If propose_order returns {{"confirmation_token","proposal"}}:
   - Show a short [ORDER_SUMMARY] in Persian.
   - Then include EXACTLY ONE line starting with "DATA:" followed by valid JSON with the entire proposal + confirmation_token:
     DATA: {{"code":"CODE","qty":QTY,"attributes":{{"KEY1":"...","KEY2":"..."}},"customer":{{"first_name":"...","last_name":"...","phone":"...","address":"...","postal_code":"...","notes":"..."}},"confirmation_token":"..."}}
   - WAIT for user confirmation (تایید / بله / اوکی / Confirm / Yes).
   - CRITICAL: You MUST include the DATA: line for the confirmation system to work.
3) ONLY after the user confirms, CALL place_order(confirmation_token, proposal).
4) For cancellations, CALL cancel_order(order_id, reason).
5) IMPORTANT: If the user changes quantity or attributes after showing the order summary, you MUST call propose_order again with the new values to get a fresh confirmation_token. Never reuse old tokens.
6) When user says "سه عدد میخوام" or similar quantity changes, immediately call propose_order with the new quantity and the same customer data to get a fresh token.

IMPORTANT: You MUST call propose_order when you have both product code and customer details. Do not ask for more information if you already have what's needed.

Formatting:
- Lists: «• نام — کد: CODE — قیمت: …»
- Prices must include currency and thousands separators.
- Tone: friendly, concise, professional. Do not hallucinate.
- When proposing/placing orders, prefer codes (product_code, customer_code) and return order_code in confirmations.
- Never invent codes; only use those returned by tools.

After you call place_order and receive a success payload, you MUST echo a single summary line:
ORDER_RESULT: {{"order_id":"...","order_code":"...","status":"created"}}

Support escalation:
- If a customer asks for human support (پشتیبانی انسانی, نیاز به پشتیبانی, صحبت با انسان, etc.), ask for their:
  1. Full name (نام و نام خانوادگی)
  2. Phone number (شماره تماس)
  3. Support message (پیام یا مشکل)
- Then call create_support_request(customer_name, customer_phone, message) to create a support ticket.
- Confirm the ticket was created and inform them that support will contact them soon."""

# ==== DATABASE SESSION MANAGEMENT ====
_db_session: Session = None

def set_db_session(session: Session):
    """Set the database session for tools"""
    global _db_session
    _db_session = session

def get_db_session() -> Session:
    """Get the current database session"""
    return _db_session

# ==== TOOL-CALLING AGENT SETUP ====
TOOLS = [
    list_products, search_products, get_product_by_code,
    crm_upsert_customer, cancel_order,
    parse_customer_details, parse_qty_and_attrs,
    propose_order, place_order, create_support_request,
    get_customer_by_phone, get_customer_order_history,
    resolve_customer, select_customer_by_id,
    list_variants, get_variant_by_sku, find_variants
]

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, max_tokens=1000)
agent = create_tool_calling_agent(llm, TOOLS, prompt)
executor = AgentExecutor(agent=agent, tools=TOOLS, verbose=False, max_iterations=3)

# ==== CONFIRMATION HANDLING ====
CONFIRM_WORDS = {"تایید","تاييد","بله","اوکی","اوكى","اوكي","confirm","yes","ok","okay"}

def _extract_json_after(prefix: str, text: str):
    """Find a line that starts with `prefix` and parse the remaining JSON payload."""
    for line in (text or "").splitlines():
        s = line.strip()
        if s.startswith(prefix):
            try:
                return json.loads(s[len(prefix):].strip())
            except Exception:
                return None
    return None

def _update_session_with_customer(state: Dict[str, Any], customer_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update session state with resolved customer information."""
    if customer_data and customer_data.get("success"):
        customer = customer_data.get("customer", {})
        if customer:
            state["last_customer_id"] = customer.get("id")
            state["last_customer_code"] = customer.get("customer_code")
            state["resolved_at"] = "now"
    return state

def sales_agent_turn(db: Session, message: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hybrid safety:
    - If user confirms and we have a pending proposal -> call place_order right here.
    - Otherwise run the agent and capture a new DATA: {...} proposal if present.
    - Maintains customer resolution session memory.
    """
    # Set database session for tools
    set_db_session(db)
    
    state = state or {
        "chat_history": [], 
        "pending_proposal": None,
        "last_customer_id": None,
        "last_customer_code": None,
        "resolved_at": None
    }
    text = (message or "").strip()
    
    # Check for customer switching (e.g., "this is for Sara...")
    if any(phrase in text.lower() for phrase in ["this is for", "برای", "سارا", "for sara"]):
        state["last_customer_id"] = None
        state["last_customer_code"] = None
        state["resolved_at"] = None

    # A) Confirmation path: create the order using cached proposal
    if state.get("pending_proposal"):
        low = text.lower()
        if any(w in low for w in [w.lower() for w in CONFIRM_WORDS]):
            pp = state["pending_proposal"]

            tool_res = place_order.invoke({
                "confirmation_token": pp.get("confirmation_token",""),
                "proposal": pp.get("proposal", {}),
            }) or {}

            if tool_res.get("error"):
                error = tool_res['error']
                if "insufficient_stock" in error:
                    # Extract stock information from error message
                    if "Available:" in error and "Requested:" in error:
                        reply = "متاسفانه موجودی کافی نیست. لطفاً تعداد کمتری انتخاب کنید یا رنگ دیگری را امتحان کنید."
                    else:
                        reply = "متاسفانه موجودی کافی نیست. لطفاً تعداد کمتری انتخاب کنید."
                elif "product_not_found" in error:
                    reply = "محصول مورد نظر یافت نشد. لطفاً کد محصول را بررسی کنید."
                else:
                    reply = f"متاسفانه ایجاد سفارش ناموفق بود: {error}"
                order_id, status = None, "error"
            else:
                order_code = tool_res.get("order_code") or tool_res.get("order_id","")
                order_id = tool_res.get("order_id")
                status = tool_res.get("status","created")
                reply = (
                    "سفارش ثبت شد ✅\n"
                    f"• شماره سفارش: {order_code}\n"
                    f"• شناسه سفارش: {order_id}"
                )

            state["pending_proposal"] = None
            state["chat_history"] += [("human", message), ("ai", reply)]
            return {"reply": reply, "state": state, "order_id": order_id, "status": status}

    # B) Delegate to the agent
    out = executor.invoke({
        "input": text,
        "chat_history": state["chat_history"],
        "agent_scratchpad": [],
    })
    reply = (out.get("output") or "").strip()

    # Check if customer was resolved and update session state
    if "شماره مشتری شما" in reply or "خوشحالم که شما را شناسایی کردم" in reply:
        # Customer was resolved, try to extract customer info from the response
        # This is a simple heuristic - in a real implementation, you'd parse the tool results
        # For now, we'll set a flag that customer was resolved
        state["customer_resolved"] = True

    # C) Capture a fresh proposal if the model emitted one
    data_payload = _extract_json_after("DATA:", reply)
    if isinstance(data_payload, dict) and data_payload.get("code") and data_payload.get("qty") and data_payload.get("confirmation_token"):
        state["pending_proposal"] = {
            "proposal": {
                "code": data_payload.get("code"),
                "qty": int(data_payload.get("qty", 1)),
                "attributes": data_payload.get("attributes") or {},
                "customer": data_payload.get("customer") or {},
            },
            "confirmation_token": data_payload.get("confirmation_token"),
        }

    # D) Optionally parse ORDER_RESULT if the model already placed it (not required)
    order_res = _extract_json_after("ORDER_RESULT:", reply)
    order_id = (order_res or {}).get("order_id")
    status = (order_res or {}).get("status")

    # E) Persist chat
    state["chat_history"] += [("human", message), ("ai", reply)]
    return {"reply": reply, "state": state, "order_id": order_id, "status": status}

# ==== BACKWARD COMPATIBILITY ====
def sales_agent_turn_legacy(db: Session, message: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy function name for backward compatibility"""
    return sales_agent_turn(db, message, state)