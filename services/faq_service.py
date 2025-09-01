import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from models import FAQ
from schemas.telegram import FAQCreate, FAQUpdate

logger = logging.getLogger(__name__)


class FAQService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_faq(self, faq_data: FAQCreate) -> FAQ:
        """Create a new FAQ entry"""
        try:
            faq = FAQ(
                question=faq_data.question,
                answer=faq_data.answer,
                tags=faq_data.tags,
                is_active=faq_data.is_active
            )
            self.db.add(faq)
            self.db.commit()
            self.db.refresh(faq)
            
            logger.info(f"Created FAQ: {faq.question[:50]}...")
            return faq
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating FAQ: {e}")
            raise
    
    def get_faq_by_id(self, faq_id: int) -> Optional[FAQ]:
        """Get FAQ by ID"""
        return self.db.query(FAQ).filter(FAQ.id == faq_id).first()
    
    def update_faq(self, faq_id: int, faq_data: FAQUpdate) -> Optional[FAQ]:
        """Update an existing FAQ"""
        try:
            faq = self.get_faq_by_id(faq_id)
            if not faq:
                return None
            
            # Update only provided fields
            if faq_data.question is not None:
                faq.question = faq_data.question
            if faq_data.answer is not None:
                faq.answer = faq_data.answer
            if faq_data.tags is not None:
                faq.tags = faq_data.tags
            if faq_data.is_active is not None:
                faq.is_active = faq_data.is_active
            
            self.db.commit()
            self.db.refresh(faq)
            
            logger.info(f"Updated FAQ {faq_id}: {faq.question[:50]}...")
            return faq
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating FAQ {faq_id}: {e}")
            raise
    
    def delete_faq(self, faq_id: int) -> bool:
        """Delete an FAQ entry"""
        try:
            faq = self.get_faq_by_id(faq_id)
            if not faq:
                return False
            
            self.db.delete(faq)
            self.db.commit()
            
            logger.info(f"Deleted FAQ {faq_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting FAQ {faq_id}: {e}")
            raise
    
    def list_faqs(self, active_only: bool = True, limit: Optional[int] = None) -> List[FAQ]:
        """List FAQs with optional filtering"""
        query = self.db.query(FAQ)
        
        if active_only:
            query = query.filter(FAQ.is_active == True)
        
        query = query.order_by(FAQ.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def search_faqs(self, query: str, limit: int = 5) -> List[FAQ]:
        """Search FAQs by question, answer, or tags using fuzzy matching"""
        if not query.strip():
            return []
        
        search_term = f"%{query.strip()}%"
        
        # Search in question, answer, and tags
        faqs = self.db.query(FAQ).filter(
            and_(
                FAQ.is_active == True,
                or_(
                    FAQ.question.ilike(search_term),
                    FAQ.answer.ilike(search_term),
                    FAQ.tags.ilike(search_term)
                )
            )
        ).order_by(FAQ.created_at.desc()).limit(limit).all()
        
        logger.info(f"FAQ search for '{query}' returned {len(faqs)} results")
        return faqs
    
    def get_faqs_by_tags(self, tags: List[str], limit: int = 10) -> List[FAQ]:
        """Get FAQs by specific tags"""
        if not tags:
            return []
        
        # Create search conditions for each tag
        tag_conditions = []
        for tag in tags:
            tag_conditions.append(FAQ.tags.ilike(f"%{tag.strip()}%"))
        
        faqs = self.db.query(FAQ).filter(
            and_(
                FAQ.is_active == True,
                or_(*tag_conditions)
            )
        ).order_by(FAQ.created_at.desc()).limit(limit).all()
        
        logger.info(f"FAQ search by tags {tags} returned {len(faqs)} results")
        return faqs
    
    def toggle_faq_status(self, faq_id: int) -> Optional[FAQ]:
        """Toggle FAQ active status"""
        try:
            faq = self.get_faq_by_id(faq_id)
            if not faq:
                return None
            
            faq.is_active = not faq.is_active
            self.db.commit()
            self.db.refresh(faq)
            
            status = "activated" if faq.is_active else "deactivated"
            logger.info(f"FAQ {faq_id} {status}")
            return faq
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error toggling FAQ {faq_id} status: {e}")
            raise
    
    def get_faq_stats(self) -> dict:
        """Get FAQ statistics"""
        try:
            total_faqs = self.db.query(FAQ).count()
            active_faqs = self.db.query(FAQ).filter(FAQ.is_active == True).count()
            inactive_faqs = total_faqs - active_faqs
            
            # Get tag statistics
            tag_stats = {}
            faqs_with_tags = self.db.query(FAQ).filter(
                and_(FAQ.is_active == True, FAQ.tags.isnot(None))
            ).all()
            
            for faq in faqs_with_tags:
                if faq.tags:
                    tags = [tag.strip() for tag in faq.tags.split(',') if tag.strip()]
                    for tag in tags:
                        tag_stats[tag] = tag_stats.get(tag, 0) + 1
            
            # Sort tags by frequency
            top_tags = sorted(tag_stats.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "total_faqs": total_faqs,
                "active_faqs": active_faqs,
                "inactive_faqs": inactive_faqs,
                "top_tags": top_tags
            }
            
        except Exception as e:
            logger.error(f"Error getting FAQ stats: {e}")
            return {} 