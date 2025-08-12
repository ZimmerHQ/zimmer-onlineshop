import json
import os
from typing import List, Dict, Any
from pydantic import BaseModel
from env import allow_mock
from .state import AgentResponse, Slots, ConversationState

# Uses OpenAI SDK v1; adjust if you have a wrapper already.
# pip install openai>=1.0.0

SYSTEM_PROMPT = """You are a retail sales assistant for a Persian shop. Always reply in Persian. Return ONLY a JSON object with fields: action, slots, clarify.

Actions: SEARCH_PRODUCTS | SELECT_PRODUCT | COLLECT_VARIANTS | CONFIRM_ORDER | CREATE_ORDER | CLARIFY | SMALL_TALK

Slots schema: { "product_id": number|null, "size": string|null, "color": string|null, "qty": number|null }

Rules:
- If user asks generally (e.g., "شلوار دارین؟"), use action=SEARCH_PRODUCTS.
- If user sends a number like "1", likely a selection; use action=SELECT_PRODUCT and set product_id to null (server fills it).
- Extract size/color from free text like "۴۳ مشکی" or "سایز 43 رنگ مشکی".
- Default qty=1.
- Move to CREATE_ORDER only when all slots are ready.
- If something is missing, use action=COLLECT_VARIANTS and put a short question in "clarify".
- If confused, use action=CLARIFY with a short question.
- Never ask for confirmation until a product is selected (slots.product_id must not be null).
Return JSON only. """

FEW_SHOTS = [
    {"role":"user","content":"شلوار دارین؟"},
    {"role":"assistant","content":json.dumps({"action":"SEARCH_PRODUCTS","slots":{"product_id":None,"size":None,"color":None,"qty":1},"clarify":None}, ensure_ascii=False)},
    {"role":"user","content":"1"},
    {"role":"assistant","content":json.dumps({"action":"SELECT_PRODUCT","slots":{"product_id":None,"size":None,"color":None,"qty":1},"clarify":None}, ensure_ascii=False)},
    {"role":"user","content":"43 مشکی"},
    {"role":"assistant","content":json.dumps({"action":"COLLECT_VARIANTS","slots":{"product_id":None,"size":"43","color":"مشکی","qty":1},"clarify":None}, ensure_ascii=False)},
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
        # No key: mock in dev, or raise to surface a clean error
        if allow_mock():
            # Simple deterministic mock that nudges the flow
            # If user sent a number, select product; else search; extract basic size/color patterns
            action = "SEARCH_PRODUCTS"
            slots = {"product_id": None, "size": None, "color": None, "qty": 1}
            if user_text.strip().isdigit():
                action = "SELECT_PRODUCT"
            if "مشکی" in user_text: 
                slots["color"] = "مشکی"
            for token in user_text.split():
                if token.isdigit():
                    slots["size"] = token
                    break
            return AgentResponse(action=action, slots=Slots(**slots), clarify=None)
        raise RuntimeError("OPENAI_API_KEY is missing")

    # Real call
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    messages = [{"role":"system","content":SYSTEM_PROMPT}] + FEW_SHOTS + [{"role":"user","content":user_text}]
    # Convert to proper OpenAI message format
    openai_messages = []
    for msg in messages:
        if msg["role"] == "system":
            openai_messages.append({"role": "system", "content": msg["content"]})
        elif msg["role"] == "user":
            openai_messages.append({"role": "user", "content": msg["content"]})
        elif msg["role"] == "assistant":
            openai_messages.append({"role": "assistant", "content": msg["content"]})
    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL","gpt-4o-mini"),
        messages=openai_messages,
        temperature=0.2,
        max_tokens=200
    )
    content = resp.choices[0].message.content or ""
    try:
        data = _parse_strict_json(content)
    except Exception:
        data = {"action":"CLARIFY","slots":{"product_id":None,"size":None,"color":None,"qty":1},"clarify":"منظورت از محصول یا ویژگی دقیق‌تر چیه؟"}
    slots = Slots(**{
        "product_id": data.get("slots",{}).get("product_id"),
        "size": data.get("slots",{}).get("size"),
        "color": data.get("slots",{}).get("color"),
        "qty": data.get("slots",{}).get("qty",1) or 1,
    })
    return AgentResponse(action=data.get("action","CLARIFY"), slots=slots, clarify=data.get("clarify")) 