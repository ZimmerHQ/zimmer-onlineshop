from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from typing import Optional
import time
import logging

from database import get_db
from config_root import ZIMMER_SERVICE_TOKEN
from services.zimmer_service import (
    provision_tenant, consume_usage, get_kb_status, reset_kb
)
from schemas.zimmer import (
    ZimmerProvisionRequest, ZimmerProvisionResponse,
    ZimmerUsageRequest, ZimmerUsageResponse,
    ZimmerKBStatusResponse, ZimmerKBResetResponse
)

router = APIRouter(prefix="/api/zimmer", tags=["zimmer"])
logger = logging.getLogger(__name__)

def verify_zimmer_token(x_zimmer_service_token: Optional[str] = Header(None)):
    """Verify Zimmer service token."""
    if not x_zimmer_service_token:
        logger.warning("Zimmer request missing service token")
        raise HTTPException(status_code=401, detail="Missing X-Zimmer-Service-Token header")
    
    if x_zimmer_service_token != ZIMMER_SERVICE_TOKEN:
        logger.warning("Zimmer request with invalid service token")
        raise HTTPException(status_code=401, detail="Invalid service token")
    
    return x_zimmer_service_token

@router.post("/provision", response_model=ZimmerProvisionResponse)
def provision_endpoint(
    request: ZimmerProvisionRequest,
    db: Session = Depends(get_db),
    token: str = Depends(verify_zimmer_token)
):
    """Provision a new tenant or update existing one."""
    start_time = time.time()
    
    try:
        result = provision_tenant(db, request)
        latency = (time.time() - start_time) * 1000
        
        logger.info(f"Zimmer provision - user_automation_id: {request.user_automation_id}, "
                   f"status: 200, latency: {latency:.1f}ms, endpoint: /provision")
        
        return result
    except Exception as e:
        latency = (time.time() - start_time) * 1000
        logger.error(f"Zimmer provision - user_automation_id: {request.user_automation_id}, "
                    f"status: 500, latency: {latency:.1f}ms, endpoint: /provision, error: {str(e)}")
        raise HTTPException(status_code=500, detail="Provision failed")

@router.post("/usage/consume", response_model=ZimmerUsageResponse)
def consume_usage_endpoint(
    request: ZimmerUsageRequest,
    db: Session = Depends(get_db),
    token: str = Depends(verify_zimmer_token)
):
    """Consume tokens for a tenant."""
    start_time = time.time()
    
    try:
        result = consume_usage(db, request)
        latency = (time.time() - start_time) * 1000
        
        logger.info(f"Zimmer usage consume - user_automation_id: {request.user_automation_id}, "
                   f"units: {request.units}, status: 200, latency: {latency:.1f}ms")
        
        return result
    except Exception as e:
        latency = (time.time() - start_time) * 1000
        logger.error(f"Zimmer usage consume - user_automation_id: {request.user_automation_id}, "
                    f"status: 500, latency: {latency:.1f}ms, error: {str(e)}")
        raise HTTPException(status_code=500, detail="Usage consumption failed")

@router.get("/kb/status", response_model=ZimmerKBStatusResponse)
def kb_status_endpoint(
    user_automation_id: int = Query(...),
    db: Session = Depends(get_db),
    token: str = Depends(verify_zimmer_token)
):
    """Get knowledge base status for a tenant."""
    start_time = time.time()
    
    try:
        result = get_kb_status(db, user_automation_id)
        latency = (time.time() - start_time) * 1000
        
        logger.info(f"Zimmer KB status - user_automation_id: {user_automation_id}, "
                   f"status: 200, latency: {latency:.1f}ms")
        
        return result
    except Exception as e:
        latency = (time.time() - start_time) * 1000
        logger.error(f"Zimmer KB status - user_automation_id: {user_automation_id}, "
                    f"status: 500, latency: {latency:.1f}ms, error: {str(e)}")
        raise HTTPException(status_code=500, detail="KB status check failed")

@router.post("/kb/reset", response_model=ZimmerKBResetResponse)
def kb_reset_endpoint(
    user_automation_id: int = Query(...),
    db: Session = Depends(get_db),
    token: str = Depends(verify_zimmer_token)
):
    """Reset knowledge base for a tenant."""
    start_time = time.time()
    
    try:
        result = reset_kb(db, user_automation_id)
        latency = (time.time() - start_time) * 1000
        
        logger.info(f"Zimmer KB reset - user_automation_id: {user_automation_id}, "
                   f"status: 200, latency: {latency:.1f}ms")
        
        return result
    except Exception as e:
        latency = (time.time() - start_time) * 1000
        logger.error(f"Zimmer KB reset - user_automation_id: {user_automation_id}, "
                    f"status: 500, latency: {latency:.1f}ms, error: {str(e)}")
        raise HTTPException(status_code=500, detail="KB reset failed")
