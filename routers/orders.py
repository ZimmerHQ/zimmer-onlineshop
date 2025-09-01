from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from services.order_service import (
    create_draft,
    confirm_order,
    update_status,
    get_order,
    list_orders
)
from schemas.order import OrderDraftIn, OrderConfirmIn, OrderUpdateStatusIn, OrderOut

router = APIRouter(tags=["orders"])


@router.post("/draft", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_draft_order_endpoint(payload: OrderDraftIn, db: Session = Depends(get_db)):
    """
    Create a draft order from chatbot.
    
    - Creates order with status "draft"
    - Validates all products and variants exist
    - Calculates total amount including variant price adjustments
    - Returns the created draft order
    """
    return create_draft(db, payload)


@router.post("/confirm", response_model=OrderOut)
def confirm_order_endpoint(payload: OrderConfirmIn, db: Session = Depends(get_db)):
    """
    Confirm a draft order (move to pending status).
    
    - Only draft orders can be confirmed
    - Moves status from "draft" to "pending"
    - Sets confirmed_at timestamp
    - No inventory changes at this stage
    """
    return confirm_order(db, payload.order_id)


@router.patch("/{order_id}/status", response_model=OrderOut)
def update_order_status_endpoint(
    order_id: int, 
    payload: OrderUpdateStatusIn, 
    db: Session = Depends(get_db)
):
    """
    Update order status. On transition to "sold", decrement inventory.
    
    Valid status transitions:
    - draft → pending, cancelled
    - pending → approved, cancelled  
    - approved → sold, cancelled
    - sold → cancelled
    - cancelled → (no further changes)
    
    When status changes to "sold":
    - Decrements inventory (product stock or variant stock)
    - Rejects if insufficient stock
    - Updates shipped_at timestamp
    """
    return update_status(db, order_id, payload.status)


@router.get("/{order_id}", response_model=OrderOut)
def get_order_endpoint(order_id: int, db: Session = Depends(get_db)):
    """
    Get order by ID with all items and details.
    
    Returns complete order information including:
    - Customer details
    - Order items with product and variant info
    - Status and payment information
    - Timestamps for all status changes
    """
    return get_order(db, order_id)


@router.get("/", response_model=List[OrderOut])
def list_orders_endpoint(
    status: Optional[str] = Query(None, description="Filter by order status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db)
):
    """
    List orders with optional status filtering.
    
    - Use `status` to filter by order status
    - Use `limit` and `offset` for pagination
    - Orders are sorted by creation date (newest first)
    - Returns orders with all items and details
    """
    # Convert status string to enum if provided
    status_enum = None
    if status:
        try:
            from models import OrderStatus
            status_enum = OrderStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}. Valid values: draft, pending, approved, sold, cancelled"
            )
    
    orders, total_count = list_orders(db, status=status_enum, limit=limit, offset=offset)
    return orders 