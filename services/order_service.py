from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional, Literal
from datetime import datetime
import uuid
from decimal import Decimal

from models import Order, OrderItem, Product, ProductVariant, OrderStatus, PaymentStatus, Customer
from schemas.order import OrderDraftIn, OrderDraftByCodeIn, OrderDraftBySkuIn, OrderConfirmIn, OrderUpdateStatusIn, OrderOut, OrderItemOut
from services.product_service import get_product, get_product_by_code
from utils.business_codes import resolve_customer_reference, resolve_order_reference, ensure_order_code, ensure_customer_code


def generate_order_number() -> str:
    """Generate a unique order number."""
    timestamp = datetime.now().strftime("%Y%m%d")
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"ORD-{timestamp}-{unique_id}"


def create_order(db: Session, *, code: str, qty: int, attributes: dict = None, customer_snapshot: dict = None) -> Order:
    """Create a simple order with product code or SKU code, quantity, and customer snapshot."""
    # First try to find by product code
    product = db.query(Product).filter(Product.code == code.upper()).first()
    variant = None
    
    # If not found as product code, try as SKU code
    if not product:
        variant = db.query(ProductVariant).filter(ProductVariant.sku_code == code.upper()).first()
        if variant:
            product = db.query(Product).filter(Product.id == variant.product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product or variant with code {code} not found"
        )
    
    # Calculate totals using real quantity
    q = int(qty)
    if q < 1:
        q = 1  # safety guard
    
    # Use variant price if available, otherwise use product price
    if variant and variant.price_override is not None:
        unit_price = Decimal(variant.price_override)
    else:
        unit_price = Decimal(product.price or 0)
    
    total = unit_price * q

    # Note: Stock is NOT decremented here - it will be decremented when order status changes to "sold"
    # This allows orders to be created as drafts without affecting inventory

    # Create order
    order = Order(
        order_number=generate_order_number(),
        customer_name=customer_snapshot.get("first_name", "") + " " + customer_snapshot.get("last_name", "") if customer_snapshot else "Chat Customer",
        customer_phone=customer_snapshot.get("phone", "chat-order") if customer_snapshot else "chat-order",
        total_amount=total,
        shipping_cost=0.0,
        discount_amount=0.0,
        final_amount=total,
        status=OrderStatus.DRAFT,  # Keep as draft for chat orders
        payment_status=PaymentStatus.PENDING,
        customer_notes=customer_snapshot.get("notes", "") if customer_snapshot else "",
        customer_snapshot=customer_snapshot,
        items_count=q  # Set the correct quantity
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Create order item
    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        variant_id=variant.id if variant else None,
        product_name=product.name,
        product_code=product.code,  # Store product code
        product_price=product.price,
        product_image_url=product.thumbnail_url or product.image_url,
        # Variant information
        sku_code=variant.sku_code if variant else None,
        variant_attributes_snapshot=variant.attributes if variant else attributes,
        unit_price_snapshot=float(unit_price),
        # Legacy variant fields
        variant_size=variant.attributes.get("size", "") if variant and variant.attributes else attributes.get("size", "") if attributes else "",
        variant_color=variant.attributes.get("color", "") if variant and variant.attributes else attributes.get("color", "") if attributes else "",
        quantity=q,
        unit_price=float(unit_price),
        total_price=float(total)
    )
    
    db.add(order_item)
    db.commit()
    db.refresh(order)
    
    return order

def restore_stock(db: Session, product_id: int, variant_id: Optional[int], quantity: int) -> None:
    """
    Restore stock for a product or variant when an order is cancelled.
    
    Args:
        db: Database session
        product_id: Product ID
        variant_id: Variant ID (optional)
        quantity: Quantity to restore
    """
    try:
        if variant_id:
            # Restore variant stock
            variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
            if variant:
                variant.stock += quantity
                variant.updated_at = datetime.utcnow()
        else:
            # Restore product stock
            product = db.query(Product).filter(Product.id == product_id).first()
            if product:
                product.stock += quantity
                product.updated_at = datetime.utcnow()
    except Exception as e:
        # Log error but don't fail the cancellation
        print(f"Warning: Failed to restore stock for product {product_id}: {str(e)}")

