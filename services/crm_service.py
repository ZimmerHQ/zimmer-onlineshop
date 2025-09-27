from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from typing import List, Dict, Any, Optional
from models import Customer, Order, OrderItem, Product
from utils.business_codes import resolve_customer_reference, resolve_order_reference, ensure_customer_code

def upsert_customer(db: Session, *, first_name: str, last_name: str, phone: str, address: str, postal_code: str, notes: str = ""):
    """Create or update a customer by phone number"""
    c = db.query(Customer).filter(Customer.phone == phone).one_or_none()
    if c:
        c.first_name = first_name
        c.last_name = last_name
        c.address = address
        c.postal_code = postal_code
        c.notes = notes
    else:
        c = Customer(
            first_name=first_name, 
            last_name=last_name, 
            phone=phone, 
            address=address, 
            postal_code=postal_code, 
            notes=notes
        )
        db.add(c)
    db.commit()
    db.refresh(c)
    
    # Ensure customer has a code
    ensure_customer_code(db, c)
    
    return c

def update_customer(db: Session, customer_id: int, *, first_name: str = None, last_name: str = None, 
                   phone: str = None, address: str = None, postal_code: str = None, notes: str = None):
    """Update a customer by ID"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return None
    
    # Update only provided fields
    if first_name is not None:
        customer.first_name = first_name
    if last_name is not None:
        customer.last_name = last_name
    if phone is not None:
        customer.phone = phone
    if address is not None:
        customer.address = address
    if postal_code is not None:
        customer.postal_code = postal_code
    if notes is not None:
        customer.notes = notes
    
    db.commit()
    db.refresh(customer)
    
    return customer

def delete_customer(db: Session, customer_id: int):
    """Delete a customer by ID"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return False
    
    # Check if customer has orders by both customer_id and phone
    orders_by_id = db.query(Order).filter(Order.customer_id == customer_id).count()
    orders_by_phone = db.query(Order).filter(Order.customer_phone == customer.phone).count() if customer.phone else 0
    total_orders = orders_by_id + orders_by_phone
    
    if total_orders > 0:
        # Don't delete customers with orders, just mark as inactive or handle differently
        # For now, we'll raise an error
        raise ValueError(f"نمی‌توان مشتری با {total_orders} سفارش را حذف کرد. لطفاً ابتدا سفارشات را مدیریت کنید.")
    
    db.delete(customer)
    db.commit()
    return True

def attach_order(db: Session, *, customer_id: int, order_id: int):
    """Attach an order to a customer and create customer snapshot"""
    o = db.query(Order).filter(Order.id == order_id).one()
    c = db.query(Customer).filter(Customer.id == customer_id).one()
    o.customer_id = c.id
    # Freeze snapshot at this moment
    o.customer_snapshot = {
        "first_name": c.first_name, 
        "last_name": c.last_name, 
        "phone": c.phone,
        "address": c.address, 
        "postal_code": c.postal_code, 
        "notes": c.notes or ""
    }
    db.commit()
    db.refresh(o)
    return {"ok": True}

def list_customers_with_stats(db: Session, limit: int = 200) -> List[Dict[str, Any]]:
    """List customers with their order statistics"""
    rows = (
        db.query(
            Customer.id, 
            Customer.first_name, 
            Customer.last_name, 
            Customer.phone,
            Customer.address,
            Customer.postal_code,
            Customer.notes,
            Customer.customer_code,
            func.COALESCE(func.SUM(Order.final_amount), 0).label("total_spent"),
            func.COUNT(Order.id).label("orders_count"),
            func.MAX(Order.created_at).label("last_order_at"),
        )
        .outerjoin(Order, Order.customer_phone == Customer.phone)
        .group_by(Customer.id, Customer.first_name, Customer.last_name, Customer.phone, Customer.address, Customer.postal_code, Customer.notes, Customer.customer_code)
        .order_by(func.SUM(Order.final_amount).desc().nullslast())
        .limit(limit)
        .all()
    )
    return [dict(r._mapping) for r in rows]

