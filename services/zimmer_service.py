from sqlalchemy.orm import Session
from models import ZimmerTenant
from schemas.zimmer import (
    ZimmerProvisionRequest, ZimmerProvisionResponse,
    ZimmerUsageRequest, ZimmerUsageResponse,
    ZimmerKBStatusResponse, ZimmerKBResetResponse
)
from datetime import datetime
from typing import Optional

def provision_tenant(db: Session, request: ZimmerProvisionRequest) -> ZimmerProvisionResponse:
    """Provision or update a Zimmer tenant."""
    # Check if tenant already exists
    tenant = db.query(ZimmerTenant).filter(
        ZimmerTenant.user_automation_id == request.user_automation_id
    ).first()
    
    if tenant:
        # Update existing tenant
        tenant.user_id = request.user_id
        tenant.demo_tokens = request.demo_tokens
        tenant.service_url = request.service_url
        tenant.integration_status = "active"
        tenant.updated_at = datetime.now()
    else:
        # Create new tenant
        tenant = ZimmerTenant(
            user_automation_id=request.user_automation_id,
            user_id=request.user_id,
            demo_tokens=request.demo_tokens,
            service_url=request.service_url,
            integration_status="active"
        )
        db.add(tenant)
    
    db.commit()
    db.refresh(tenant)
    
    return ZimmerProvisionResponse(
        success=True,
        message="Tenant provisioned successfully",
        provisioned_at=tenant.updated_at,
        integration_status=tenant.integration_status,
        service_url=tenant.service_url
    )

def consume_usage(db: Session, request: ZimmerUsageRequest) -> ZimmerUsageResponse:
    """Consume tokens for a tenant (demo first, then paid)."""
    tenant = db.query(ZimmerTenant).filter(
        ZimmerTenant.user_automation_id == request.user_automation_id
    ).first()
    
    if not tenant:
        return ZimmerUsageResponse(
            accepted=False,
            remaining_demo_tokens=0,
            remaining_paid_tokens=0,
            message="Tenant not found"
        )
    
    units_to_consume = request.units
    
    # Consume demo tokens first
    if tenant.demo_tokens >= units_to_consume:
        tenant.demo_tokens -= units_to_consume
        units_to_consume = 0
    else:
        units_to_consume -= tenant.demo_tokens
        tenant.demo_tokens = 0
    
    # Then consume paid tokens
    if units_to_consume > 0:
        if tenant.paid_tokens >= units_to_consume:
            tenant.paid_tokens -= units_to_consume
        else:
            # Not enough tokens
            db.commit()
            return ZimmerUsageResponse(
                accepted=False,
                remaining_demo_tokens=tenant.demo_tokens,
                remaining_paid_tokens=tenant.paid_tokens,
                message="Insufficient tokens"
            )
    
    tenant.updated_at = datetime.now()
    db.commit()
    db.refresh(tenant)
    
    return ZimmerUsageResponse(
        accepted=True,
        remaining_demo_tokens=tenant.demo_tokens,
        remaining_paid_tokens=tenant.paid_tokens,
        message="Usage consumed successfully"
    )

def get_kb_status(db: Session, user_automation_id: int) -> ZimmerKBStatusResponse:
    """Get knowledge base status for a tenant."""
    tenant = db.query(ZimmerTenant).filter(
        ZimmerTenant.user_automation_id == user_automation_id
    ).first()
    
    if not tenant:
        return ZimmerKBStatusResponse(
            status="error",
            last_updated=None,
            total_documents=0,
            healthy=False
        )
    
    return ZimmerKBStatusResponse(
        status=tenant.kb_status,
        last_updated=tenant.kb_last_updated,
        total_documents=tenant.kb_total_documents,
        healthy=tenant.kb_healthy
    )

def reset_kb(db: Session, user_automation_id: int) -> ZimmerKBResetResponse:
    """Reset knowledge base for a tenant."""
    tenant = db.query(ZimmerTenant).filter(
        ZimmerTenant.user_automation_id == user_automation_id
    ).first()
    
    if not tenant:
        return ZimmerKBResetResponse(
            success=False,
            message="Tenant not found",
            reset_at=datetime.now()
        )
    
    # Reset KB fields
    tenant.kb_status = "empty"
    tenant.kb_last_updated = None
    tenant.kb_total_documents = 0
    tenant.kb_healthy = False
    tenant.updated_at = datetime.now()
    
    db.commit()
    db.refresh(tenant)
    
    return ZimmerKBResetResponse(
        success=True,
        message="Knowledge base reset successfully",
        reset_at=tenant.updated_at
    )
