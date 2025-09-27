from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from datetime import datetime, timedelta
from typing import Optional, List
import logging

from database import get_db
from models import Order, OrderItem, Product, Category, TelegramMessage, TelegramUser, ChatMessage, Message

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/summary")
def get_analytics_summary(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get analytics summary with optional date range filtering.
    If no dates provided, defaults to last 30 days.
    """
    try:
        # Default to last 30 days if no dates provided
        if not start_date or not end_date:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=30)
        else:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            # Include full end day
            end_dt = end_dt.replace(hour=23, minute=59, second=59)

        # Base filters for date range
        order_filter = and_(Order.created_at >= start_dt, Order.created_at <= end_dt)

        # Total orders and revenue in date range
        total_orders = db.query(Order).filter(order_filter).count()
        total_revenue = db.query(func.sum(Order.final_amount)).filter(order_filter).scalar() or 0.0

        # Total messages in date range (all message types)
        total_messages = 0
        try:
            # Count Telegram messages
            telegram_messages = 0
            try:
                telegram_filter = and_(TelegramMessage.created_at >= start_dt, TelegramMessage.created_at <= end_dt)
                telegram_messages = db.query(TelegramMessage).filter(telegram_filter).count()
            except:
                pass
            
            # Count Chat messages
            chat_messages = 0
            try:
                chat_filter = and_(ChatMessage.created_at >= start_dt, ChatMessage.created_at <= end_dt)
                chat_messages = db.query(ChatMessage).filter(chat_filter).count()
            except:
                pass
            
            # Count general messages
            general_messages = 0
            try:
                message_filter = and_(Message.created_at >= start_dt, Message.created_at <= end_dt)
                general_messages = db.query(Message).filter(message_filter).count()
            except:
                pass
            
            total_messages = telegram_messages + chat_messages + general_messages
        except Exception as e:
            logger.error(f"Error counting messages: {e}")
            pass

        # Calculate message to order ratio
        msg_order_ratio = round(total_messages / max(total_orders, 1), 2)

        # Total customers (unique customers who made purchases in date range)
        total_customers = 0
        try:
            # Count unique customers who made orders in the date range
            unique_customers = db.query(Order.customer_phone).filter(
                and_(
                    order_filter,
                    Order.customer_phone.isnot(None),
                    Order.customer_phone != ''
                )
            ).distinct().count()
            total_customers = unique_customers
        except Exception as e:
            logger.error(f"Error counting customers: {e}")
            pass

        # Top products by sales in date range
        top_products_query = (
            db.query(
                Product.name,
                Product.id.label('product_id'),
                func.sum(OrderItem.quantity).label('sales'),
                func.sum(OrderItem.quantity * OrderItem.unit_price).label('revenue')
            )
            .join(OrderItem, Product.id == OrderItem.product_id)
            .join(Order, OrderItem.order_id == Order.id)
            .filter(order_filter)
            .group_by(Product.id, Product.name)
            .order_by(desc('sales'))
            .limit(5)
            .all()
        )

        top_products = [
            {
                "name": p.name,
                "product_id": p.product_id,
                "sales": int(p.sales),
                "revenue": float(p.revenue)
            }
            for p in top_products_query
        ]

        # Top categories by sales in date range
        top_categories_query = (
            db.query(
                Category.name,
                Category.id.label('category_id'),
                func.sum(OrderItem.quantity).label('sales'),
                func.sum(OrderItem.quantity * OrderItem.unit_price).label('revenue')
            )
            .join(Product, Category.id == Product.category_id)
            .join(OrderItem, Product.id == OrderItem.product_id)
            .join(Order, OrderItem.order_id == Order.id)
            .filter(order_filter)
            .group_by(Category.id, Category.name)
            .order_by(desc('sales'))
            .limit(5)
            .all()
        )

        top_categories = [
            {
                "name": c.name,
                "category_id": c.category_id,
                "sales": int(c.sales),
                "revenue": float(c.revenue)
            }
            for c in top_categories_query
        ]

        # Recent activity in date range
        recent_orders = (
            db.query(Order)
            .filter(order_filter)
            .order_by(desc(Order.created_at))
            .limit(5)
            .all()
        )

        recent_activity = []
        
        # Add recent orders
        for order in recent_orders:
            activity = {
                "type": "order",
                "title": f"سفارش جدید از {order.customer_name}",
                "time_ago": _time_ago(order.created_at)
            }
            recent_activity.append(activity)

        return {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "total_messages": total_messages, 
            "total_customers": total_customers,
            "msg_order_ratio": msg_order_ratio,
            "top_products": top_products,
            "top_categories": top_categories,
            "recent_activity": recent_activity
        }

    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics summary")


@router.get("/products/search")
def search_product_analytics(
    q: str = Query(..., description="Search query for product name or code"),
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    db: Session = Depends(get_db)
):
    """
    Search for products and get their sales analytics.
    """
    try:
        # Default to last 30 days if no dates provided
        if not start_date or not end_date:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=30)
        else:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            # Include full end day
            end_dt = end_dt.replace(hour=23, minute=59, second=59)

        # Base filters for date range
        order_filter = and_(Order.created_at >= start_dt, Order.created_at <= end_dt)

        # Search for products by name or code
        search_filter = or_(
            Product.name.ilike(f"%{q}%"),
            Product.code.ilike(f"%{q}%")
        )

        # Get product sales analytics
        products_query = (
            db.query(
                Product.id,
                Product.name,
                Product.code,
                Product.price,
                Product.stock,
                Product.category_id,
                Category.name.label('category_name'),
                func.sum(OrderItem.quantity).label('total_sold'),
                func.sum(OrderItem.quantity * OrderItem.unit_price).label('total_revenue'),
                func.count(Order.id.distinct()).label('order_count'),
                func.max(Order.created_at).label('last_sale_date')
            )
            .outerjoin(OrderItem, Product.id == OrderItem.product_id)
            .outerjoin(Order, and_(OrderItem.order_id == Order.id, order_filter))
            .outerjoin(Category, Product.category_id == Category.id)
            .filter(search_filter)
            .group_by(
                Product.id, 
                Product.name, 
                Product.code, 
                Product.price, 
                Product.stock, 
                Product.category_id,
                Category.name
            )
            .order_by(desc('total_sold'))
            .limit(limit)
            .all()
        )

        products = []
        for p in products_query:
            product_data = {
                "id": p.id,
                "name": p.name,
                "code": p.code,
                "price": float(p.price) if p.price else 0.0,
                "stock": p.stock or 0,
                "category_id": p.category_id,
                "category_name": p.category_name or "بدون دسته‌بندی",
                "total_sold": int(p.total_sold) if p.total_sold else 0,
                "total_revenue": float(p.total_revenue) if p.total_revenue else 0.0,
                "order_count": int(p.order_count) if p.order_count else 0,
                "last_sale_date": p.last_sale_date.isoformat() if p.last_sale_date else None,
                "avg_price_sold": float(p.total_revenue / p.total_sold) if p.total_sold and p.total_sold > 0 else 0.0
            }
            products.append(product_data)

        return {
            "products": products,
            "total_found": len(products),
            "search_query": q,
            "date_range": {
                "start_date": start_dt.isoformat(),
                "end_date": end_dt.isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error searching product analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to search product analytics")


@router.get("/products/{product_id}/details")
def get_product_analytics_details(
    product_id: int,
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get detailed analytics for a specific product.
    """
    try:
        # Default to last 30 days if no dates provided
        if not start_date or not end_date:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=30)
        else:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            # Include full end day
            end_dt = end_dt.replace(hour=23, minute=59, second=59)

        # Base filters for date range
        order_filter = and_(Order.created_at >= start_dt, Order.created_at <= end_dt)

        # Get product details
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Get sales analytics
        sales_data = (
            db.query(
                func.sum(OrderItem.quantity).label('total_sold'),
                func.sum(OrderItem.quantity * OrderItem.unit_price).label('total_revenue'),
                func.count(Order.id.distinct()).label('order_count'),
                func.avg(OrderItem.unit_price).label('avg_sale_price'),
                func.min(OrderItem.unit_price).label('min_sale_price'),
                func.max(OrderItem.unit_price).label('max_sale_price')
            )
            .join(Order, OrderItem.order_id == Order.id)
            .filter(
                and_(
                    OrderItem.product_id == product_id,
                    order_filter
                )
            )
            .first()
        )

        # Get daily sales breakdown
        daily_sales = (
            db.query(
                func.date(Order.created_at).label('sale_date'),
                func.sum(OrderItem.quantity).label('daily_sold'),
                func.sum(OrderItem.quantity * OrderItem.unit_price).label('daily_revenue')
            )
            .join(Order, OrderItem.order_id == Order.id)
            .filter(
                and_(
                    OrderItem.product_id == product_id,
                    order_filter
                )
            )
            .group_by(func.date(Order.created_at))
            .order_by(func.date(Order.created_at))
            .all()
        )

        # Get recent orders containing this product
        recent_orders = (
            db.query(Order, OrderItem.quantity, OrderItem.unit_price)
            .join(OrderItem, Order.id == OrderItem.order_id)
            .filter(
                and_(
                    OrderItem.product_id == product_id,
                    order_filter
                )
            )
            .order_by(desc(Order.created_at))
            .limit(10)
            .all()
        )

        return {
            "product": {
                "id": product.id,
                "name": product.name,
                "code": product.code,
                "price": float(product.price) if product.price else 0.0,
                "stock": product.stock or 0,
                "category_id": product.category_id
            },
            "analytics": {
                "total_sold": int(sales_data.total_sold) if sales_data.total_sold else 0,
                "total_revenue": float(sales_data.total_revenue) if sales_data.total_revenue else 0.0,
                "order_count": int(sales_data.order_count) if sales_data.order_count else 0,
                "avg_sale_price": float(sales_data.avg_sale_price) if sales_data.avg_sale_price else 0.0,
                "min_sale_price": float(sales_data.min_sale_price) if sales_data.min_sale_price else 0.0,
                "max_sale_price": float(sales_data.max_sale_price) if sales_data.max_sale_price else 0.0
            },
            "daily_sales": [
                {
                    "date": str(ds.sale_date),
                    "sold": int(ds.daily_sold),
                    "revenue": float(ds.daily_revenue)
                }
                for ds in daily_sales
            ],
            "recent_orders": [
                {
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "customer_name": order.customer_name,
                    "quantity": int(quantity),
                    "unit_price": float(unit_price),
                    "total_price": float(quantity * unit_price),
                    "created_at": order.created_at.isoformat()
                }
                for order, quantity, unit_price in recent_orders
            ],
            "date_range": {
                "start_date": start_dt.isoformat(),
                "end_date": end_dt.isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product analytics details: {e}")
        raise HTTPException(status_code=500, detail="Failed to get product analytics details")


def _time_ago(dt: datetime) -> str:
    """Helper to calculate time ago string"""
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} روز پیش"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} ساعت پیش"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} دقیقه پیش"
    else:
        return "اکنون" 