from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional, Literal
from datetime import datetime
import uuid

from models import Order, OrderItem, Product, ProductVariant, OrderStatus, PaymentStatus
from schemas.order import OrderDraftIn, OrderConfirmIn, OrderUpdateStatusIn, OrderOut, OrderItemOut
from services.product_service import get_product


def generate_order_number() -> str:
    """Generate a unique order number."""
    timestamp = datetime.now().strftime("%Y%m%d")
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"ORD-{timestamp}-{unique_id}"


def decrement_stock(db: Session, product_id: int, variant_id: Optional[int], quantity: int) -> None:
    """
    Decrement stock for a product or variant atomically.
    
    Args:
        db: Database session
        product_id: Product ID
        variant_id: Variant ID (optional)
        quantity: Quantity to decrement
        
    Raises:
        HTTPException: If insufficient stock
    """
    try:
        if variant_id:
            # Decrement variant stock
            variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
            if not variant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Variant with ID {variant_id} not found"
                )
            if variant.product_id != product_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Variant does not belong to the specified product"
                )
            
            if variant.stock < quantity:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Insufficient stock for variant {variant.id} (size: {variant.size}, color: {variant.color}). Available: {variant.stock}, Requested: {quantity}"
                )
            
            variant.stock -= quantity
            variant.updated_at = datetime.utcnow()
        else:
            # Decrement product stock
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {product_id} not found"
                )
            
            if product.stock < quantity:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Insufficient stock for product {product.code}. Available: {product.stock}, Requested: {quantity}"
                )
            
            product.stock -= quantity
            product.updated_at = datetime.utcnow()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stock update failed: {str(e)}"
        )


def validate_status_transition(current_status: OrderStatus, new_status: OrderStatus) -> bool:
    """
    Validate if a status transition is allowed.
    
    Args:
        current_status: Current order status
        new_status: New order status
        
    Returns:
        bool: True if transition is valid
    """
    valid_transitions = {
        OrderStatus.DRAFT: [OrderStatus.PENDING, OrderStatus.CANCELLED],
        OrderStatus.PENDING: [OrderStatus.APPROVED, OrderStatus.CANCELLED],
        OrderStatus.APPROVED: [OrderStatus.SOLD, OrderStatus.CANCELLED],
        OrderStatus.SOLD: [OrderStatus.CANCELLED],  # Can only cancel sold orders
        OrderStatus.CANCELLED: []  # Cancelled orders cannot change status
    }
    
    return new_status in valid_transitions.get(current_status, [])