def get_customer_detail(db: Session, customer_id: int) -> Dict[str, Any]:
    """Get detailed customer information with statistics"""
    c = db.query(Customer).filter(Customer.id == customer_id).one()
    stats = list_customers_with_stats(db, limit=10000)
    me = next(s for s in stats if s["id"] == customer_id)
    return {
        "customer": {
            "id": c.id, 
            "first_name": c.first_name, 
            "last_name": c.last_name, 
            "phone": c.phone,
            "address": c.address, 
            "postal_code": c.postal_code, 
            "notes": c.notes or ""
        }, 
        "stats": me
    }

def get_top_customers(db: Session, limit: int = 20) -> List[Dict[str, Any]]:
    """Get top customers by total spending"""
    return list_customers_with_stats(db, limit=limit)

# Unified CRM functions that work for both bot and Telegram
def get_customer_by_phone(db: Session, phone: str) -> Optional[Dict[str, Any]]:
    """Get customer by phone number - used by both bot and Telegram"""
    customer = db.query(Customer).filter(Customer.phone == phone).first()
    if not customer:
            return None
    
    # Get order stats for this customer
    orders = db.query(Order).filter(Order.customer_phone == customer.phone).all()
    total_spent = sum(order.final_amount for order in orders)
    
    return {
        "id": customer.id,
        "customer_code": customer.customer_code,
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "phone": customer.phone,
        "address": customer.address,
        "postal_code": customer.postal_code,
        "notes": customer.notes or "",
        "total_spent": total_spent,
        "orders_count": len(orders),
        "last_order_at": max(order.created_at for order in orders) if orders else None
    }


def get_customer_by_code(db: Session, customer_code: str) -> Optional[Dict[str, Any]]:
    """Get customer by customer code"""
    customer = db.query(Customer).filter(Customer.customer_code == customer_code).first()
    if not customer:
        return None
    
    # Get order stats for this customer
    orders = db.query(Order).filter(Order.customer_phone == customer.phone).all()
    total_spent = sum(order.final_amount for order in orders)
    
    return {
        "id": customer.id,
        "customer_code": customer.customer_code,
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "phone": customer.phone,
        "address": customer.address,
        "postal_code": customer.postal_code,
        "notes": customer.notes or "",
        "total_spent": total_spent,
        "orders_count": len(orders),
        "last_order_at": max(order.created_at for order in orders) if orders else None
    }


def get_customer_by_reference(db: Session, ref: str) -> Optional[Dict[str, Any]]:
    """Get customer by either ID or code"""
    customer = resolve_customer_reference(db, ref)
    if not customer:
        return None
    
    # Get order stats for this customer
    orders = db.query(Order).filter(Order.customer_phone == customer.phone).all()
    total_spent = sum(order.final_amount for order in orders)
    
    return {
        "id": customer.id,
        "customer_code": customer.customer_code,
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "phone": customer.phone,
        "address": customer.address,
        "postal_code": customer.postal_code,
        "notes": customer.notes or "",
        "total_spent": total_spent,
        "orders_count": len(orders),
        "last_order_at": max(order.created_at for order in orders) if orders else None
    }

def get_crm_overview(db: Session) -> Dict[str, Any]:
    """Get unified CRM overview statistics"""
    total_customers = db.query(Customer).count()
    total_orders = db.query(Order).count()
    total_revenue = db.query(func.SUM(Order.final_amount)).scalar() or 0
    
    # Get recent customers (last 30 days)
    from datetime import datetime, timedelta
    recent_cutoff = datetime.utcnow() - timedelta(days=30)
    recent_customers = db.query(Customer).filter(Customer.created_at >= recent_cutoff).count()
    
    # Get top customer
    top_customers = list_customers_with_stats(db, limit=1)
    top_customer = top_customers[0] if top_customers else None
    
    return {
        "total_customers": total_customers,
        "total_orders": total_orders,
        "total_revenue": float(total_revenue),
        "recent_customers": recent_customers,
        "top_customer": top_customer
    }

