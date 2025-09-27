from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class SupportRequestStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class SupportRequestCreate(BaseModel):
    customer_name: str
    customer_phone: str
    message: str
    telegram_user_id: Optional[str] = None

class SupportRequestUpdate(BaseModel):
    status: Optional[SupportRequestStatus] = None
    admin_notes: Optional[str] = None

class SupportRequestOut(BaseModel):
    id: int
    customer_name: str
    customer_phone: str
    message: str
    status: SupportRequestStatus
    telegram_user_id: Optional[str] = None
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