def create_draft(db: Session, payload: OrderDraftIn) -> OrderOut:
    """
    Creates a new product with auto-generated code.
    
    Args:
        db: Database session
        payload: Product creation data
        
    Returns:
        ProductOut: Created product with category name
        
    Raises:
        HTTPException: If category doesn't exist or code generation fails
    """
    # Validate all products exist
    total_amount = 0
    items_data = []
    
    for item in payload.items:
        product = get_product(db, item.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item.product_id} not found"
            )
        
        # Calculate unit price (base price + variant price delta)
        unit_price = product.price
        variant_size = None
        variant_color = None
        
        if item.variant_id:
            variant = db.query(ProductVariant).filter(ProductVariant.id == item.variant_id).first()
            if not variant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Variant with ID {item.variant_id} not found"
                )
            if variant.product_id != item.product_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Variant does not belong to the specified product"
                )
            unit_price += variant.price_delta
            variant_size = variant.size
            variant_color = variant.color
        
        item_total = unit_price * item.quantity
        total_amount += item_total
        
        items_data.append({
            'product_id': item.product_id,
            'variant_id': item.variant_id,
            'product_name': product.name,
            'product_price': product.price,
            'product_image_url': product.thumbnail_url or product.image_url,
            'variant_size': variant_size,
            'variant_color': variant_color,
            'quantity': item.quantity,
            'unit_price': unit_price,
            'total_price': item_total
        })
    
    # Create order
    order = Order(
        order_number=generate_order_number(),
        customer_name=payload.customer_name,
        customer_phone=payload.contact,  # Store contact in phone field for now
        total_amount=total_amount,
        shipping_cost=0.0,  # Default to 0 for draft
        discount_amount=0.0,  # Default to 0 for draft
        final_amount=total_amount,
        status=OrderStatus.DRAFT,
        payment_status=PaymentStatus.PENDING,
        customer_notes=payload.note
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Create order items
    for item_data in items_data:
        order_item = OrderItem(
            order_id=order.id,
            **item_data
        )
        db.add(order_item)
    
    db.commit()
    db.refresh(order)
    
    return to_order_out(order)


def confirm_order(db: Session, order_id: int) -> OrderOut:
    """
    Confirm a draft order (move to pending status).
    
    Args:
        db: Database session
        order_id: Order ID to confirm
        
    Returns:
        OrderOut: Confirmed order
        
    Raises:
        HTTPException: If order not found or not in draft status
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.status != OrderStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft orders can be confirmed"
        )
    
    # Update status to pending
    order.status = OrderStatus.PENDING
    order.confirmed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    
    return to_order_out(order)


def update_status(db: Session, order_id: int, new_status: str) -> OrderOut:
    """
    Update order status. On transition to "sold", decrement inventory.
    
    Args:
        db: Session: Database session
        order_id: Order ID
        new_status: New status string
        
    Returns:
        OrderOut: Updated order
        
    Raises:
        HTTPException: If order not found or status transition invalid
    """
    # Convert string to enum
    try:
        new_status_enum = OrderStatus(new_status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {new_status}. Valid values: draft, pending, approved, sold, cancelled"
        )
    
    order = db.query(Order).options(
        joinedload(Order.items)
    ).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    old_status = order.status
    
    # Validate status transition
    if not validate_status_transition(old_status, new_status_enum):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from {old_status} to {new_status_enum}"
        )
    
    # Handle inventory decrement on "sold" status
    if new_status_enum == OrderStatus.SOLD:
        try:
            # Decrement inventory in a transaction
            for item in order.items:
                decrement_stock(db, item.product_id, item.variant_id, item.quantity)
        except HTTPException:
            # Re-raise HTTP exceptions (like 409 for insufficient stock)
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Inventory update failed: {str(e)}"
            )
    
    # Update order status
    order.status = new_status_enum
    order.updated_at = datetime.utcnow()
    
    # Set additional timestamps based on status
    if new_status_enum == OrderStatus.SOLD:
        order.shipped_at = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    
    return to_order_out(order)


def get_order(db: Session, order_id: int) -> OrderOut:
    """
    Get order by ID with items.
    
    Args:
        db: Database session
        order_id: Order ID
        
    Returns:
        OrderOut: Order with items
        
    Raises:
        HTTPException: If order not found
    """
    order = db.query(Order).options(
        joinedload(Order.items)
    ).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return to_order_out(order)


def list_orders(db: Session, status: Optional[OrderStatus] = None, 
                limit: int = 50, offset: int = 0) -> tuple[List[OrderOut], int]:
    """
    List orders with optional status filter.
    
    Args:
        db: Database session
        status: Filter by status
        limit: Maximum number of results
        offset: Number of results to skip
        
    Returns:
        List[OrderOut]: List of orders
        int: Total count
    """
    query = db.query(Order).options(joinedload(Order.items))
    
    if status:
        query = query.filter(Order.status == status)
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination and sorting
    orders = query.order_by(Order.created_at.desc()).offset(offset).limit(limit).all()
    
    # Convert to OrderOut
    order_outs = [to_order_out(order) for order in orders]
    
    return order_outs, total_count


def to_order_out(order: Order) -> OrderOut:
    """Convert Order model to OrderOut schema."""
    # Convert order items
    items = []
    for item in order.items:
        items.append(OrderItemOut(
            id=item.id,
            product_id=item.product_id,
            variant_id=getattr(item, 'variant_id', None),
            product_name=item.product_name,
            product_price=item.product_price,
            product_image_url=getattr(item, 'product_image_url', None),
            variant_size=getattr(item, 'variant_size', None),
            variant_color=getattr(item, 'variant_color', None),
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.total_price
        ))
    
    # Ensure status is properly converted to enum
    from models import OrderStatus
    status_enum = order.status
    if isinstance(status_enum, str):
        try:
            status_enum = OrderStatus(status_enum)
        except ValueError:
            # Fallback to DRAFT if invalid status
            status_enum = OrderStatus.DRAFT
    
    return OrderOut(
        id=order.id,
        order_number=order.order_number,
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        customer_address=order.customer_address,
        customer_instagram=getattr(order, 'customer_instagram', None),
        total_amount=order.total_amount,
        shipping_cost=getattr(order, 'shipping_cost', 0.0),
        discount_amount=getattr(order, 'discount_amount', 0.0),
        final_amount=order.final_amount,
        status=status_enum,
        payment_status=getattr(order, 'payment_status', None),
        payment_method=getattr(order, 'payment_method', None),
        shipping_method=getattr(order, 'shipping_method', None),
        tracking_number=getattr(order, 'tracking_number', None),
        estimated_delivery=getattr(order, 'estimated_delivery', None),
        created_at=order.created_at,
        updated_at=order.updated_at,
        confirmed_at=getattr(order, 'confirmed_at', None),
        shipped_at=getattr(order, 'shipped_at', None),
        delivered_at=getattr(order, 'delivered_at', None),
        admin_notes=getattr(order, 'admin_notes', None),
        customer_notes=getattr(order, 'customer_notes', None),
        items=items
    ) 