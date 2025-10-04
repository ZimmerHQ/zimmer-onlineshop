"""
Zimmer integration SQLAlchemy models.
Defines user isolation, token management, and usage tracking tables.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger, func, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
import json
from database import Base
from app.core.settings import (
    USER_ID_MAX_LENGTH, AUTOMATION_ID_MAX_LENGTH, EMAIL_MAX_LENGTH, 
    NAME_MAX_LENGTH, SESSION_ID_MAX_LENGTH, REASON_MAX_LENGTH
)

class AutomationUser(Base):
    """
    Represents a user in the automation system with token management.
    Provides multi-tenant isolation keyed by (user_id, automation_id).
    """
    __tablename__ = "automation_users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(USER_ID_MAX_LENGTH), nullable=False, index=True)
    automation_id: Mapped[str] = mapped_column(String(AUTOMATION_ID_MAX_LENGTH), nullable=False, index=True)
    user_email: Mapped[str] = mapped_column(String(EMAIL_MAX_LENGTH), nullable=True)
    user_name: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH), nullable=True)
    tokens_remaining: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    demo_tokens: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Unique constraint on (user_id, automation_id)
    __table_args__ = (
        Index('ix_automation_users_user_automation', 'user_id', 'automation_id', unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<AutomationUser(id={self.id}, user_id='{self.user_id}', automation_id='{self.automation_id}', tokens={self.tokens_remaining})>"

class UserSession(Base):
    """
    Tracks user sessions for the automation system.
    """
    __tablename__ = "user_sessions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(USER_ID_MAX_LENGTH), nullable=False, index=True)
    automation_id: Mapped[str] = mapped_column(String(AUTOMATION_ID_MAX_LENGTH), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(SESSION_ID_MAX_LENGTH), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    last_activity: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    
    def __repr__(self) -> str:
        return f"<UserSession(id={self.id}, user_id='{self.user_id}', session_id='{self.session_id}')>"

class UsageLedger(Base):
    """
    Tracks all token usage and top-ups for audit and analytics.
    Records both consumption (negative delta) and top-ups (positive delta).
    """
    __tablename__ = "usage_ledger"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(USER_ID_MAX_LENGTH), nullable=False, index=True)
    automation_id: Mapped[str] = mapped_column(String(AUTOMATION_ID_MAX_LENGTH), nullable=False, index=True)
    delta: Mapped[int] = mapped_column(BigInteger, nullable=False)  # negative for consume, positive for top-up
    reason: Mapped[str] = mapped_column(String(REASON_MAX_LENGTH), nullable=False)  # action or reason for the change
    meta: Mapped[str] = mapped_column(Text, nullable=True)  # JSON serialized metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    
    def set_meta(self, data: dict) -> None:
        """Set metadata as JSON string."""
        self.meta = json.dumps(data) if data else None
    
    def get_meta(self) -> dict:
        """Get metadata as dictionary."""
        if self.meta:
            try:
                return json.loads(self.meta)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def __repr__(self) -> str:
        return f"<UsageLedger(id={self.id}, user_id='{self.user_id}', delta={self.delta}, reason='{self.reason}')>"

