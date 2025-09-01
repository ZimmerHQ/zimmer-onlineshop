from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import Optional, List, Dict, Any
import logging

from database import get_db
from models import TelegramUser, TelegramMessage, Order

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/users")
def list_users(
    query: Optional[str] = Query(None, description="Search by name or username"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get unified list of customers/users (currently Telegram users only).
    Returns paginated results with search support.
    """
    try:
        # Base query for TelegramUser
        base_query = db.query(TelegramUser)

        # Apply search filter if provided
        if query:
            search_filter = or_(
                TelegramUser.first_name.ilike(f"%{query}%"),
                TelegramUser.last_name.ilike(f"%{query}%"),
                TelegramUser.username.ilike(f"%{query}%"),
                TelegramUser.phone.ilike(f"%{query}%")
            )
            base_query = base_query.filter(search_filter)

        # Get total count for pagination
        total_count = base_query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        users = base_query.order_by(desc(TelegramUser.last_seen)).offset(offset).limit(page_size).all()

        # Prepare user data with aggregated info
        user_list = []
        for user in users:
            # Get orders count and total spend (matching by phone if available)
            orders_count = 0
            total_spend = 0.0
            
            if user.phone:
                user_orders = db.query(Order).filter(Order.customer_phone == user.phone).all()
                orders_count = len(user_orders)
                total_spend = sum(order.final_amount for order in user_orders)

            # Combine first and last name
            full_name = " ".join(filter(None, [user.first_name, user.last_name]))
            
            user_data = {
                "id": user.id,
                "name": full_name or user.username or f"کاربر {user.id}",
                "username": user.username,
                "phone": user.phone,
                "last_seen": user.last_seen.isoformat() if user.last_seen else None,
                "visits_count": user.visits_count,
                "channel": "telegram",
                "orders_count": orders_count,
                "total_spend": total_spend
            }
            user_list.append(user_data)

        return {
            "users": user_list,
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "has_more": offset + page_size < total_count
        }

    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(status_code=500, detail="Failed to list users")


@router.get("/users/{user_id}")
def get_user_details(user_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information for a specific user including profile, orders, and messages.
    """
    try:
        # Get user
        user = db.query(TelegramUser).filter(TelegramUser.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Combine first and last name
        full_name = " ".join(filter(None, [user.first_name, user.last_name]))

        # Build profile data
        profile = {
            "id": user.id,
            "telegram_user_id": user.telegram_user_id,
            "name": full_name or user.username or f"کاربر {user.id}",
            "username": user.username,
            "phone": user.phone,
            "address": None,  # Not available in current TelegramUser model
            "last_seen": user.last_seen.isoformat() if user.last_seen else None,
            "visits_count": user.visits_count
        }

        # Get orders (if phone matches)
        orders = []
        if user.phone:
            user_orders = (
                db.query(Order)
                .filter(Order.customer_phone == user.phone)
                .order_by(desc(Order.created_at))
                .limit(20)
                .all()
            )
            
            orders = [
                {
                    "id": order.id,
                    "order_number": order.order_number,
                    "status": order.status.value,
                    "total_amount": order.final_amount,
                    "created_at": order.created_at.isoformat()
                }
                for order in user_orders
            ]

        # Get messages (Telegram only for now)
        user_messages = (
            db.query(TelegramMessage)
            .filter(TelegramMessage.user_id == user_id)
            .order_by(desc(TelegramMessage.created_at))
            .limit(50)
            .all()
        )

        messages = [
            {
                "id": msg.id,
                "direction": msg.direction,
                "text": msg.text,
                "created_at": msg.created_at.isoformat()
            }
            for msg in user_messages
        ]

        return {
            "profile": profile,
            "orders": orders,
            "messages": messages
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user details for {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user details")


@router.patch("/users/{user_id}")
def update_user(
    user_id: int,
    update_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Update CRM fields for a user (phone, note, etc.).
    """
    try:
        # Get user
        user = db.query(TelegramUser).filter(TelegramUser.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update allowed fields
        if "phone" in update_data:
            user.phone = update_data["phone"]
        
        if "note" in update_data:
            user.note = update_data["note"]

        # Note: address field doesn't exist in current TelegramUser model
        # Would need to add it if required

        db.commit()
        db.refresh(user)

        return {"message": "User updated successfully", "user_id": user_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update user") 