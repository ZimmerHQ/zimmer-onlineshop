import json
import os
import logging
from typing import List, Dict, Any
from pydantic import BaseModel
from env import allow_mock
from .state import AgentResponse, Slots, ConversationState

SYSTEM_PROMPT = """تو یک فروشنده حرفه‌ای و دوستانه در یک فروشگاه پوشاک ایرانی هستی. باید مثل یک فروشنده واقعی رفتار کنی:

شخصیت تو:
- گرم و دوستانه، مثل فروشنده‌های قدیمی بازار
- حرفه‌ای و آگاه از محصولات
- صبور و راهنما
- همیشه به فارسی پاسخ می‌دهی
- از کلمات محترمانه استفاده می‌کنی (شما، لطفاً، ممنون)

رفتار فروشنده:
- وقتی مشتری سلام می‌کند: گرم و دوستانه پاسخ بده
- وقتی محصول می‌خواهد: لیست محصولات را نشان بده با کد محصول
- وقتی انتخاب می‌کند: جزئیات را بپرس (سایز، رنگ)
- وقتی تایید می‌کند: سفارش را ثبت کن
- همیشه پیشنهاد کمک بیشتر بده

مهم: همیشه کد محصولات را در لیست نشان بده و از مشتری بخواه با کد پاسخ دهد.

فقط JSON برگردان با این فیلدها:
- action: SEARCH_PRODUCTS | SELECT_PRODUCT | COLLECT_VARIANTS | CONFIRM_ORDER | CREATE_ORDER | CLARIFY | SMALL_TALK
- slots: { "product_code": null, "size": null, "color": null, "qty": 1 }
- clarify: پیام کوتاه برای مشتری (اختیاری)

قوانین:
- "شلوار دارین؟" = SEARCH_PRODUCTS
- کد محصول (مثل A0001) = SELECT_PRODUCT  
- "43 مشکی" = COLLECT_VARIANTS
- "بله" = CONFIRM_ORDER
- سلام = SMALL_TALK"""

FEW_SHOTS = [
    {"role":"user","content":"سلام"},
    {"role":"assistant","content":json.dumps({"action":"SMALL_TALK","slots":{"product_code":None,"size":None,"color":None,"qty":1},"clarify":"سلام! به فروشگاه ما خوش آمدید 🌟 چطور می‌تونم کمکتون کنم؟"}, ensure_ascii=False)},
    {"role":"user","content":"شلوار دارین؟"},
    {"role":"assistant","content":json.dumps({"action":"SEARCH_PRODUCTS","slots":{"product_code":None,"size":None,"color":None,"qty":1},"clarify":None}, ensure_ascii=False)},
    {"role":"user","content":"A0001"},
    {"role":"assistant","content":json.dumps({"action":"SELECT_PRODUCT","slots":{"product_code":"A0001","size":None,"color":None,"qty":1},"clarify":None}, ensure_ascii=False)},
    {"role":"user","content":"43 مشکی"},
    {"role":"assistant","content":json.dumps({"action":"COLLECT_VARIANTS","slots":{"product_code":"A0001","size":"43","color":"مشکی","qty":1},"clarify":None}, ensure_ascii=False)},
    {"role":"user","content":"بله"},
    {"role":"assistant","content":json.dumps({"action":"CONFIRM_ORDER","slots":{"product_code":"A0001","size":"43","color":"مشکی","qty":1},"clarify":None}, ensure_ascii=False)},
]

def _parse_strict_json(txt: str) -> Dict[str, Any]:
    # find first JSON object in the text; tolerate code fences
    start = txt.find("{")
    end = txt.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found")
    raw = txt[start:end+1]
    return json.loads(raw)

