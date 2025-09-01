from openai import OpenAI
from config import OPENAI_API_KEY
from typing import Optional
import logging

# Configure OpenAI client
client = None
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)

def ask_gpt(message: str) -> str:
    """
    Ask GPT a question and return the response.
    Uses OpenAI's ChatCompletion API with Persian-friendly system prompt.
    """
    if not OPENAI_API_KEY or not client:
        logging.error("❌ No OpenAI API key or client available")
        return "متاسفم، الان نمی‌تونم پاسخ بدم. لطفاً دوباره تلاش کنید."
    
    # Determine model - use gpt-4 if available, else gpt-3.5-turbo
    try:
        # Try to use gpt-4 first
        model = "gpt-4"
        logging.info(f"🤖 Attempting GPT call with model: {model}")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant for an online shop. Answer in Persian."},
                {"role": "user", "content": message}
            ],
            max_tokens=500,
            temperature=0.7,
            timeout=30  # Add timeout
        )
        
        result = response.choices[0].message.content.strip()
        logging.info(f"✅ GPT response received: {result[:50]}...")
        return result
        
    except Exception as e:
        logging.error(f"❌ GPT-4 failed: {type(e).__name__}: {str(e)}")
        # If gpt-4 fails, try gpt-3.5-turbo
        try:
            model = "gpt-3.5-turbo"
            logging.info(f"🤖 Retrying with model: {model}")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for an online shop. Answer in Persian."},
                    {"role": "user", "content": message}
            ],
                max_tokens=500,
                temperature=0.7,
                timeout=30  # Add timeout
            )
            
            result = response.choices[0].message.content.strip()
            logging.info(f"✅ GPT-3.5 response received: {result[:50]}...")
            return result
            
        except Exception as e2:
            logging.error(f"❌ GPT-3.5 also failed: {type(e2).__name__}: {str(e2)}")
            # Return a more specific error message
            if "timeout" in str(e2).lower() or "connection" in str(e2).lower():
                return "متاسفم، مشکل اتصال به سرور. لطفاً دوباره تلاش کنید."
            elif "quota" in str(e2).lower() or "billing" in str(e2).lower():
                return "متاسفم، مشکل در سرویس. لطفاً دوباره تلاش کنید."
            else:
                return f"متاسفم، خطا در سرویس: {type(e2).__name__}"

