from pydantic import BaseModel
from typing import Optional, Dict, Any

class ChatIn(BaseModel):
    conversation_id: str
    message: str

class ChatOut(BaseModel):
    reply: str
    slots: Dict[str, Any] = {}
    order_id: Optional[int] = None
    status: Optional[str] = None
    debug: Optional[Dict[str, Any]] = None  # only in non-prod 