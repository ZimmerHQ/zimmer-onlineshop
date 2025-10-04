"""
Service token authentication for Zimmer platform integration.
Handles bcrypt-based token verification for platform→automation calls.
"""

import bcrypt
import secrets
from typing import Optional
from fastapi import HTTPException, Depends, Header
from app.core.settings import SERVICE_TOKEN, SERVICE_TOKEN_HASH

# Global variable to store computed hash
_computed_token_hash: Optional[bytes] = None

def _get_service_token_hash() -> bytes:
    """
    Get the service token hash, computing it if necessary.
    Returns the bcrypt hash for verification.
    """
    global _computed_token_hash
    
    if _computed_token_hash is not None:
        return _computed_token_hash
    
    if SERVICE_TOKEN_HASH:
        # Use pre-computed hash if available
        if isinstance(SERVICE_TOKEN_HASH, str):
            _computed_token_hash = SERVICE_TOKEN_HASH.encode('utf-8')
        else:
            _computed_token_hash = SERVICE_TOKEN_HASH
    elif SERVICE_TOKEN:
        # Compute hash from plain token
        _computed_token_hash = bcrypt.hashpw(
            SERVICE_TOKEN.encode('utf-8'), 
            bcrypt.gensalt()
        )
    else:
        raise ValueError("Neither SERVICE_TOKEN nor SERVICE_TOKEN_HASH is configured")
    
    return _computed_token_hash

def verify_service_token(header_token: str) -> bool:
    """
    Verify a service token against the configured hash.
    
    Args:
        header_token: The token from the X-Zimmer-Service-Token header
        
    Returns:
        True if token is valid, False otherwise
    """
    if not header_token:
        return False
    
    try:
        if SERVICE_TOKEN_HASH:
            # Use bcrypt verification
            token_hash = _get_service_token_hash()
            return bcrypt.checkpw(
                header_token.encode('utf-8'), 
                token_hash
            )
        elif SERVICE_TOKEN:
            # Fallback to constant-time comparison for dev mode
            return secrets.compare_digest(header_token, SERVICE_TOKEN)
        else:
            return False
    except Exception:
        return False

def require_service_token(
    x_zimmer_service_token: Optional[str] = Header(None, alias="X-Zimmer-Service-Token")
) -> str:
    """
    FastAPI dependency that requires a valid service token.
    
    Args:
        x_zimmer_service_token: The service token from the header
        
    Returns:
        The validated token
        
    Raises:
        HTTPException: 401 if token is missing or invalid
    """
    if not x_zimmer_service_token:
        raise HTTPException(
            status_code=401,
            detail="Missing X-Zimmer-Service-Token header"
        )
    
    if not verify_service_token(x_zimmer_service_token):
        raise HTTPException(
            status_code=401,
            detail="Invalid service token"
        )
    
    return x_zimmer_service_token

