import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from models import Order, OrderItem, Product, OrderStatus, PaymentStatus
from database import get_db
from schemas import OrderCreate, OrderUpdate, OrderOut, OrderSummary, OrderItemOut, OrderItemCreate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/orders", tags=["orders"])


def generate_order_number() -> str:
    """Generate a unique order number in format ORD-YYYY-NNNN"""
    from datetime import datetime
    year = datetime.now().year
    # In a real app, you'd get the next number from database
    # For now, we'll use timestamp-based approach
    import time
    timestamp = int(time.time() * 1000) % 10000
    return f"ORD-{year}-{timestamp:04d}"


def calculate_order_totals(items: List[OrderItemCreate], db: Session) -> tuple[float, List[OrderItem]]:
    """Calculate order totals and create order items"""
    total_amount = 0.0
    order_items = []
    
    for item_data in items:
        # Get product details
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item_data.product_id} not found"
            )
        
        # Check stock availability
        if product.stock is not None and product.stock < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product {product.name}. Available: {product.stock}, Requested: {item_data.quantity}"
            )
        
        # Calculate item total
        unit_price = product.price
        item_total = unit_price * item_data.quantity
        total_amount += item_total
        
        # Create order item
        order_item = OrderItem(
            product_id=product.id,
            product_name=product.name,
            product_price=product.price,
            product_image_url=product.image_url,
            quantity=item_data.quantity,
            size=item_data.size,
            unit_price=unit_price,
            total_price=item_total
        )
        order_items.append(order_item)
    
    return total_amount, order_items


@router.get("/", response_model=List[OrderSummary])
def get_orders(
    status_filter: Optional[OrderStatus] = None,
    payment_status_filter: Optional[PaymentStatus] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all orders with optional filtering"""
    query = db.query(Order)
    
    if status_filter:
        query = query.filter(Order.status == status_filter)
    
    if payment_status_filter:
        query = query.filter(Order.payment_status == payment_status_filter)
    
    orders = query.order_by(Order.created_at.desc()).offset(offset).limit(limit).all()
    
    # Convert to summary format
    order_summaries = []
    for order in orders:
        items_count = len(order.items)
        summary = OrderSummary(
            id=order.id,
            order_number=order.order_number,
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            final_amount=order.final_amount,
            status=order.status,
            payment_status=order.payment_status,
            created_at=order.created_at,
            items_count=items_count
        )
        order_summaries.append(summary)
    
    return order_summaries


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get a specific order by ID"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order


@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order"""
    logger.info(f"📥 New order received from: {order_data.customer_name}")
    
    try:
        # Calculate totals and create order items
        total_amount, order_items = calculate_order_totals(order_data.items, db)
        
        # Calculate final amount
        final_amount = total_amount + order_data.shipping_cost - order_data.discount_amount
        
        # Create order
        order = Order(
            order_number=generate_order_number(),
            customer_name=order_data.customer_name,
            customer_phone=order_data.customer_phone,
            customer_address=order_data.customer_address,
            customer_instagram=order_data.customer_instagram,
            total_amount=total_amount,
            shipping_cost=order_data.shipping_cost,
            discount_amount=order_data.discount_amount,
            final_amount=final_amount,
            payment_method=order_data.payment_method,
            shipping_method=order_data.shipping_method,
            customer_notes=order_data.customer_notes,
            status=OrderStatus.PENDING,
            payment_status=PaymentStatus.PENDING
        )
        
        # Add order items
        order.items = order_items
        
        # Save to database
        db.add(order)
        db.commit()
        db.refresh(order)
        
        logger.info(f"✅ Order created with ID: {order.id}, Order Number: {order.order_number}")
        
        # Update product stock
        for item in order_items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product and product.stock is not None:
                old_stock = product.stock
                product.stock = old_stock - item.quantity
                logger.info(f"📦 Updated stock for product {product.name}: {old_stock} -> {product.stock}")
        
        db.commit()
        
        return order
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Order creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"خطا در ایجاد سفارش: {str(e)}"
        )


