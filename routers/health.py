from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import os
import subprocess

from database import get_db
from models import Category, Product

router = APIRouter(prefix="/health", tags=["health"])


def get_git_version() -> str:
    """Get git short SHA or return 'unknown'."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return "unknown"
    except Exception:
        return "unknown"


@router.get("/")
def health_check() -> Dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "ok"}


@router.get("/details")
def health_details(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Detailed health check with database status and counts."""
    try:
        # Test database connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_status = "ok"
        
        # Get counts
        categories_count = db.query(Category).count()
        products_count = db.query(Product).count()
        
    except Exception as e:
        db_status = "fail"
        categories_count = 0
        products_count = 0
    
    return {
        "db": db_status,
        "categories_count": categories_count,
        "products_count": products_count,
        "env": os.getenv("ENV", "dev"),
        "version": get_git_version()
    }
