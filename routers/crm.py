from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from database import get_db
from schemas.customer import CustomerUpdateIn, CustomerOut, CustomerCreateIn
from services.crm_service import (
    list_customers_with_stats,
    get_customer_detail,
    get_top_customers,
    upsert_customer,
    update_customer,
    delete_customer,
    attach_order,
    get_customer_purchase_history,
    search_customer_orders
)

router = APIRouter(prefix="/api/crm", tags=["crm"])

@router.get("/customers", response_model=List[Dict[str, Any]])
def list_customers(db: Session = Depends(get_db), limit: int = Query(200, ge=1, le=1000)):
    """List customers with their order statistics"""
    return list_customers_with_stats(db, limit=limit)

@router.get("/customers/{customer_id}", response_model=Dict[str, Any])
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get detailed customer information"""
    try:
        return get_customer_detail(db, customer_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Customer not found: {str(e)}")

@router.get("/top", response_model=List[Dict[str, Any]])
def top_customers(db: Session = Depends(get_db), limit: int = Query(20, ge=1, le=100)):
    """Get top customers by total spending"""
    return get_top_customers(db, limit=limit)

@router.post("/customers/upsert", response_model=Dict[str, Any])
def upsert_customer_endpoint(
    first_name: str,
    last_name: str,
    phone: str,
    address: str,
    postal_code: str,
    notes: str = "",
    db: Session = Depends(get_db)
):
    """Create or update a customer"""
    try:
        customer = upsert_customer(
            db=db,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            address=address,
            postal_code=postal_code,
            notes=notes
        )
        return {
            "customer_id": customer.id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "phone": customer.phone,
            "address": customer.address,
            "postal_code": customer.postal_code,
            "notes": customer.notes
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to upsert customer: {str(e)}")

@router.put("/customers/{customer_id}", response_model=CustomerOut)
def update_customer_endpoint(
    customer_id: int,
    customer_data: CustomerUpdateIn,
    db: Session = Depends(get_db)
):
    """Update a customer by ID"""
    try:
        customer = update_customer(
            db=db,
            customer_id=customer_id,
            first_name=customer_data.first_name,
            last_name=customer_data.last_name,
            phone=customer_data.phone,
            address=customer_data.address,
            postal_code=customer_data.postal_code,
            notes=customer_data.notes
        )
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        return CustomerOut(
            customer_id=customer.id,
            customer_code=customer.customer_code,
            first_name=customer.first_name,
            last_name=customer.last_name,
            phone=customer.phone,
            address=customer.address,
            postal_code=customer.postal_code,
            notes=customer.notes
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update customer: {str(e)}")

@router.delete("/customers/{customer_id}")
def delete_customer_endpoint(customer_id: int, db: Session = Depends(get_db)):
    """Delete a customer by ID"""
    try:
        success = delete_customer(db=db, customer_id=customer_id)
        if not success:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        return {"message": "Customer deleted successfully", "customer_id": customer_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete customer: {str(e)}")

@router.post("/orders/attach", response_model=Dict[str, Any])
def attach_order_endpoint(
    customer_id: int,
    order_id: int,
    db: Session = Depends(get_db)
):
    """Attach an order to a customer"""
    try:
        result = attach_order(db=db, customer_id=customer_id, order_id=order_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to attach order: {str(e)}")

@router.get("/customers/{customer_id}/purchases")
def get_customer_purchases(
    customer_id: int,
    search: str = Query(None, description="Search query for orders"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get detailed purchase history for a customer with search functionality"""
    try:
        return get_customer_purchase_history(
            db=db, 
            customer_id=customer_id, 
            search_query=search,
            limit=limit,
            offset=offset
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get purchase history: {str(e)}")

@router.get("/orders/search")
def search_orders(
    q: str = Query(..., description="Search query"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Search through all customer orders"""
    try:
        return search_customer_orders(
            db=db,
            search_query=q,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
