from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import Optional, List, Dict, Any
import logging

from database import get_db
from models import TelegramUser, TelegramMessage, Order, ChatMessage, Customer

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
def get_conversations(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get list of conversations (currently returns empty as we don't have conversation management yet).
    This endpoint exists to prevent 404 errors from frontend calls.
    """
    try:
        return {
            "conversations": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "has_more": False
        }
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversations")


@router.get("/users")
def list_users(
    query: Optional[str] = Query(None, description="Search by name or username"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get unified list of customers/users from both Telegram users and CRM customers.
    Returns paginated results with search support.
    """
    try:
        user_list = []
        
        # Get Telegram users
        telegram_query = db.query(TelegramUser)
        if query:
            telegram_filter = or_(
                TelegramUser.first_name.ilike(f"%{query}%"),
                TelegramUser.last_name.ilike(f"%{query}%"),
                TelegramUser.username.ilike(f"%{query}%"),
                TelegramUser.phone.ilike(f"%{query}%")
            )
            telegram_query = telegram_query.filter(telegram_filter)
        
        telegram_users = telegram_query.all()
        
        for user in telegram_users:
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
                "id": f"tg_{user.id}",
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
        
        # Get CRM customers
        crm_query = db.query(Customer)
        if query:
            crm_filter = or_(
                Customer.first_name.ilike(f"%{query}%"),
                Customer.last_name.ilike(f"%{query}%"),
                Customer.phone.ilike(f"%{query}%")
            )
            crm_query = crm_query.filter(crm_filter)
        
        crm_customers = crm_query.all()
        
        for customer in crm_customers:
            # Get orders count and total spend
            orders_count = 0
            total_spend = 0.0
            
            if customer.phone:
                user_orders = db.query(Order).filter(Order.customer_phone == customer.phone).all()
                orders_count = len(user_orders)
                total_spend = sum(order.final_amount for order in user_orders)

            # Combine first and last name
            full_name = " ".join(filter(None, [customer.first_name, customer.last_name]))
            
            user_data = {
                "id": f"crm_{customer.id}",
                "name": full_name or f"مشتری {customer.id}",
                "username": None,
                "phone": customer.phone,
                "last_seen": customer.created_at.isoformat() if customer.created_at else None,
                "visits_count": 0,
                "channel": "crm",
                "orders_count": orders_count,
                "total_spend": total_spend
            }
            user_list.append(user_data)
        
        # Sort by total spend descending, then by name
        user_list.sort(key=lambda x: (-x["total_spend"], x["name"]))
        
        # Apply pagination
        total_count = len(user_list)
        offset = (page - 1) * page_size
        paginated_users = user_list[offset:offset + page_size]

        return {
            "users": paginated_users,
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "has_more": offset + page_size < total_count
        }

    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(status_code=500, detail="Failed to list users")


@router.get("/users/{user_id}")
def get_user_details(user_id: str, db: Session = Depends(get_db)):
    """
    Get detailed information for a specific user including profile, orders, and messages.
    Handles both Telegram users (tg_*) and CRM customers (crm_*).
    """
    try:
        # Parse user ID to determine type
        if user_id.startswith("tg_"):
            # Telegram user
            telegram_id = int(user_id[3:])  # Remove "tg_" prefix
            user = db.query(TelegramUser).filter(TelegramUser.id == telegram_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="Telegram user not found")
            
            # Combine first and last name
            full_name = " ".join(filter(None, [user.first_name, user.last_name]))
            
            # Build profile data
            profile = {
                "id": f"tg_{user.id}",
                "telegram_user_id": user.telegram_user_id,
                "name": full_name or user.username or f"کاربر {user.id}",
                "username": user.username,
                "phone": user.phone,
                "address": None,  # Not available in current TelegramUser model
                "last_seen": user.last_seen.isoformat() if user.last_seen else None,
                "visits_count": user.visits_count,
                "channel": "telegram"
            }
            
        elif user_id.startswith("crm_"):
            # CRM customer
            customer_id = int(user_id[4:])  # Remove "crm_" prefix
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                raise HTTPException(status_code=404, detail="CRM customer not found")
            
            # Combine first and last name
            full_name = " ".join(filter(None, [customer.first_name, customer.last_name]))
            
            # Build profile data
            profile = {
                "id": f"crm_{customer.id}",
                "telegram_user_id": None,
                "name": full_name or f"مشتری {customer.id}",
                "username": None,
                "phone": customer.phone,
                "address": customer.address,
                "last_seen": customer.created_at.isoformat() if customer.created_at else None,
                "visits_count": 0,
                "channel": "crm"
            }
            
        else:
            raise HTTPException(status_code=400, detail="Invalid user ID format")

        # Get orders (if phone matches)
        orders = []
        phone_number = None
        
        if user_id.startswith("tg_"):
            phone_number = user.phone
        elif user_id.startswith("crm_"):
            phone_number = customer.phone
            
        if phone_number:
            user_orders = (
                db.query(Order)
                .filter(Order.customer_phone == phone_number)
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
        messages = []
        if user_id.startswith("tg_"):
            telegram_user_id = user.telegram_user_id
            if telegram_user_id:
                user_messages = (
                    db.query(TelegramMessage)
                    .filter(TelegramMessage.user_id == telegram_user_id)
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
    user_id: str,
    update_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Update CRM fields for a user (phone, note, etc.).
    Handles both Telegram users (tg_*) and CRM customers (crm_*).
    """
    try:
        # Parse user ID to determine type
        if user_id.startswith("tg_"):
            # Telegram user
            telegram_id = int(user_id[3:])  # Remove "tg_" prefix
            user = db.query(TelegramUser).filter(TelegramUser.id == telegram_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="Telegram user not found")
            
            # Update allowed fields
            if "phone" in update_data:
                user.phone = update_data["phone"]
                
        elif user_id.startswith("crm_"):
            # CRM customer
            customer_id = int(user_id[4:])  # Remove "crm_" prefix
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                raise HTTPException(status_code=404, detail="CRM customer not found")
            
            # Update allowed fields
            if "phone" in update_data:
                customer.phone = update_data["phone"]
            if "address" in update_data:
                customer.address = update_data["address"]
            if "first_name" in update_data:
                customer.first_name = update_data["first_name"]
            if "last_name" in update_data:
                customer.last_name = update_data["last_name"]
                
        else:
            raise HTTPException(status_code=400, detail="Invalid user ID format")
        
        # Handle note field for both user types
        if "note" in update_data:
            if user_id.startswith("tg_"):
                # Note field doesn't exist in TelegramUser model, skip for now
                pass
            elif user_id.startswith("crm_"):
                # Add note field to Customer model if needed
                pass

        db.commit()
        
        # Refresh the appropriate object
        if user_id.startswith("tg_"):
            db.refresh(user)
        elif user_id.startswith("crm_"):
            db.refresh(customer)

        return {"message": "User updated successfully", "user_id": user_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update user")


@router.get("/messages")
def get_conversation_messages(
    conversation_id: str = Query("default", description="Conversation ID to retrieve messages for"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Messages per page"),
    db: Session = Depends(get_db)
):
    """
    Get chronological messages for a conversation.
    Returns paginated chat messages ordered by creation time.
    """
    try:
        # Base query for ChatMessage
        base_query = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        )

        # Get total count for pagination
        total_count = base_query.count()

        # Apply pagination and ordering (chronological)
        offset = (page - 1) * page_size
        messages = base_query.order_by(ChatMessage.created_at).offset(offset).limit(page_size).all()

        # Format messages
        message_list = [
            {
                "id": msg.id,
                "role": msg.role,
                "text": msg.text,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]

        return {
            "messages": message_list,
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "has_more": offset + page_size < total_count,
            "conversation_id": conversation_id
        }

    except Exception as e:
        logger.error(f"Error getting conversation messages for {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversation messages") 