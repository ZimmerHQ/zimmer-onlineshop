from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from services.crm_service import (
    get_customer_by_phone,
    get_customer_by_code,
    get_customer_by_reference,
    list_customers_with_stats,
    get_customer_detail,
    get_crm_overview
)

router = APIRouter(tags=["customers"])


@router.get("/code/{customer_code}")
def get_customer_by_code_endpoint(customer_code: str, db: Session = Depends(get_db)):
    """
    Get customer by customer code.
    
    Returns customer information with order statistics.
    """
    customer = get_customer_by_code(db, customer_code)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with code '{customer_code}' not found"
        )
    return customer


@router.get("/ref/{ref}")
def get_customer_by_reference_endpoint(ref: str, db: Session = Depends(get_db)):
    """
    Get customer by either ID or code.
    
    Automatically detects whether the reference is an ID (integer) or code (CUS-YYYY-NNNNNN).
    Returns customer information with order statistics.
    """
    customer = get_customer_by_reference(db, ref)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer '{ref}' not found"
        )
    return customer


@router.get("/phone/{phone}")
def get_customer_by_phone_endpoint(phone: str, db: Session = Depends(get_db)):
    """
    Get customer by phone number.
    
    Returns customer information with order statistics.
    """
    customer = get_customer_by_phone(db, phone)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with phone '{phone}' not found"
        )
    return customer


@router.get("/")
def list_customers_endpoint(
    limit: int = Query(200, ge=1, le=1000, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    List customers with order statistics.
    
    Returns customers sorted by total spending (highest first).
    """
    return list_customers_with_stats(db, limit=limit)


@router.get("/overview")
def get_crm_overview_endpoint(db: Session = Depends(get_db)):
    """
    Get CRM overview statistics.
    
    Returns total customers, orders, revenue, and top customer information.
    """
    return get_crm_overview(db)
