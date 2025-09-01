import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from models import TelegramUser, TelegramMessage
from models import Order

logger = logging.getLogger(__name__)


class CRMService:
    def __init__(self, db: Session):
        self.db = db
    
    def list_interactions(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """List CRM interactions with optional filtering"""
        try:
            # Base query for interactions
            query = self.db.query(
                TelegramMessage.id,
                TelegramMessage.direction,
                TelegramMessage.text,
                TelegramMessage.created_at,
                TelegramUser.telegram_user_id,
                TelegramUser.username,
                TelegramUser.first_name,
                TelegramUser.last_name,
                TelegramUser.phone,
                TelegramUser.visits_count
            ).join(TelegramUser, TelegramMessage.user_id == TelegramUser.id)
            
            # Apply filters
            if filters:
                if filters.get('user_id'):
                    query = query.filter(TelegramUser.id == filters['user_id'])
                
                if filters.get('telegram_user_id'):
                    query = query.filter(TelegramUser.telegram_user_id == filters['telegram_user_id'])
                
                if filters.get('direction'):
                    query = query.filter(TelegramMessage.direction == filters['direction'])
                
                if filters.get('has_phone'):
                    if filters['has_phone']:
                        query = query.filter(TelegramUser.phone.isnot(None))
                    else:
                        query = query.filter(TelegramUser.phone.is_(None))
                
                if filters.get('has_orders'):
                    # Subquery to find users with orders
                    users_with_orders = self.db.query(Order.customer_phone).distinct()
                    if filters['has_orders']:
                        query = query.filter(TelegramUser.phone.in_(users_with_orders))
                    else:
                        query = query.filter(~TelegramUser.phone.in_(users_with_orders))
                
                if filters.get('date_from'):
                    query = query.filter(TelegramMessage.created_at >= filters['date_from'])
                
                if filters.get('date_to'):
                    query = query.filter(TelegramMessage.created_at <= filters['date_to'])
                
                if filters.get('search_text'):
                    search_term = f"%{filters['search_text']}%"
                    query = query.filter(TelegramMessage.text.ilike(search_term))
            
            # Order by most recent first
            query = query.order_by(desc(TelegramMessage.created_at))
            
            # Apply pagination
            if filters and filters.get('limit'):
                query = query.limit(filters['limit'])
            
            if filters and filters.get('offset'):
                query = query.offset(filters['offset'])
            
            # Execute query and format results
            results = query.all()
            
            interactions = []
            for result in results:
                interactions.append({
                    'id': result.id,
                    'direction': result.direction,
                    'text': result.text,
                    'created_at': result.created_at,
                    'user': {
                        'telegram_user_id': result.telegram_user_id,
                        'username': result.username,
                        'first_name': result.first_name,
                        'last_name': result.last_name,
                        'phone': result.phone,
                        'visits_count': result.visits_count
                    }
                })
            
            logger.info(f"Retrieved {len(interactions)} interactions with filters: {filters}")
            return interactions
            
        except Exception as e:
            logger.error(f"Error listing interactions: {e}")
            return []
    
    def get_user_interactions(self, user_id: int, limit: int = 50) -> List[TelegramMessage]:
        """Get all interactions for a specific user"""
        try:
            messages = self.db.query(TelegramMessage).filter(
                TelegramMessage.user_id == user_id
            ).order_by(desc(TelegramMessage.created_at)).limit(limit).all()
            
            logger.info(f"Retrieved {len(messages)} interactions for user {user_id}")
            return messages
            
        except Exception as e:
            logger.error(f"Error getting user interactions for {user_id}: {e}")
            return []
    
    def get_user_summary(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get comprehensive summary for a user"""
        try:
            user = self.db.query(TelegramUser).filter(TelegramUser.id == user_id).first()
            if not user:
                return None
            
            # Get message counts
            inbound_count = self.db.query(TelegramMessage).filter(
                and_(
                    TelegramMessage.user_id == user_id,
                    TelegramMessage.direction == 'in'
                )
            ).count()
            
            outbound_count = self.db.query(TelegramMessage).filter(
                and_(
                    TelegramMessage.user_id == user_id,
                    TelegramMessage.direction == 'out'
                )
            ).count()
            
            # Get order information if phone exists
            orders_info = None
            if user.phone:
                orders = self.db.query(Order).filter(
                    Order.customer_phone == user.phone
                ).all()
                
                if orders:
                    total_spent = sum(order.final_amount for order in orders)
                    order_statuses = {}
                    for order in orders:
                        status = order.status.value if hasattr(order.status, 'value') else str(order.status)
                        order_statuses[status] = order_statuses.get(status, 0) + 1
                    
                    orders_info = {
                        'total_orders': len(orders),
                        'total_spent': total_spent,
                        'avg_order_value': total_spent / len(orders) if orders else 0,
                        'statuses': order_statuses,
                        'last_order': max(order.created_at for order in orders) if orders else None
                    }
            
            # Get recent activity
            recent_messages = self.db.query(TelegramMessage).filter(
                TelegramMessage.user_id == user_id
            ).order_by(desc(TelegramMessage.created_at)).limit(5).all()
            
            summary = {
                'user': {
                    'id': user.id,
                    'telegram_user_id': user.telegram_user_id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': user.phone,
                    'note': user.note,
                    'first_seen': user.first_seen,
                    'last_seen': user.last_seen,
                    'visits_count': user.visits_count,
                    'is_blocked': user.is_blocked
                },
                'interactions': {
                    'total_inbound': inbound_count,
                    'total_outbound': outbound_count,
                    'total_messages': inbound_count + outbound_count
                },
                'orders': orders_info,
                'recent_activity': [
                    {
                        'direction': msg.direction,
                        'text': msg.text[:100] + '...' if len(msg.text) > 100 else msg.text,
                        'created_at': msg.created_at
                    }
                    for msg in recent_messages
                ]
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting user summary for {user_id}: {e}")
            return None
    
    def add_contact_info(self, user_id: int, phone: Optional[str] = None, note: Optional[str] = None) -> bool:
        """Add or update contact information for a user"""
        try:
            user = self.db.query(TelegramUser).filter(TelegramUser.id == user_id).first()
            if not user:
                return False
            
            if phone is not None:
                user.phone = phone
            if note is not None:
                user.note = note
            
            user.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Updated contact info for user {user_id}: phone={phone}, note={note}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating contact info for user {user_id}: {e}")
            return False
    
    def block_user(self, user_id: int, reason: Optional[str] = None) -> bool:
        """Block a user from using the bot"""
        try:
            user = self.db.query(TelegramUser).filter(TelegramUser.id == user_id).first()
            if not user:
                return False
            
            user.is_blocked = True
            if reason:
                user.note = f"BLOCKED: {reason}" + (f"\n{user.note}" if user.note else "")
            
            user.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Blocked user {user_id}, reason: {reason}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error blocking user {user_id}: {e}")
            return False
    
    def unblock_user(self, user_id: int) -> bool:
        """Unblock a user"""
        try:
            user = self.db.query(TelegramUser).filter(TelegramUser.id == user_id).first()
            if not user:
                return False
            
            user.is_blocked = True
            user.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Unblocked user {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error unblocking user {user_id}: {e}")
            return False
    
    def get_crm_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get CRM statistics for the last N days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # User statistics
            total_users = self.db.query(TelegramUser).count()
            new_users = self.db.query(TelegramUser).filter(
                TelegramUser.created_at >= cutoff_date
            ).count()
            active_users = self.db.query(TelegramUser).filter(
                TelegramUser.last_seen >= cutoff_date
            ).count()
            blocked_users = self.db.query(TelegramUser).filter(
                TelegramUser.is_blocked == True
            ).count()
            
            # Message statistics
            total_messages = self.db.query(TelegramMessage).filter(
                TelegramMessage.created_at >= cutoff_date
            ).count()
            
            inbound_messages = self.db.query(TelegramMessage).filter(
                and_(
                    TelegramMessage.created_at >= cutoff_date,
                    TelegramMessage.direction == 'in'
                )
            ).count()
            
            outbound_messages = self.db.query(TelegramMessage).filter(
                and_(
                    TelegramMessage.created_at >= cutoff_date,
                    TelegramMessage.direction == 'out'
                )
            ).count()
            
            # Users with phone numbers
            users_with_phone = self.db.query(TelegramUser).filter(
                TelegramUser.phone.isnot(None)
            ).count()
            
            # Users with orders
            users_with_orders = self.db.query(TelegramUser).filter(
                and_(
                    TelegramUser.phone.isnot(None),
                    self.db.query(Order).filter(Order.customer_phone == TelegramUser.phone).exists()
                )
            ).count()
            
            stats = {
                'period_days': days,
                'users': {
                    'total': total_users,
                    'new': new_users,
                    'active': active_users,
                    'blocked': blocked_users,
                    'with_phone': users_with_phone,
                    'with_orders': users_with_orders
                },
                'messages': {
                    'total': total_messages,
                    'inbound': inbound_messages,
                    'outbound': outbound_messages,
                    'avg_per_user': total_messages / active_users if active_users > 0 else 0
                },
                'engagement': {
                    'phone_conversion_rate': (users_with_phone / total_users * 100) if total_users > 0 else 0,
                    'order_conversion_rate': (users_with_orders / total_users * 100) if total_users > 0 else 0
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting CRM stats: {e}")
            return {} 