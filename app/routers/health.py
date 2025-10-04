"""
Health router for Zimmer automation system.
Provides system status, uptime, and health checks.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import time
import psutil
import os
from database import get_db
from app.core.settings import APP_VERSION

router = APIRouter()

# Track application start time
_start_time = time.time()

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    last_updated: str
    version: str
    uptime: float
    memory_usage: Optional[Dict[str, Any]] = None
    database_status: str

def get_memory_usage() -> Optional[Dict[str, Any]]:
    """
    Get memory usage information if psutil is available.
    
    Returns:
        Memory usage dictionary or None if psutil not available
    """
    try:
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            "rss": memory_info.rss,  # Resident Set Size
            "vms": memory_info.vms,  # Virtual Memory Size
            "percent": process.memory_percent(),
            "available": psutil.virtual_memory().available,
            "total": psutil.virtual_memory().total
        }
    except (ImportError, AttributeError, OSError):
        return None

def check_database_status() -> str:
    """
    Check database connectivity.
    
    Returns:
        "ok" if database is accessible, "error" otherwise
    """
    try:
        db = next(get_db())
        # Simple query to test connection
        db.execute("SELECT 1")
        db.close()
        return "ok"
    except Exception:
        return "error"

@router.get("/api/health", response_model=HealthResponse)
async def get_health():
    """
    Get system health status.
    
    Returns:
        Health status with system information
    """
    try:
        # Calculate uptime
        uptime_seconds = time.time() - _start_time
        
        # Get memory usage
        memory_usage = get_memory_usage()
        
        # Check database status
        database_status = check_database_status()
        
        # Determine overall status
        overall_status = "healthy"
        if database_status != "ok":
            overall_status = "degraded"
        
        return HealthResponse(
            status=overall_status,
            last_updated=datetime.now(timezone.utc).isoformat(),
            version=APP_VERSION,
            uptime=uptime_seconds,
            memory_usage=memory_usage,
            database_status=database_status
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )

