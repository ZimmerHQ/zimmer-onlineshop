"""
Users service for Zimmer automation system.
Handles user management, token operations, and usage tracking.
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.zimmer import AutomationUser, UserSession, UsageLedger
from app.core.settings import SEED_TOKENS
import uuid
import json
from datetime import datetime

class UsersService:
    """Service for managing automation users and their tokens."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def ensure_user(
        self, 
        user_id: str, 
        automation_id: str, 
        email: Optional[str] = None, 
        name: Optional[str] = None, 
        tokens: Optional[int] = None, 
        demo_tokens: Optional[int] = None
    ) -> AutomationUser:
        """
        Ensure a user exists in the system with upsert semantics.
        
        Args:
            user_id: The Zimmer user ID
            automation_id: The automation ID
            email: User email (optional)
            name: User name (optional)
            tokens: Initial token amount (optional)
            demo_tokens: Initial demo token amount (optional)
            
        Returns:
            The AutomationUser instance
        """
        # Try to get existing user
        user = self.get_user(user_id, automation_id)
        
        if user is None:
            # Create new user
            user = AutomationUser(
                user_id=user_id,
                automation_id=automation_id,
                user_email=email,
                user_name=name,
                tokens_remaining=tokens if tokens is not None else (SEED_TOKENS if SEED_TOKENS > 0 else 0),
                demo_tokens=demo_tokens or 0
            )
            self.db.add(user)
            try:
                self.db.commit()
                self.db.refresh(user)
            except IntegrityError:
                # Handle race condition - user might have been created by another process
                self.db.rollback()
                user = self.get_user(user_id, automation_id)
                if user is None:
                    raise
        else:
            # Update existing user if new data provided
            updated = False
            if email is not None and user.user_email != email:
                user.user_email = email
                updated = True
            if name is not None and user.user_name != name:
                user.user_name = name
                updated = True
            if tokens is not None and user.tokens_remaining != tokens:
                user.tokens_remaining = tokens
                updated = True
            if demo_tokens is not None and user.demo_tokens != demo_tokens:
                user.demo_tokens = demo_tokens
                updated = True
            
            if updated:
                user.updated_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(user)
        
        return user
    
    def get_user(self, user_id: str, automation_id: str) -> Optional[AutomationUser]:
        """
        Get a user by user_id and automation_id.
        
        Args:
            user_id: The Zimmer user ID
            automation_id: The automation ID
            
        Returns:
            The AutomationUser instance or None if not found
        """
        return self.db.query(AutomationUser).filter(
            AutomationUser.user_id == user_id,
            AutomationUser.automation_id == automation_id
        ).first()
    
    def update_tokens(
        self, 
        user_id: str, 
        automation_id: str, 
        delta: int, 
        reason: str, 
        meta: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Update user tokens and record the change in usage ledger.
        
        Args:
            user_id: The Zimmer user ID
            automation_id: The automation ID
            delta: Token change (negative for consume, positive for top-up)
            reason: Reason for the change
            meta: Additional metadata
            
        Returns:
            The new token balance
        """
        user = self.get_user(user_id, automation_id)
        if user is None:
            raise ValueError(f"User {user_id} not found for automation {automation_id}")
        
        # Calculate new balance (ensure it doesn't go below 0)
        new_balance = max(0, user.tokens_remaining + delta)
        actual_delta = new_balance - user.tokens_remaining
        
        # Update user tokens
        user.tokens_remaining = new_balance
        user.updated_at = datetime.utcnow()
        
        # Record in usage ledger
        ledger_entry = UsageLedger(
            user_id=user_id,
            automation_id=automation_id,
            delta=actual_delta,
            reason=reason,
            meta=json.dumps(meta) if meta else None
        )
        self.db.add(ledger_entry)
        
        self.db.commit()
        self.db.refresh(user)
        
        return new_balance
    
    def create_session(self, user_id: str, automation_id: str) -> str:
        """
        Create a new user session.
        
        Args:
            user_id: The Zimmer user ID
            automation_id: The automation ID
            
        Returns:
            The session ID
        """
        session_id = str(uuid.uuid4())
        session = UserSession(
            user_id=user_id,
            automation_id=automation_id,
            session_id=session_id
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """
        Get a user session by session ID.
        
        Args:
            session_id: The session ID
            
        Returns:
            The UserSession instance or None if not found
        """
        return self.db.query(UserSession).filter(
            UserSession.session_id == session_id
        ).first()
    
    def update_session_activity(self, session_id: str) -> bool:
        """
        Update the last activity time for a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            True if session was updated, False if not found
        """
        session = self.get_session(session_id)
        if session:
            session.last_activity = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def get_user_usage_history(
        self, 
        user_id: str, 
        automation_id: str, 
        limit: int = 100
    ) -> list[UsageLedger]:
        """
        Get usage history for a user.
        
        Args:
            user_id: The Zimmer user ID
            automation_id: The automation ID
            limit: Maximum number of records to return
            
        Returns:
            List of UsageLedger entries
        """
        return self.db.query(UsageLedger).filter(
            UsageLedger.user_id == user_id,
            UsageLedger.automation_id == automation_id
        ).order_by(UsageLedger.created_at.desc()).limit(limit).all()

