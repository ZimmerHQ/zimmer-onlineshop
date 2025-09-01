from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageOut(BaseModel):
    id: int
    conversation_id: str
    role: str
    text: str
    intent: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationOut(BaseModel):
    id: str
    messages: list[MessageOut]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 