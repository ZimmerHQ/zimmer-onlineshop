"""
Chat order service for creating orders from chat interactions.
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
import time

from models import Product, Order, OrderItem, OrderStatus, PaymentStatus
from utils.business_codes import ensure_order_code

def create_order_from_chat(
    db: Session,
    *,
    product_code: str,
    quantity: int = 1,
    meta: Optional[Dict[str, Any]] = None,
    customer_name: Optional[str] = None,
) -> Order:
    """
    Create an order (draft -> pending) for a single product by code.
    Loads Product from DB to get authoritative price.
    """
    meta = meta or {}

    product = db.query(Product).filter(Product.code == product_code).first()
    if not product:
        raise ValueError(f"Product with code {product_code} not found")

    unit_price = product.price or 0
    qty = max(1, quantity)
    total_amount = unit_price * qty

    # Generate unique order number
    timestamp = int(time.time() * 1000) % 10000  # Last 4 digits of timestamp
    order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{product.id:03d}-{timestamp:04d}"
    
    order = Order(
        order_number=order_number,
        customer_name=customer_name or "Chat Customer",
        customer_phone="chat-order",
        customer_address="Chat Order",
        total_amount=total_amount,
        final_amount=total_amount,
        status=OrderStatus.DRAFT,
        payment_status=PaymentStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(order)
    db.flush()  # get order.id

    item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=qty,
        unit_price=unit_price,
        total_price=unit_price * qty,
        product_name=product.name,
        product_code=product.code,  # Store product code snapshot
        product_price=unit_price,
        variant_size=meta.get("size") if meta else None,
        variant_color=meta.get("color") if meta else None,
    )
    db.add(item)

    # move to pending
    order.status = OrderStatus.PENDING
    
    # Ensure order has a code
    ensure_order_code(db, order)
    
    db.commit()
    db.refresh(order)
    return order