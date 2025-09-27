from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from services.support_service import (
    create_support_request, 
    get_support_requests, 
    get_support_request,
    update_support_request,
    delete_support_request,
    get_support_stats
)
from schemas.support import SupportRequestCreate, SupportRequestUpdate, SupportRequestOut, SupportRequestStatus

router = APIRouter()

@router.post("/requests", response_model=SupportRequestOut)
def create_request(request: SupportRequestCreate, db: Session = Depends(get_db)):
    """Create a new support request"""
    return create_support_request(db, request)

@router.get("/requests", response_model=List[SupportRequestOut])
def list_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[SupportRequestStatus] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all support requests with optional filtering"""
    return get_support_requests(db, skip=skip, limit=limit, status=status)

@router.get("/requests/{request_id}", response_model=SupportRequestOut)
def get_request(request_id: int, db: Session = Depends(get_db)):
    """Get a specific support request"""
    request = get_support_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Support request not found")
    return request

@router.patch("/requests/{request_id}", response_model=SupportRequestOut)
def update_request(
    request_id: int, 
    request_update: SupportRequestUpdate, 
    db: Session = Depends(get_db)
):
    """Update a support request"""
    request = update_support_request(db, request_id, request_update)
    if not request:
        raise HTTPException(status_code=404, detail="Support request not found")
    return request

@router.delete("/requests/{request_id}")
def delete_request(request_id: int, db: Session = Depends(get_db)):
    """Delete a support request"""
    success = delete_support_request(db, request_id)
    if not success:
        raise HTTPException(status_code=404, detail="Support request not found")
    return {"message": "Support request deleted successfully"}

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get support request statistics"""
    return get_support_stats(db)
