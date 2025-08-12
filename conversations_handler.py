import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime
from models import Message, User
from database import get_db
from schemas import ConversationOut, MessageOut

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("/", response_model=List[ConversationOut])
def get_conversations(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all conversations grouped by user"""
    try:
        # Get all users with their message counts and last message info
        conversations_query = db.query(
            User.id.label('user_id'),
            User.chat_id,
            User.username,
            func.count(Message.id).label('message_count'),
            func.max(Message.id).label('last_message_id')
        ).join(Message, User.id == Message.user_id)\
         .group_by(User.id, User.chat_id, User.username)\
         .order_by(desc(func.max(Message.id)))\
         .offset(offset)\
         .limit(limit)
        
        conversations = conversations_query.all()
        
        # Convert to response format
        conversation_list = []
        for conv in conversations:
            # Get the last message for this user
            last_message = db.query(Message).filter(
                Message.user_id == conv.user_id
            ).order_by(desc(Message.id)).first()
            
            # Get all messages for this user (limited to last 50 for performance)
            messages = db.query(Message).filter(
                Message.user_id == conv.user_id
            ).order_by(Message.id.desc()).limit(50).all()
            
            # Convert messages to response format
            message_list = []
            for msg in reversed(messages):  # Reverse to get chronological order
                message_list.append(MessageOut(
                    id=str(msg.id),
                    userId=str(msg.user_id),
                    content=msg.text,
                    timestamp=msg.created_at,
                    isFromUser=msg.role == 'user'
                ))
            
            conversation_list.append(ConversationOut(
                id=str(conv.user_id),
                userId=str(conv.user_id),
                messages=message_list,
                lastMessage=last_message.text if last_message else "",
                lastMessageTime=last_message.created_at if last_message else datetime.utcnow()
            ))
        
        logger.info(f"📚 Retrieved {len(conversation_list)} conversations")
        return conversation_list
        
    except Exception as e:
        logger.error(f"❌ Error fetching conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در دریافت گفتگوها: {str(e)}"
        )


@router.get("/{user_id}/messages", response_model=List[MessageOut])
def get_user_messages(
    user_id: int,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all messages for a specific user"""
    try:
        messages = db.query(Message).filter(
            Message.user_id == user_id
        ).order_by(Message.id.desc()).offset(offset).limit(limit).all()
        
        # Convert to response format
        message_list = []
        for msg in reversed(messages):  # Reverse to get chronological order
            message_list.append(MessageOut(
                id=str(msg.id),
                userId=str(msg.user_id),
                content=msg.text,
                timestamp=msg.created_at,
                isFromUser=msg.role == 'user'
            ))
        
        logger.info(f"📨 Retrieved {len(message_list)} messages for user {user_id}")
        return message_list
        
    except Exception as e:
        logger.error(f"❌ Error fetching messages for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در دریافت پیام‌ها: {str(e)}"
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(user_id: int, db: Session = Depends(get_db)):
    """Delete all messages for a specific user"""
    try:
        # Delete all messages for this user
        deleted_count = db.query(Message).filter(Message.user_id == user_id).delete()
        db.commit()
        
        logger.info(f"🗑️ Deleted {deleted_count} messages for user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error deleting conversation for user {user_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در حذف گفتگو: {str(e)}"
        ) 