def call_llm(history: List[Dict[str,str]], state: ConversationState, user_text: str) -> AgentResponse:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.error("❌ No OpenAI API key available")
        if allow_mock():
            logging.info("🔄 Using mock response due to missing API key")
            # Smart mock that acts like a real salesman
            action = "SMALL_TALK"
            slots = {"product_code": None, "size": None, "color": None, "qty": 1}
            
            user_lower = user_text.lower().strip()
            
            # Greeting
            if any(word in user_lower for word in ["سلام", "درود", "هی"]):
                action = "SMALL_TALK"
            # Product inquiry
            elif any(word in user_lower for word in ["شلوار", "پیراهن", "کت", "کفش", "دارین", "دارید"]):
                action = "SEARCH_PRODUCTS"
            # Number selection
            elif user_lower.isdigit():
                action = "SELECT_PRODUCT"
            # Size/color specification
            elif any(word in user_lower for word in ["مشکی", "سفید", "آبی", "قرمز"]) or any(char.isdigit() for char in user_lower):
                action = "COLLECT_VARIANTS"
                # Extract size and color
                if "مشکی" in user_lower: slots["color"] = "مشکی"
                if "سفید" in user_lower: slots["color"] = "سفید"
                if "آبی" in user_lower: slots["color"] = "آبی"
                if "قرمز" in user_lower: slots["color"] = "قرمز"
                for token in user_lower.split():
                    if token.isdigit():
                        slots["size"] = token
                        break
            # Confirmation
            elif any(word in user_lower for word in ["بله", "باشه", "تایید", "ok"]):
                action = "CONFIRM_ORDER"
            
            return AgentResponse(action=action, slots=Slots(**slots), clarify=None)
        raise RuntimeError("OPENAI_API_KEY is missing")

    # Real call
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        messages = [{"role":"system","content":SYSTEM_PROMPT}] + FEW_SHOTS + [{"role":"user","content":user_text}]
        
        openai_messages = []
        for msg in messages:
            if msg["role"] == "system":
                openai_messages.append({"role": "system", "content": msg["content"]})
            elif msg["role"] == "user":
                openai_messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "assistant":
                openai_messages.append({"role": "assistant", "content": msg["content"]})
        
        model = os.getenv("OPENAI_MODEL","gpt-4o-mini")
        logging.info(f"🤖 Calling LLM with model: {model}")
        
        resp = client.chat.completions.create(
            model=model,
            messages=openai_messages,
            temperature=0.3,  # Slightly more creative for natural responses
            max_tokens=300,
            timeout=30
        )
        content = resp.choices[0].message.content or ""
        logging.info(f"✅ LLM response received: {content[:50]}...")
        
        try:
            data = _parse_strict_json(content)
        except Exception as parse_error:
            logging.error(f"❌ Failed to parse LLM response: {parse_error}")
            # Fallback to smart mock
            return call_llm([], state, user_text)  # Recursive call to mock
        
        slots = Slots(**{
            "product_code": data.get("slots",{}).get("product_code"),
            "size": data.get("slots",{}).get("size"),
            "color": data.get("slots",{}).get("color"),
            "qty": data.get("slots",{}).get("qty",1) or 1,
        })
        return AgentResponse(action=data.get("action","CLARIFY"), slots=slots, clarify=data.get("clarify"))
        
    except Exception as e:
        logging.error(f"❌ LLM call failed: {type(e).__name__}: {str(e)}")
        # Return a fallback response instead of raising
        if "timeout" in str(e).lower() or "connection" in str(e).lower():
            logging.error("❌ Connection/timeout error in LLM call")
            return AgentResponse(action="CLARIFY", slots=Slots(product_code=None, size=None, color=None, qty=1), clarify="متاسفم، مشکل اتصال. لطفاً دوباره تلاش کنید.")
        else:
            logging.error(f"❌ Unexpected error in LLM call: {e}")
            return AgentResponse(action="CLARIFY", slots=Slots(product_code=None, size=None, color=None, qty=1), clarify="متاسفم، خطا در پردازش. لطفاً دوباره تلاش کنید.") 