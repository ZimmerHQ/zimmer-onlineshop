from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

# Conversation state is in-memory for MVP; you can replace with Redis/DB later.
# Store one "last_list" to resolve numeric selections.

class Slots(BaseModel):
    product_code: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    qty: Optional[int] = 1

class ListItem(BaseModel):
    idx: int
    product_id: int
    product_code: str
    name: str
    price: Optional[float] = None
    sizes: Optional[List[str]] = None
    colors: Optional[List[str]] = None

class ConversationState(BaseModel):
    slots: Slots = Field(default_factory=Slots)
    last_list: List[ListItem] = Field(default_factory=list)
    last_query: Optional[str] = None

class AgentResponse(BaseModel):
    action: str
    slots: Slots
    clarify: Optional[str] = None

def merge_slots(base: Slots, delta: Slots) -> Slots:
    out = base.model_copy()
    for k, v in delta.model_dump().items():
        if v not in (None, "", []):
            setattr(out, k, v)
    return out

def find_by_code(state: ConversationState, maybe_code: str) -> Optional[str]:
    # map product code to product_code using last_list or direct match
    for item in state.last_list:
        if item.product_code == maybe_code:
            return item.product_code
    return maybe_code if maybe_code else None

def missing_fields(slots: Slots) -> List[str]:
    need = []
    if not slots.product_code:
        need.append("product")
    if not slots.size:
        need.append("size")
    if not slots.color:
        need.append("color")
    if not slots.qty:
        need.append("qty")
    return need

def _normalize_digits(text: str) -> str:
    # Persian/Arabic to Latin digits
    mapping = {
        "۰":"0","۱":"1","۲":"2","۳":"3","۴":"4","۵":"5","۶":"6","۷":"7","۸":"8","۹":"9",
        "٠":"0","١":"1","٢":"2","٣":"3","٤":"4","٥":"5","٦":"6","٧":"7","٨":"8","٩":"9"
    }
    return "".join(mapping.get(ch, ch) for ch in text or "") 