def get_customer_purchase_history(
    db: Session, 
    customer_id: int, 
    search_query: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """Get detailed purchase history for a customer with search functionality"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise ValueError("Customer not found")
    
    # Base query for orders
    orders_query = db.query(Order).filter(Order.customer_phone == customer.phone)
    
    # Apply search filter if provided
    if search_query:
        # Search in order items through products
        search_filter = or_(
            Order.order_number.ilike(f"%{search_query}%"),
            Order.customer_name.ilike(f"%{search_query}%"),
            Order.customer_phone.ilike(f"%{search_query}%")
        )
        orders_query = orders_query.filter(search_filter)
    
    # Get total count
    total_orders = orders_query.count()
    
    # Get paginated orders
    orders = orders_query.order_by(desc(Order.created_at)).offset(offset).limit(limit).all()
    
    # Get detailed order information with items
    detailed_orders = []
    for order in orders:
        # Get order items with product details
        order_items = (
            db.query(OrderItem, Product)
            .join(Product, OrderItem.product_id == Product.id)
            .filter(OrderItem.order_id == order.id)
            .all()
        )
        
        items = []
        for item, product in order_items:
            items.append({
                "id": item.id,
                "product_id": product.id,
                "product_name": product.name,
                "product_code": product.code,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "total_price": float(item.quantity * item.unit_price),
                "variant_size": item.variant_size,
                "variant_color": item.variant_color
            })
        
        detailed_orders.append({
            "id": order.id,
            "order_number": order.order_number,
            "order_code": order.order_code,
            "status": order.status.value if order.status else "unknown",
            "total_amount": float(order.final_amount),
            "created_at": order.created_at.isoformat(),
            "customer_name": order.customer_name,
            "customer_phone": order.customer_phone,
            "items": items
        })
    
    return {
        "customer": {
            "id": customer.id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "phone": customer.phone
        },
        "orders": detailed_orders,
        "total_orders": total_orders,
        "has_more": offset + limit < total_orders,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": total_orders
        }
    }

def search_customer_orders(
    db: Session,
    search_query: str,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """Search through all customer orders across all customers"""
    # Search in orders and order items
    orders_query = db.query(Order).join(OrderItem, Order.id == OrderItem.order_id).join(Product, OrderItem.product_id == Product.id)
    
    search_filter = or_(
        Order.order_number.ilike(f"%{search_query}%"),
        Order.customer_name.ilike(f"%{search_query}%"),
        Order.customer_phone.ilike(f"%{search_query}%"),
        Product.name.ilike(f"%{search_query}%"),
        Product.code.ilike(f"%{search_query}%")
    )
    
    orders_query = orders_query.filter(search_filter).distinct()
    
    # Get total count
    total_orders = orders_query.count()
    
    # Get paginated orders
    orders = orders_query.order_by(desc(Order.created_at)).offset(offset).limit(limit).all()
    
    # Get detailed order information
    detailed_orders = []
    for order in orders:
        # Get order items with product details
        order_items = (
            db.query(OrderItem, Product)
            .join(Product, OrderItem.product_id == Product.id)
            .filter(OrderItem.order_id == order.id)
            .all()
        )
        
        items = []
        for item, product in order_items:
            items.append({
                "id": item.id,
                "product_id": product.id,
                "product_name": product.name,
                "product_code": product.code,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "total_price": float(item.quantity * item.unit_price),
                "variant_size": item.variant_size,
                "variant_color": item.variant_color
            })
        
        detailed_orders.append({
            "id": order.id,
            "order_number": order.order_number,
            "order_code": order.order_code,
            "status": order.status.value if order.status else "unknown",
            "total_amount": float(order.final_amount),
            "created_at": order.created_at.isoformat(),
            "customer_name": order.customer_name,
            "customer_phone": order.customer_phone,
            "items": items
        })
    
    return {
        "orders": detailed_orders,
        "total_orders": total_orders,
        "has_more": offset + limit < total_orders,
        "search_query": search_query,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": total_orders
        }
    }