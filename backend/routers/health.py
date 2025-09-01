"""
Health check endpoints for monitoring and deployment verification.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from sqlalchemy import text
import os
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Basic health check endpoint.
    Returns 200 OK if the service is running.
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "zimmer-backend",
        "version": "1.0.0"
    }

@router.get("/health/details")
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check including database connectivity.
    Returns comprehensive service status.
    """
    health_status = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "zimmer-backend",
        "version": "1.0.0",
        "environment": os.getenv("ENV", "development"),
        "checks": {}
    }
    
    # Database connectivity check
    try:
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        health_status["checks"]["database"] = {
            "status": "ok",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }
        health_status["status"] = "degraded"
    
    # Environment variables check
    required_env_vars = ["ENV"]
    optional_env_vars = ["OPENAI_API_KEY", "TELEGRAM_BOT_TOKEN", "FRONTEND_URL"]
    
    health_status["checks"]["environment"] = {
        "required": {},
        "optional": {}
    }
    
    for var in required_env_vars:
        value = os.getenv(var)
        health_status["checks"]["environment"]["required"][var] = {
            "status": "ok" if value else "missing",
            "value": value if value else None
        }
        if not value:
            health_status["status"] = "degraded"
    
    for var in optional_env_vars:
        value = os.getenv(var)
        health_status["checks"]["environment"]["optional"][var] = {
            "status": "ok" if value else "not_set",
            "value": value if value else None
        }
    
    # Overall status determination
    if health_status["status"] == "ok":
        health_status["message"] = "All systems operational"
    elif health_status["status"] == "degraded":
        health_status["message"] = "Service operational with warnings"
    else:
        health_status["message"] = "Service experiencing issues"
    
    return health_status

@router.get("/health/ready")
async def readiness_check():
    """
    Readiness check for Kubernetes/Render health checks.
    Returns 200 when the service is ready to accept traffic.
    """
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/health/live")
async def liveness_check():
    """
    Liveness check for Kubernetes/Render health checks.
    Returns 200 when the service is alive and running.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    } 