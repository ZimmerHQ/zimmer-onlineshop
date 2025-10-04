"""
Provision router for Zimmer platform integration.
Handles user provisioning and webhook URL generation.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Union
from database import get_db
from app.services.users_service import UsersService
from app.core.service_token import require_service_token
from app.core.settings import WEBHOOK_PATH_TEMPLATE

router = APIRouter()

class ProvisionRequest(BaseModel):
    """Request model for user provisioning."""
    user_automation_id: Union[int, str]
    user_id: str
    bot_token: str
    demo_tokens: int = 0

class ProvisionResponse(BaseModel):
    """Response model for user provisioning."""
    success: bool
    message: str
    webhook_url: str

@router.post("/api/provision", response_model=ProvisionResponse)
async def provision_user(
    request: Request,
    provision_data: ProvisionRequest,
    service_token: str = Depends(require_service_token)
):
    """
    Provision a user for the automation system.
    
    Args:
        request: FastAPI request object
        provision_data: User provisioning data
        service_token: Validated service token
        
    Returns:
        Provision response with webhook URL
    """
    # Get database session
    db = next(get_db())
    users_service = UsersService(db)
    
    try:
        # Convert user_automation_id to string for consistency
        automation_id = str(provision_data.user_automation_id)
        
        # Ensure user exists with demo tokens
        user = users_service.ensure_user(
            user_id=provision_data.user_id,
            automation_id=automation_id,
            demo_tokens=provision_data.demo_tokens
        )
        
        # Generate webhook URL using configurable template
        base_url = str(request.base_url).rstrip('/')
        webhook_path = WEBHOOK_PATH_TEMPLATE.format(user_id=provision_data.user_id)
        webhook_url = f"{base_url}{webhook_path}"
        
        return ProvisionResponse(
            success=True,
            message=f"User {provision_data.user_id} provisioned successfully for automation {automation_id}",
            webhook_url=webhook_url
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error provisioning user: {str(e)}"
        )
    finally:
        db.close()

