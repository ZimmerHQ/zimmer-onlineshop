from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ZimmerProvisionRequest(BaseModel):
    user_automation_id: int
    user_id: int
    demo_tokens: int
    service_url: Optional[str] = None

class ZimmerProvisionResponse(BaseModel):
    success: bool
    message: str
    provisioned_at: datetime
    integration_status: str
    service_url: Optional[str] = None

class ZimmerUsageRequest(BaseModel):
    user_automation_id: int
    units: int
    usage_type: str
    meta: Optional[dict] = None

class ZimmerUsageResponse(BaseModel):
    accepted: bool
    remaining_demo_tokens: int
    remaining_paid_tokens: int
    message: str

class ZimmerKBStatusResponse(BaseModel):
    status: str
    last_updated: Optional[datetime] = None
    total_documents: int
    healthy: bool

class ZimmerKBResetResponse(BaseModel):
    success: bool
    message: str
    reset_at: datetime
