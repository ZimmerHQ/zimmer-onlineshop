"""
Chat state management service for persisting conversation state.
Uses in-memory dict for now, can be swapped with Redis later.
"""

from typing import Dict, Any, Optional
import logging

# In-memory storage for conversation states
# In production, this should be replaced with Redis or database
_conversation_states: Dict[str, Dict[str, Any]] = {}

logger = logging.getLogger(__name__)

def get_state(conversation_id: str) -> Dict[str, Any]:
    """Get conversation state, return empty dict if not exists."""
    state = _conversation_states.get(conversation_id, {})
    logger.debug(f"📋 Getting state for {conversation_id}: {state}")
    return state.copy()  # Return copy to prevent external modification

def set_state(conversation_id: str, new_state: Dict[str, Any]) -> None:
    """Set conversation state, merging with existing if present."""
    current = _conversation_states.get(conversation_id, {})
    current.update(new_state)
    _conversation_states[conversation_id] = current
    logger.debug(f"💾 Setting state for {conversation_id}: {current}")

def clear_state(conversation_id: str) -> None:
    """Clear conversation state."""
    if conversation_id in _conversation_states:
        del _conversation_states[conversation_id]
        logger.debug(f"🗑️ Cleared state for {conversation_id}")

def update_state(conversation_id: str, updates: Dict[str, Any]) -> None:
    """Update specific fields in conversation state."""
    current = get_state(conversation_id)
    current.update(updates)
    set_state(conversation_id, current)

def get_stage(conversation_id: str) -> str:
    """Get current conversation stage."""
    return get_state(conversation_id).get("stage", "idle")

def set_stage(conversation_id: str, stage: str) -> None:
    """Set conversation stage."""
    update_state(conversation_id, {"stage": stage})

def get_selected_product(conversation_id: str) -> Optional[Dict[str, Any]]:
    """Get selected product from conversation state."""
    return get_state(conversation_id).get("selected_product")

def set_selected_product(conversation_id: str, product: Dict[str, Any]) -> None:
    """Set selected product in conversation state."""
    update_state(conversation_id, {"selected_product": product})

def get_wanted(conversation_id: str) -> Dict[str, Any]:
    """Get wanted attributes (qty, size, color) from conversation state."""
    return get_state(conversation_id).get("wanted", {"qty": 1, "size": None, "color": None})

def set_wanted(conversation_id: str, wanted: Dict[str, Any]) -> None:
    """Set wanted attributes in conversation state."""
    update_state(conversation_id, {"wanted": wanted})

def reset_to_idle(conversation_id: str) -> None:
    """Reset conversation to idle state, clearing product and wanted."""
    clear_state(conversation_id)
    set_state(conversation_id, {"stage": "idle"})

# Future Redis integration stub
def _get_redis_client():
    """Stub for future Redis integration."""
    try:
        import redis
        return redis.Redis(host='localhost', port=6379, db=0)
    except ImportError:
        logger.warning("Redis not available, using in-memory storage")
        return None

def migrate_to_redis():
    """Future function to migrate from in-memory to Redis."""
    logger.info("Redis migration not implemented yet")
    pass 