def cancel_order(db: Session, order_id: int, reason: str = "") -> dict:
    """Cancel an existing order by order_id and restore stock."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"error": "Order not found"}
    
    # Restore stock for all items in the order
    try:
        for item in order.items:
            restore_stock(db, item.product_id, item.variant_id, item.quantity)
    except Exception as e:
        # Log error but continue with cancellation
        print(f"Warning: Failed to restore stock during cancellation: {str(e)}")
    
    order.status = OrderStatus.CANCELLED
    order.admin_notes = f"Cancelled: {reason}" if reason else "Cancelled by user"
    
    db.commit()
    db.refresh(order)
    
    return {"order_id": order_id, "status": "cancelled", "reason": reason}


def restore_stock(db: Session, product_id: int, variant_id: Optional[int], quantity: int) -> None:
    """
    Restore stock for a product or variant (opposite of decrement_stock).
    
    Args:
        db: Database session
        product_id: Product ID
        variant_id: Variant ID (optional)
        quantity: Quantity to restore
    """
    try:
        if variant_id:
            # Restore variant stock
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
            
            variant.stock_qty += quantity
            variant.updated_at = datetime.utcnow()
        else:
            # Restore product stock
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {product_id} not found"
                )
            
            product.stock += quantity
            product.updated_at = datetime.utcnow()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stock restoration failed: {str(e)}"
        )


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
            
            if variant.stock_qty < quantity:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Insufficient stock for variant {variant.id} (size: {variant.size}, color: {variant.color}). Available: {variant.stock_qty}, Requested: {quantity}"
                )
            
            variant.stock_qty -= quantity
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
            'product_code': product.code,  # Store product code snapshot
            'product_price': product.price,
            'product_image_url': product.thumbnail_url or product.image_url,
            'variant_size': variant_size,
            'variant_color': variant_color,
            'quantity': item.quantity,
            'unit_price': unit_price,
            'total_price': item_total
        })
    
    # Create customer snapshot if customer data is provided
    customer_snapshot = None
    if hasattr(payload, 'customer_snapshot') and payload.customer_snapshot:
        customer_snapshot = payload.customer_snapshot
    elif hasattr(payload, 'customer_name') and hasattr(payload, 'contact'):
        # Create basic snapshot from available data
        customer_snapshot = {
            "first_name": payload.customer_name.split(' ')[0] if payload.customer_name else "",
            "last_name": ' '.join(payload.customer_name.split(' ')[1:]) if payload.customer_name and ' ' in payload.customer_name else "",
            "phone": payload.contact,
            "address": getattr(payload, 'address', ''),
            "postal_code": getattr(payload, 'postal_code', ''),
            "notes": getattr(payload, 'note', '')
        }

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
        customer_notes=payload.note,
        customer_snapshot=customer_snapshot
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Ensure order has a code
    ensure_order_code(db, order)
    
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


def create_draft_by_codes(db: Session, payload: OrderDraftByCodeIn) -> OrderOut:
    """
    Create a draft order using product codes and optional customer code.
    
    Args:
        db: Database session
        payload: Order creation data with codes
        
    Returns:
        OrderOut: Created order with code
        
    Raises:
        HTTPException: If products not found or customer code invalid
    """
    # Validate all products exist by code
    total_amount = 0
    items_data = []
    
    for item in payload.items:
        product = get_product_by_code(db, item.product_code)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with code '{item.product_code}' not found"
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
            if variant.product_id != product.id:
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
            'product_id': product.id,
            'variant_id': item.variant_id,
            'product_name': product.name,
            'product_code': product.code,  # Store product code snapshot
            'product_price': product.price,
            'product_image_url': product.thumbnail_url or product.image_url,
            'variant_size': variant_size,
            'variant_color': variant_color,
            'quantity': item.quantity,
            'unit_price': unit_price,
            'total_price': item_total
        })
    
    # Handle customer code if provided
    customer_snapshot = None
    customer_id = None
    
    if payload.customer_code:
        customer = resolve_customer_reference(db, payload.customer_code)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with code '{payload.customer_code}' not found"
            )
        customer_id = customer.id
        
        # Create customer snapshot
        customer_snapshot = {
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "phone": customer.phone,
            "address": customer.address,
            "postal_code": customer.postal_code,
            "notes": customer.notes or ""
        }
    else:
        # Create basic snapshot from provided data
        customer_snapshot = {
            "first_name": payload.customer_name.split(' ')[0] if payload.customer_name else "",
            "last_name": ' '.join(payload.customer_name.split(' ')[1:]) if payload.customer_name and ' ' in payload.customer_name else "",
            "phone": payload.contact,
            "address": "",
            "postal_code": "",
            "notes": payload.note or ""
        }

    # Create order
    order = Order(
        order_number=generate_order_number(),
        customer_id=customer_id,
        customer_name=payload.customer_name,
        customer_phone=payload.contact,
        total_amount=total_amount,
        shipping_cost=0.0,  # Default to 0 for draft
        discount_amount=0.0,  # Default to 0 for draft
        final_amount=total_amount,
        status=OrderStatus.DRAFT,
        payment_status=PaymentStatus.PENDING,
        customer_notes=payload.note,
        customer_snapshot=customer_snapshot
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Ensure order has a code
    ensure_order_code(db, order)
    
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


def create_draft_by_skus(db: Session, payload: OrderDraftBySkuIn) -> OrderOut:
    """
    Create a draft order using SKU codes and optional customer code.
    
    Args:
        db: Database session
        payload: Order creation payload with SKU codes
        
    Returns:
        OrderOut: Created order with items
    """
    from services.variant_service import get_variant_by_sku, consume_stock
    
    total_amount = 0
    items_data = []
    
    # Process each SKU item
    for item in payload.items:
        # Get variant by SKU
        variant_data = get_variant_by_sku(db, item.sku_code)
        if not variant_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Variant with SKU '{item.sku_code}' not found"
            )
        
        # Check stock availability
        if variant_data['stock_qty'] < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for SKU '{item.sku_code}'. Available: {variant_data['stock_qty']}, Requested: {item.quantity}"
            )
        
        # Calculate pricing
        unit_price = variant_data['effective_price']
        item_total = unit_price * item.quantity
        total_amount += item_total
        
        # Prepare item data
        items_data.append({
            'product_id': variant_data['product_id'],
            'variant_id': variant_data['id'],
            'product_name': variant_data['product_name'],
            'product_code': variant_data['product_code'],
            'product_price': variant_data['effective_price'],
            'product_image_url': None,  # TODO: Add image URL to variant data
            'sku_code': item.sku_code,
            'variant_attributes_snapshot': variant_data['attributes'],
            'unit_price_snapshot': unit_price,
            'quantity': item.quantity,
            'unit_price': unit_price,
            'total_price': item_total
        })
    
    # Handle customer code if provided
    customer_snapshot = None
    customer_id = None
    
    if payload.customer_code:
        customer = resolve_customer_reference(db, payload.customer_code)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with code '{payload.customer_code}' not found"
            )
        customer_id = customer.id
        
        # Create customer snapshot
        customer_snapshot = {
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "phone": customer.phone,
            "address": customer.address,
            "postal_code": customer.postal_code,
            "notes": customer.notes or ""
        }
    else:
        # Create basic snapshot from provided data
        customer_snapshot = {
            "first_name": payload.customer_name.split(' ')[0] if payload.customer_name else "",
            "last_name": ' '.join(payload.customer_name.split(' ')[1:]) if payload.customer_name and ' ' in payload.customer_name else "",
            "phone": payload.contact,
            "address": "",
            "postal_code": "",
            "notes": payload.note or ""
        }
    
    # Create order
    order = Order(
        order_number=generate_order_number(),
        customer_id=customer_id,
        customer_name=payload.customer_name,
        customer_phone=payload.contact,
        total_amount=total_amount,
        shipping_cost=0.0,
        discount_amount=0.0,
        final_amount=total_amount,
        status=OrderStatus.DRAFT,
        payment_status=PaymentStatus.PENDING,
        customer_notes=payload.note,
        customer_snapshot=customer_snapshot
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Ensure order has a code
    ensure_order_code(db, order)
    
    # Create order items (stock will be consumed when order status changes to "sold")
    for item_data in items_data:
        # Create order item
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
    
    # Handle inventory changes based on status transition
    if new_status_enum == OrderStatus.SOLD and old_status != OrderStatus.SOLD:
        # Decrement inventory when order becomes "sold"
        try:
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
    elif new_status_enum == OrderStatus.CANCELLED and old_status == OrderStatus.SOLD:
        # Restore inventory when order is cancelled after being sold
        try:
            for item in order.items:
                restore_stock(db, item.product_id, item.variant_id, item.quantity)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Inventory restoration failed: {str(e)}"
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


def get_order_by_code(db: Session, order_code: str) -> OrderOut:
    """
    Get order by code with items.
    
    Args:
        db: Database session
        order_code: Order code
        
    Returns:
        OrderOut: Order with items
        
    Raises:
        HTTPException: If order not found
    """
    order = db.query(Order).options(
        joinedload(Order.items)
    ).filter(Order.order_code == order_code).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with code '{order_code}' not found"
        )
    
    return to_order_out(order)


def get_order_by_reference(db: Session, ref: str) -> OrderOut:
    """
    Get order by either ID or code.
    
    Args:
        db: Database session
        ref: Order reference (ID or code)
        
    Returns:
        OrderOut: Order with items
        
    Raises:
        HTTPException: If order not found
    """
    order = resolve_order_reference(db, ref)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{ref}' not found"
        )
    
    # Reload with items
    order = db.query(Order).options(
        joinedload(Order.items)
    ).filter(Order.id == order.id).first()
    
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
            product_code=getattr(item, 'product_code', None) or 'UNKNOWN',
            product_price=item.product_price,
            product_image_url=getattr(item, 'product_image_url', None),
            # New variant fields
            sku_code=getattr(item, 'sku_code', None),
            variant_attributes_snapshot=getattr(item, 'variant_attributes_snapshot', None),
            unit_price_snapshot=getattr(item, 'unit_price_snapshot', None),
            # Legacy variant fields
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
        order_code=getattr(order, 'order_code', None),
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
        customer_snapshot=getattr(order, 'customer_snapshot', None),
        items_count=sum(item.quantity for item in items),
        items=items
    ) 