@router.patch("/{order_id}", response_model=OrderOut)
def update_order(order_id: int, order_update: OrderUpdate, db: Session = Depends(get_db)):
    """Update order status and details"""
    logger.info(f"📝 Updating order with ID: {order_id}")
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update fields
    update_data = order_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "status" and value:
            # Update status-specific timestamps
            if value == OrderStatus.CONFIRMED and not order.confirmed_at:
                order.confirmed_at = datetime.utcnow()
            elif value == OrderStatus.SHIPPED and not order.shipped_at:
                order.shipped_at = datetime.utcnow()
            elif value == OrderStatus.DELIVERED and not order.delivered_at:
                order.delivered_at = datetime.utcnow()
        
        setattr(order, field, value)
        logger.info(f"✅ Updated {field}: {value}")
    
    # Update the updated_at timestamp
    order.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    
    logger.info(f"✅ Order {order_id} updated successfully")
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """Delete an order (soft delete by setting status to cancelled)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Soft delete by setting status to cancelled
    order.status = OrderStatus.CANCELLED
    order.updated_at = datetime.utcnow()
    
    # Restore product stock
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product and product.stock is not None:
            product.stock += item.quantity
            logger.info(f"📦 Restored stock for product {product.name}: {product.stock - item.quantity} -> {product.stock}")
    
    db.commit()
    logger.info(f"✅ Order {order_id} cancelled successfully")
    return None


@router.get("/{order_id}/items", response_model=List[OrderItemOut])
def get_order_items(order_id: int, db: Session = Depends(get_db)):
    """Get items for a specific order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order.items


# Simple order creation for chat system
def create_simple_order(product_id: int, size: str, color: str, qty: int = 1, meta: dict = None) -> dict:
    """
    Create a simple order for the chat system.
    
    Args:
        product_id: Product ID
        size: Size (e.g., "43")
        color: Color (e.g., "مشکی")
        qty: Quantity (default 1)
        meta: Additional metadata
        
    Returns:
        dict: Order information
    """
    try:
        from database import SessionLocal
        
        db = SessionLocal()
        try:
            # Get product details
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise Exception(f"Product with ID {product_id} not found")
            
            # Create a simple order (using existing Order model)
            order = Order(
                order_number=generate_order_number(),
                customer_name="Chat User",  # Default for chat orders
                customer_phone="Chat",      # Default for chat orders
                total_amount=product.price * qty,
                shipping_cost=0.0,
                discount_amount=0.0,
                final_amount=product.price * qty,
                status=OrderStatus.PENDING,
                payment_status=PaymentStatus.PENDING,
                admin_notes=f"Chat order - Size: {size}, Color: {color}, Meta: {meta}"
            )
            
            db.add(order)
            db.commit()
            db.refresh(order)
            
            # Create order item
            order_item = OrderItem(
                order_id=order.id,
                product_id=product_id,
                product_name=product.name,
                product_price=product.price,
                product_image_url=product.image_url,
                quantity=qty,
                size=size,
                unit_price=product.price,
                total_price=product.price * qty
            )
            
            db.add(order_item)
            db.commit()
            
            order_info = {
                "id": order.id,
                "order_number": order.order_number,
                "product_id": product_id,
                "size": size,
                "color": color,
                "quantity": qty,
                "status": order.status.value,
                "created_at": order.created_at.isoformat(),
                "meta": meta or {}
            }
            
            logger.info(f"✅ Simple order created: id={order.id}, order_number={order.order_number}")
            return order_info
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"❌ Simple order creation failed: {str(e)}")
        raise Exception(f"خطا در ایجاد سفارش: {str(e)}")


# Statistics endpoints
@router.get("/stats/summary")
def get_order_stats(db: Session = Depends(get_db)):
    """Get order statistics"""
    total_orders = db.query(Order).count()
    pending_orders = db.query(Order).filter(Order.status == OrderStatus.PENDING).count()
    confirmed_orders = db.query(Order).filter(Order.status == OrderStatus.CONFIRMED).count()
    shipped_orders = db.query(Order).filter(Order.status == OrderStatus.SHIPPED).count()
    delivered_orders = db.query(Order).filter(Order.status == OrderStatus.DELIVERED).count()
    
    # Calculate total revenue
    total_revenue = db.query(Order).filter(Order.status == OrderStatus.DELIVERED).with_entities(
        db.func.sum(Order.final_amount)
    ).scalar() or 0.0
    
    return {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "confirmed_orders": confirmed_orders,
        "shipped_orders": shipped_orders,
        "delivered_orders": delivered_orders,
        "total_revenue": total_revenue
    }
