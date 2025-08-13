import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime
from models import ChatMessage, User
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
    """Get all conversations grouped by conversation_id"""
    try:
        # Get all conversation_ids with their message counts and last message info
        conversations_query = db.query(
            ChatMessage.conversation_id,
            func.count(ChatMessage.id).label('message_count'),
            func.max(ChatMessage.id).label('last_message_id')
        ).group_by(ChatMessage.conversation_id)\
         .order_by(desc(func.max(ChatMessage.id)))\
         .offset(offset)\
         .limit(limit)
        
        conversations = conversations_query.all()
        
        # Convert to response format
        conversation_list = []
        for conv in conversations:
            # Get the last message for this conversation
            last_message = db.query(ChatMessage).filter(
                ChatMessage.conversation_id == conv.conversation_id
            ).order_by(desc(ChatMessage.id)).first()
            
            # Get all messages for this conversation (limited to last 50 for performance)
            messages = db.query(ChatMessage).filter(
                ChatMessage.conversation_id == conv.conversation_id
            ).order_by(ChatMessage.id.desc()).limit(50).all()
            
            # Convert messages to response format
            message_list = []
            for msg in reversed(messages):  # Reverse to get chronological order
                message_list.append(MessageOut(
                    id=str(msg.id),
                    userId=msg.conversation_id,  # Use conversation_id as userId
                    content=msg.text,
                    timestamp=msg.created_at,
                    isFromUser=msg.role == 'user'
                ))
            
            conversation_list.append(ConversationOut(
                id=conv.conversation_id,
                userId=conv.conversation_id,
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


@router.get("/{conversation_id}/messages", response_model=List[MessageOut])
def get_conversation_messages(
    conversation_id: str,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all messages for a specific conversation"""
    try:
        messages = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.id.desc()).offset(offset).limit(limit).all()
        
        # Convert to response format
        message_list = []
        for msg in reversed(messages):  # Reverse to get chronological order
            message_list.append(MessageOut(
                id=str(msg.id),
                userId=msg.conversation_id,
                content=msg.text,
                timestamp=msg.created_at,
                isFromUser=msg.role == 'user'
            ))
        
        logger.info(f"📝 Retrieved {len(message_list)} messages for conversation {conversation_id}")
        return message_list
        
    except Exception as e:
        logger.error(f"❌ Error fetching messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در دریافت پیام‌ها: {str(e)}"
        )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Delete all messages for a specific conversation"""
    try:
        deleted_count = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).delete()
        
        db.commit()
        logger.info(f"🗑️ Deleted {deleted_count} messages for conversation {conversation_id}")
        return None
        
    except Exception as e:
        logger.error(f"❌ Error deleting conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در حذف گفتگو: {str(e)}"
        ) 