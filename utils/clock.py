from datetime import datetime, timezone
from typing import Optional


def utcnow() -> datetime:
    """
    Returns timezone-aware UTC datetime.
    
    Returns:
        datetime: Current UTC time with timezone info
    """
    return datetime.now(timezone.utc)


def utcnow_optional() -> Optional[datetime]:
    """
    Returns timezone-aware UTC datetime or None.
    Useful for optional datetime fields.
    
    Returns:
        Optional[datetime]: Current UTC time with timezone info or None
    """
    return utcnow() 