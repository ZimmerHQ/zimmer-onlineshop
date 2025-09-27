from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from models import SupportRequest, SupportRequestStatus
from schemas.support import SupportRequestCreate, SupportRequestUpdate, SupportRequestOut
from datetime import datetime

def create_support_request(db: Session, request: SupportRequestCreate) -> SupportRequestOut:
    """Create a new support request"""
    db_request = SupportRequest(
        customer_name=request.customer_name,
        customer_phone=request.customer_phone,
        message=request.message,
        telegram_user_id=request.telegram_user_id,
        status=SupportRequestStatus.PENDING
    )
    
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    return SupportRequestOut.model_validate(db_request)

def get_support_requests(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[SupportRequestStatus] = None
) -> List[SupportRequestOut]:
    """Get all support requests with optional status filter"""
    query = db.query(SupportRequest)
    
    if status:
        query = query.filter(SupportRequest.status == status)
    
    requests = query.order_by(desc(SupportRequest.created_at)).offset(skip).limit(limit).all()
    
    return [SupportRequestOut.model_validate(req) for req in requests]

def get_support_request(db: Session, request_id: int) -> Optional[SupportRequestOut]:
    """Get a specific support request by ID"""
    request = db.query(SupportRequest).filter(SupportRequest.id == request_id).first()
    
    if not request:
        return None
    
    return SupportRequestOut.model_validate(request)

def update_support_request(
    db: Session, 
    request_id: int, 
    request_update: SupportRequestUpdate
) -> Optional[SupportRequestOut]:
    """Update a support request"""
    request = db.query(SupportRequest).filter(SupportRequest.id == request_id).first()
    
    if not request:
        return None
    
    if request_update.status is not None:
        # Convert string status to enum
        if isinstance(request_update.status, str):
            status_map = {
                'pending': SupportRequestStatus.PENDING,
                'in_progress': SupportRequestStatus.IN_PROGRESS,
                'resolved': SupportRequestStatus.RESOLVED,
                'closed': SupportRequestStatus.CLOSED
            }
            request.status = status_map.get(request_update.status.lower(), SupportRequestStatus.PENDING)
        else:
            request.status = request_update.status
    
    if request_update.admin_notes is not None:
        request.admin_notes = request_update.admin_notes
    
    request.updated_at = datetime.now()
    
    db.commit()
    db.refresh(request)
    
    return SupportRequestOut.model_validate(request)

def delete_support_request(db: Session, request_id: int) -> bool:
    """Delete a support request"""
    request = db.query(SupportRequest).filter(SupportRequest.id == request_id).first()
    
    if not request:
        return False
    
    db.delete(request)
    db.commit()
    
    return True

def get_support_stats(db: Session) -> dict:
    """Get support request statistics"""
    total_requests = db.query(SupportRequest).count()
    pending_requests = db.query(SupportRequest).filter(SupportRequest.status == SupportRequestStatus.PENDING).count()
    in_progress_requests = db.query(SupportRequest).filter(SupportRequest.status == SupportRequestStatus.IN_PROGRESS).count()
    resolved_requests = db.query(SupportRequest).filter(SupportRequest.status == SupportRequestStatus.RESOLVED).count()
    
    return {
        "total_requests": total_requests,
        "pending_requests": pending_requests,
        "in_progress_requests": in_progress_requests,
        "resolved_requests": resolved_requests
    }
