"""
Conversation handlers for different message types
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from .tools import tool_search_products, tool_get_product_by_code, tool_create_order, tool_rag_search, tool_featured_products
from .slots import SlotFrame
from .utils import format_products, format_price, random_no_match, is_greeting, is_cancellation, extract_product_code, is_confirmation
from .prompts import SLOT_EXTRACTION_PROMPT

def handle_greeting(db: Session, state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle greeting messages"""
    from .prompts import GREETING_TEMPLATE
    
    feats = tool_featured_products(db, limit=3)
    state["last_suggestion_type"] = "featured"
    state["last_suggestions"] = feats  # Store for selection
    
    return {
        "reply": GREETING_TEMPLATE.format(featured_products=format_products(feats, with_examples=True)),
        "state": state
    }

def handle_cancellation(state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle cancellation messages"""
    state["cart"] = {}
    return {
        "reply": "باشه، سفارش لغو شد. چطور می‌تونم کمکتون کنم؟",
        "state": state
    }

def handle_product_code(db: Session, code: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle product code lookup"""
    from .prompts import PRODUCT_DETAILS_TEMPLATE
    
    try:
        product = tool_get_product_by_code(db, code)
    except Exception:
        product = None
    
    if not product:
        return None
    
    if product["stock"] <= 0:
        # Suggest alternatives
        alternatives = tool_search_products(db, q=None, category_id=product.get("category_id"), limit=3)
        alt_text = ""
        if alternatives:
            alt_lines = [f"{i+1}) {alt['name']} (کد {alt['code']}) — {format_price(alt['price'])}" for i, alt in enumerate(alternatives)]
            alt_text = f"\n\nپیشنهادات مشابه:\n" + "\n".join(alt_lines)
        return {"reply": f"متأسفانه {product['name']} موجود نیست 😔{alt_text}", "state": state}
    
    # Product found and in stock
    state["cart"]["product"] = product
    reply = PRODUCT_DETAILS_TEMPLATE.format(
        name=product['name'],
        code=product['code'],
        price=format_price(product['price'])
    )
    state["last_suggestion_type"] = None
    return {"reply": reply, "state": state}

def handle_search(db: Session, search_terms: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle product search"""
    from .prompts import SEARCH_RESULTS_TEMPLATE, RAG_RESULTS_TEMPLATE
    
    # Try RAG search first
    try:
        rag_matches = tool_rag_search(search_terms, k=3) or []
    except Exception:
        rag_matches = []

    if rag_matches:
        state["last_suggestion_type"] = "rag"
        state["last_suggestions"] = rag_matches  # Store for selection
        return {
            "reply": RAG_RESULTS_TEMPLATE.format(products=format_products(rag_matches, with_examples=False)),
            "state": state
        }

    # Try fuzzy product search
    try:
        search_matches = tool_search_products(db, q=search_terms, limit=3) or []
    except Exception:
        search_matches = []

    if search_matches:
        state["last_suggestion_type"] = "search"
        state["last_suggestions"] = search_matches  # Store for selection
        return {
            "reply": SEARCH_RESULTS_TEMPLATE.format(products=format_products(search_matches, with_examples=False)),
            "state": state
        }

    # No matches found
    return None

def handle_no_match(db: Session, state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle when no products are found"""
    feats = tool_featured_products(db, limit=3)
    text_intro = random_no_match()
    
    if state.get("last_suggestion_type") == "featured":
        text_intro = "فعلاً چنین موردی در موجودی نداریم؛ این‌ها پرفروش‌ها هستن:"
    
    state["last_suggestion_type"] = "featured"
    state["last_suggestions"] = feats  # Store for selection
    return {
        "reply": f"{text_intro}\n" + format_products(feats, with_examples=True),
        "state": state
    }

def handle_product_selection(message: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle when user selects a product by number (1, 2, 3, etc.)"""
    import re
    
    # Check for number selection patterns
    number_match = re.search(r'^(\d+)$', message.strip())
    if not number_match:
        # Check for Persian number patterns
        persian_numbers = {'۱': '1', '۲': '2', '۳': '3', '۴': '4', '۵': '5'}
        for persian, arabic in persian_numbers.items():
            if message.strip() == persian:
                number_match = re.search(r'^(\d+)$', arabic)
                break
    
    if not number_match:
        return None
    
    selection_num = int(number_match.group(1))
    last_suggestions = state.get("last_suggestions", [])
    
    if not last_suggestions or selection_num < 1 or selection_num > len(last_suggestions):
        return None
    
    # Get the selected product
    selected_product = last_suggestions[selection_num - 1]
    
    # Set as current product
    state["cart"]["product"] = selected_product
    state["last_suggestion_type"] = None
    
    from .prompts import PRODUCT_DETAILS_TEMPLATE
    reply = PRODUCT_DETAILS_TEMPLATE.format(
        name=selected_product['name'],
        code=selected_product['code'],
        price=format_price(selected_product['price'])
    )
    
    return {"reply": reply, "state": state}

def handle_same_product_request(message: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle when user wants the same product (همین رو میخوام)"""
    same_product_phrases = [
        "همین رو میخوام", "همینو میخوام", "همین", "همینو", 
        "همین محصول", "همین کالا", "همینو میخوایم"
    ]
    
    message_lower = message.strip().lower()
    if not any(phrase in message_lower for phrase in same_product_phrases):
        return None
    
    # Check if there's a current product in cart
    current_product = state.get("cart", {}).get("product")
    if not current_product:
        return None
    
    # User wants the current product
    from .prompts import PRODUCT_DETAILS_TEMPLATE
    reply = PRODUCT_DETAILS_TEMPLATE.format(
        name=current_product['name'],
        code=current_product['code'],
        price=format_price(current_product['price'])
    )
    
    return {"reply": reply, "state": state}

def extract_slots_llm(message: str) -> SlotFrame:
    """Extract slots using LLM"""
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        parser = JsonOutputParser(pydantic_object=SlotFrame)
        prompt = ChatPromptTemplate.from_messages([
            ("system", SLOT_EXTRACTION_PROMPT),
            ("human", "پیام: {message}\nخروجی با کلیدهای product_code, quantity, size, color, confirm")
        ])
        chain = prompt | llm | parser
        return chain.invoke({"message": message})
    except Exception:
        return extract_slots_fallback(message)

def extract_slots_fallback(message: str) -> SlotFrame:
    """Fallback slot extraction using regex patterns"""
    import re
    from .utils import YES_RE
    
    # Extract product code
    code_match = re.search(r'[A-Za-z]{1,4}\d{3,6}', message)
    product_code = code_match.group(0) if code_match else None
    
    # Extract quantity
    qty_match = re.search(r'(\d+)\s*(عدد|تا|تایی)?', message)
    quantity = int(qty_match.group(1)) if qty_match else None
    
    # Extract size
    size_patterns = {
        'S': r'\b(کوچک|S|سایز کوچک)\b',
        'M': r'\b(مدیوم|M|سایز مدیوم)\b', 
        'L': r'\b(بزرگ|L|سایز بزرگ)\b',
        'XL': r'\b(XL|سایز XL)\b'
    }
    size = None
    for size_code, pattern in size_patterns.items():
        if re.search(pattern, message, re.I):
            size = size_code
            break
    
    # Extract color
    color_patterns = {
        'مشکی': r'\b(مشکی|سیاه|black)\b',
        'سفید': r'\b(سفید|white)\b',
        'قرمز': r'\b(قرمز|red)\b',
        'آبی': r'\b(آبی|blue)\b'
    }
    color = None
    for color_name, pattern in color_patterns.items():
        if re.search(pattern, message, re.I):
            color = color_name
            break
    
    # Extract confirmation
    confirm = bool(YES_RE.search(message or ""))
    
    return SlotFrame(
        product_code=product_code,
        quantity=quantity,
        size=size,
        color=color,
        confirm=confirm
    )
