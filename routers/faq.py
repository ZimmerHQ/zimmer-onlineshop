from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
import logging

from database import get_db
from models import FAQ
from schemas.telegram import FAQCreate, FAQUpdate, FAQOut

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[FAQOut])
def list_faqs(
    active_only: bool = True,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of FAQ entries"""
    try:
        query = db.query(FAQ)
        
        if active_only:
            query = query.filter(FAQ.is_active == True)
        
        faqs = query.order_by(FAQ.updated_at.desc()).limit(limit).all()
        return faqs
        
    except Exception as e:
        logger.error(f"Error listing FAQs: {e}")
        raise HTTPException(status_code=500, detail="Failed to list FAQs")


@router.post("/", response_model=FAQOut)
def create_faq(faq: FAQCreate, db: Session = Depends(get_db)):
    """Create a new FAQ entry"""
    try:
        db_faq = FAQ(
            question=faq.question,
            answer=faq.answer,
            tags=faq.tags,
            is_active=faq.is_active
        )
        
        db.add(db_faq)
        db.commit()
        db.refresh(db_faq)
        
        logger.info(f"Created FAQ: {db_faq.id}")
        return db_faq
        
    except Exception as e:
        logger.error(f"Error creating FAQ: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create FAQ")


@router.get("/{faq_id}", response_model=FAQOut)
def get_faq(faq_id: int, db: Session = Depends(get_db)):
    """Get a specific FAQ entry"""
    try:
        faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
        if not faq:
            raise HTTPException(status_code=404, detail="FAQ not found")
        
        return faq
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting FAQ {faq_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get FAQ")


@router.patch("/{faq_id}", response_model=FAQOut)
def update_faq(faq_id: int, faq_update: FAQUpdate, db: Session = Depends(get_db)):
    """Update an FAQ entry"""
    try:
        faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
        if not faq:
            raise HTTPException(status_code=404, detail="FAQ not found")
        
        # Update fields if provided
        if faq_update.question is not None:
            faq.question = faq_update.question
        if faq_update.answer is not None:
            faq.answer = faq_update.answer
        if faq_update.tags is not None:
            faq.tags = faq_update.tags
        if faq_update.is_active is not None:
            faq.is_active = faq_update.is_active
        
        db.commit()
        db.refresh(faq)
        
        logger.info(f"Updated FAQ: {faq.id}")
        return faq
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating FAQ {faq_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update FAQ")


@router.delete("/{faq_id}")
def delete_faq(faq_id: int, db: Session = Depends(get_db)):
    """Delete an FAQ entry"""
    try:
        faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
        if not faq:
            raise HTTPException(status_code=404, detail="FAQ not found")
        
        db.delete(faq)
        db.commit()
        
        logger.info(f"Deleted FAQ: {faq_id}")
        return {"message": "FAQ deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting FAQ {faq_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete FAQ")


@router.patch("/{faq_id}/toggle")
def toggle_faq_status(faq_id: int, db: Session = Depends(get_db)):
    """Toggle FAQ active status"""
    try:
        faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
        if not faq:
            raise HTTPException(status_code=404, detail="FAQ not found")
        
        faq.is_active = not faq.is_active
        db.commit()
        db.refresh(faq)
        
        logger.info(f"Toggled FAQ {faq_id} status to: {faq.is_active}")
        return {"message": f"FAQ status updated to {'active' if faq.is_active else 'inactive'}", "is_active": faq.is_active}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling FAQ {faq_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to toggle FAQ status") 