"""
Business code generators for customers and orders.
Provides stable, human-readable codes for external references.
"""

# Simple base36 implementation
def _base36_encode(num: int) -> str:
    """Encode integer to base36 string."""
    if num == 0:
        return "0"
    
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = ""
    
    while num:
        num, remainder = divmod(num, 36)
        result = alphabet[remainder] + result
    
    return result


def _base36_decode(s: str) -> int:
    """Decode base36 string to integer."""
    return int(s, 36)
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Customer, Order


def generate_customer_code(db: Session, customer: Optional[Customer] = None) -> str:
    """
    Generate a unique customer code in format: CUS-YYYY-NNNNNN
    
    Args:
        db: Database session
        customer: Customer object (optional, for retry scenarios)
        
    Returns:
        str: Unique customer code
        
    Raises:
        ValueError: If unable to generate unique code after retries
    """
    year = datetime.now().year
    
    # Get the highest sequence number for this year
    max_code = db.query(func.max(Customer.customer_code)).filter(
        Customer.customer_code.like(f"CUS-{year}-%")
    ).scalar()
    
    if max_code:
        # Extract sequence number from existing code
        try:
            sequence = int(max_code.split('-')[-1])
        except (ValueError, IndexError):
            sequence = 0
    else:
        sequence = 0
    
    # Generate new code with collision detection
    max_retries = 100
    for attempt in range(max_retries):
        sequence += 1
        code = f"CUS-{year}-{sequence:06d}"
        
        # Check if code already exists
        existing = db.query(Customer).filter(Customer.customer_code == code).first()
        if not existing:
            return code
    
    raise ValueError(f"Unable to generate unique customer code after {max_retries} attempts")


def generate_order_code(db: Session, order: Optional[Order] = None) -> str:
    """
    Generate a unique order code using base36 encoding of order ID.
    Format: ORD-XXXXXX (where XXXXXX is base36 encoded)
    
    Args:
        db: Database session
        order: Order object (optional, for retry scenarios)
        
    Returns:
        str: Unique order code
        
    Raises:
        ValueError: If unable to generate unique code after retries
    """
    # If order is provided, use its ID
    if order and order.id:
        order_id = order.id
    else:
        # Get the next available ID
        max_id = db.query(func.max(Order.id)).scalar() or 0
        order_id = max_id + 1
    
    # Generate base36 encoded code
    base36_id = _base36_encode(order_id)
    code = f"ORD-{base36_id}"
    
    # Check for collisions (very rare with base36)
    existing = db.query(Order).filter(Order.order_code == code).first()
    if existing:
        # If collision, append suffix
        for suffix in range(1, 100):
            collision_code = f"{code}-{suffix}"
            existing = db.query(Order).filter(Order.order_code == collision_code).first()
            if not existing:
                return collision_code
    
    return code


def resolve_customer_reference(db: Session, ref: str) -> Optional[Customer]:
    """
    Resolve customer by either ID (int) or code (str).
    
    Args:
        db: Database session
        ref: Customer reference (ID as string or customer code)
        
    Returns:
        Customer or None if not found
    """
    # Try as customer code first
    if ref.startswith('CUS-'):
        return db.query(Customer).filter(Customer.customer_code == ref).first()
    
    # Try as ID
    try:
        customer_id = int(ref)
        return db.query(Customer).filter(Customer.id == customer_id).first()
    except ValueError:
        pass
    
    return None


def resolve_order_reference(db: Session, ref: str) -> Optional[Order]:
    """
    Resolve order by either ID (int) or code (str).
    
    Args:
        db: Database session
        ref: Order reference (ID as string or order code)
        
    Returns:
        Order or None if not found
    """
    # Try as order code first
    if ref.startswith('ORD-'):
        return db.query(Order).filter(Order.order_code == ref).first()
    
    # Try as ID
    try:
        order_id = int(ref)
        return db.query(Order).filter(Order.id == order_id).first()
    except ValueError:
        pass
    
    return None


def ensure_customer_code(db: Session, customer: Customer) -> str:
    """
    Ensure customer has a code, generating one if missing.
    
    Args:
        db: Database session
        customer: Customer object
        
    Returns:
        str: Customer code
    """
    if customer.customer_code:
        return customer.customer_code
    
    # Generate and assign code
    code = generate_customer_code(db, customer)
    customer.customer_code = code
    db.commit()
    db.refresh(customer)
    
    return code


def ensure_order_code(db: Session, order: Order) -> str:
    """
    Ensure order has a code, generating one if missing.
    
    Args:
        db: Database session
        order: Order object
        
    Returns:
        str: Order code
    """
    if order.order_code:
        return order.order_code
    
    # Generate and assign code
    code = generate_order_code(db, order)
    order.order_code = code
    db.commit()
    db.refresh(order)
    
    return code
