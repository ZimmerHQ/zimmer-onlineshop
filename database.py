import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.config import DATABASE_URL, DB_POOL_SIZE, DB_MAX_OVERFLOW

# Validate DATABASE_URL
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is required")

# Create engine with proper settings for SQLite or PostgreSQL
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL with connection pooling
    engine = create_engine(
        DATABASE_URL,
        pool_size=DB_POOL_SIZE,
        max_overflow=DB_MAX_OVERFLOW,
        pool_pre_ping=True,
        pool_recycle=300
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Safe DB session helper with automatic commit/rollback
from contextlib import contextmanager

@contextmanager
def session_scope():
    """Safe database session with automatic commit/rollback handling."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()