def call_llm_for_action(message: str) -> dict:
    """
    Call LLM to determine action and extract slots.
    Returns a dict with 'action' and 'slots' keys.
    """
    if not OPENAI_API_KEY or not client:
        logging.error("❌ No OpenAI API key or client available")
        return {"action": "ERROR", "slots": {"error": "No API key"}}
    
    try:
        # Use gpt-4o-mini for action extraction
        model = "gpt-4o-mini"
        logging.info(f"🤖 Calling LLM with model: {model}")
        
        system_prompt = """You are a shopping assistant. Analyze the user's message and return a JSON response with:
- action: one of [SEARCH_PRODUCTS, CREATE_ORDER, CONFIRM_ORDER, SMALL_TALK, CLARIFY]
- slots: relevant information like product name, code, category, etc.

CRITICAL RULES:
1. SEARCH_PRODUCTS: Use when user asks about products, wants to find products, or references product codes
2. CREATE_ORDER: Use when user wants to place an order or buy something
3. CONFIRM_ORDER: Use when user confirms/approves an order (after seeing order summary)
4. SMALL_TALK: Use only for greetings like "سلام", "hello"
5. CLARIFY: Use when you cannot understand the user's intent

SEARCH_PRODUCTS Examples:
- "جوراب دارین؟" → {"action": "SEARCH_PRODUCTS", "slots": {"q": "جوراب"}}
- "شلوار دارین؟" → {"action": "SEARCH_PRODUCTS", "slots": {"q": "شلوار"}}
- "search for products" → {"action": "SEARCH_PRODUCTS", "slots": {"q": ""}}
- "کد A0001 قیمتش؟" → {"action": "SEARCH_PRODUCTS", "slots": {"code": "A0001"}}
- "A0001 رو میخوام" → {"action": "SEARCH_PRODUCTS", "slots": {"code": "A0001"}}
- "شماره 1" → {"action": "SEARCH_PRODUCTS", "slots": {"code": "A0001"}}
- "1" → {"action": "SEARCH_PRODUCTS", "slots": {"code": "A0001"}}

CREATE_ORDER Examples:
- "میخواهم ثبت سفارش کنم" → {"action": "CREATE_ORDER", "slots": {}}
- "ثبت سفارش برای محصول A0001" → {"action": "CREATE_ORDER", "slots": {"product_code": "A0001"}}
- "سفارش A0001" → {"action": "CREATE_ORDER", "slots": {"product_code": "A0001"}}
- "همینو میخوام" → {"action": "CREATE_ORDER", "slots": {}}
- "میخوام" → {"action": "CREATE_ORDER", "slots": {}}
- "میخوامش" → {"action": "CREATE_ORDER", "slots": {}}
- "بخر" → {"action": "CREATE_ORDER", "slots": {}}
- "سفارش بده" → {"action": "CREATE_ORDER", "slots": {}}

CONFIRM_ORDER Examples:
- "تایید میکنم" → {"action": "CONFIRM_ORDER", "slots": {}}
- "بله" → {"action": "CONFIRM_ORDER", "slots": {}}
- "تایید" → {"action": "CONFIRM_ORDER", "slots": {}}
- "yes" → {"action": "CONFIRM_ORDER", "slots": {}}
- "ok" → {"action": "CONFIRM_ORDER", "slots": {}}
- "درست" → {"action": "CONFIRM_ORDER", "slots": {}}
- "باشه" → {"action": "CONFIRM_ORDER", "slots": {}}

SMALL_TALK Examples:
- "سلام" → {"action": "SMALL_TALK", "slots": {}}
- "hello" → {"action": "SMALL_TALK", "slots": {}}

IMPORTANT RULES FOR PERSIAN TEXT:
1. If the message ends with "دارین؟" (do you have?), ALWAYS use SEARCH_PRODUCTS action
2. If the message contains product names like "جوراب", "شلوار", "پیراهن", use SEARCH_PRODUCTS action
3. If the message is just "سلام" or "hello", use SMALL_TALK action
4. If the message is a confirmation like "تایید میکنم", "بله", use CONFIRM_ORDER action
5. Everything else should be analyzed for intent

CRITICAL: The message "شلوار دارین؟" MUST return {"action": "SEARCH_PRODUCTS", "slots": {"q": "شلوار"}}
CRITICAL: The message "تایید میکنم" MUST return {"action": "CONFIRM_ORDER", "slots": {}}

Return ONLY valid JSON, no other text."""
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=200,
            temperature=0.1,
            timeout=30
        )
        
        result = response.choices[0].message.content.strip()
        logging.info(f"✅ LLM response received: {result}")
        
        # Try to parse JSON
        import json
        try:
            parsed = json.loads(result)
            if isinstance(parsed, dict) and "action" in parsed:
                return parsed
            else:
                logging.warning(f"⚠️ LLM response missing action: {result}")
                return {"action": "CLARIFY", "slots": {"error": "Invalid response format"}}
        except json.JSONDecodeError as e:
            logging.error(f"❌ Failed to parse LLM JSON: {e}, response: {result}")
            return {"action": "CLARIFY", "slots": {"error": "JSON parse failed"}}
            
    except Exception as e:
        logging.exception(f"❌ LLM call failed: {e}")
        return {"action": "ERROR", "slots": {"error": str(e)}}

def call_gpt_for_intent(message: str) -> str:
    """
    Call GPT for intent classification (legacy function for compatibility).
    """
    return ask_gpt(message)
