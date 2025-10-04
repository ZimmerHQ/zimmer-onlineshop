"""
Usage router for Zimmer token consumption.
Handles both platform→automation and internal bot/UI→backend token consumption.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from database import get_db
from app.services.users_service import UsersService
from app.services.usage_forwarder import usage_forwarder
from app.core.service_token import require_service_token
from app.core.settings import DEFAULT_AUTOMATION_ID

router = APIRouter()

class PlatformUsageRequest(BaseModel):
    """Request model for platform usage consumption."""
    user_automation_id: str
    tokens_consumed: int
    session_id: Optional[str] = None
    timestamp: Optional[str] = None
    action: str

class PlatformUsageResponse(BaseModel):
    """Response model for platform usage consumption."""
    success: bool
    tokens_consumed: int
    remaining_tokens: int

class InternalUsageRequest(BaseModel):
    """Request model for internal usage consumption."""
    user_id: str
    automation_id: str
    tokens_consumed: int
    action: str
    session_id: Optional[str] = None

class InternalUsageResponse(BaseModel):
    """Response model for internal usage consumption."""
    success: bool
    remaining_tokens: int

@router.post("/api/usage/consume", response_model=PlatformUsageResponse)
async def consume_usage_platform(
    usage_data: PlatformUsageRequest,
    service_token: str = Depends(require_service_token)
):
    """
    Consume tokens from platform→automation calls.
    
    Args:
        usage_data: Usage consumption data from platform
        service_token: Validated service token
        
    Returns:
        Usage consumption response
    """
    # Get database session
    db = next(get_db())
    users_service = UsersService(db)
    
    try:
        # Interpret user_automation_id as user_id (per guideline examples)
        user_id = usage_data.user_automation_id
        automation_id = DEFAULT_AUTOMATION_ID
        
        # Calculate delta (negative for consumption)
        delta = -abs(usage_data.tokens_consumed)
        
        # Prepare metadata
        meta = {
            "session_id": usage_data.session_id,
            "timestamp": usage_data.timestamp or datetime.utcnow().isoformat(),
            "source": "platform"
        }
        
        # Update tokens
        remaining_tokens = users_service.update_tokens(
            user_id=user_id,
            automation_id=automation_id,
            delta=delta,
            reason=usage_data.action,
            meta=meta
        )
        
        return PlatformUsageResponse(
            success=True,
            tokens_consumed=abs(delta),
            remaining_tokens=remaining_tokens
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error consuming tokens: {str(e)}"
        )
    finally:
        db.close()

@router.post("/api/consume-tokens", response_model=InternalUsageResponse)
async def consume_tokens_internal(usage_data: InternalUsageRequest):
    """
    Consume tokens from internal bot/UI→backend calls.
    
    Args:
        usage_data: Internal usage consumption data
        
    Returns:
        Internal usage consumption response
    """
    # Get database session
    db = next(get_db())
    users_service = UsersService(db)
    
    try:
        # Calculate delta (negative for consumption)
        delta = -abs(usage_data.tokens_consumed)
        
        # Prepare metadata
        meta = {
            "session_id": usage_data.session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "internal"
        }
        
        # Update tokens locally
        remaining_tokens = users_service.update_tokens(
            user_id=usage_data.user_id,
            automation_id=usage_data.automation_id,
            delta=delta,
            reason=usage_data.action,
            meta=meta
        )
        
        # Forward usage to platform if configured
        if usage_forwarder.is_configured():
            platform_usage = {
                "user_automation_id": usage_data.user_id,
                "tokens_consumed": abs(delta),
                "session_id": usage_data.session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "action": usage_data.action
            }
            await usage_forwarder.forward_usage_to_platform(platform_usage)
        
        return InternalUsageResponse(
            success=True,
            remaining_tokens=remaining_tokens
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error consuming tokens: {str(e)}"
        )
    finally:
        db.close()

