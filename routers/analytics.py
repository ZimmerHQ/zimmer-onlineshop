from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
from typing import Optional
import logging

from database import get_db
from models import Order, OrderItem, Product, Category, TelegramMessage, TelegramUser

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

        # Total messages in date range (if telegram messages exist)
        total_messages = 0
        try:
            message_filter = and_(TelegramMessage.created_at >= start_dt, TelegramMessage.created_at <= end_dt)
            total_messages = db.query(TelegramMessage).filter(message_filter).count()
        except:
            pass  # Table might not exist yet

        # Calculate message to order ratio
        msg_order_ratio = round(total_messages / max(total_orders, 1), 2)

        # Total customers (unique telegram users up to end date)
        total_customers = 0
        try:
            total_customers = db.query(TelegramUser).filter(TelegramUser.created_at <= end_dt).count()
        except:
            pass  # Table might not exist yet

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