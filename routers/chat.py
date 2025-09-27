from backend.ai.graph import app as chat_graph
from backend.ai.agent import sales_agent_turn
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from token_tracker import track_openai_usage
from database import get_db
from models import ChatMessage
from config_root import CHAT_BUDGET_SECONDS, LLM_TIMEOUT, AGENT_MAX_ITERS, CHAT_MODEL
import json
import asyncio
import time

class ChatPayload(BaseModel):
    conversation_id: str
    message: str

# Simple in-memory state storage (in production, use Redis or DB)
_conversation_states = {}

def load_conversation_state(db: Session, conversation_id: str) -> dict:
    """Load conversation state from storage"""
    return _conversation_states.get(conversation_id, {})

def save_conversation_state(db: Session, conversation_id: str, state: dict):
    """Save conversation state to storage"""
    _conversation_states[conversation_id] = state

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.get("/ping")
def ping():
    """Health check endpoint for the chat router."""
    return {"ok": True}

@router.post("/test")
def test(payload: ChatPayload):
    """Test endpoint that echoes back the payload for frontend wiring checks."""
    return {"ok": True, "echo": payload.dict()}

@router.post("/graph")
def chat_via_graph(payload: ChatPayload, db: Session = Depends(get_db)):
    start_time = time.time()
    
    try:
        # Log user message
        user_msg = ChatMessage(
            conversation_id=payload.conversation_id,
            role="user",
            text=payload.message
        )
        db.add(user_msg)
        db.commit()
        
        # Use natural language sales agent with timeout protection
        state = load_conversation_state(db, payload.conversation_id)
        
        # Check if we have enough time budget
        elapsed = time.time() - start_time
        remaining_budget = CHAT_BUDGET_SECONDS - elapsed
        
        if remaining_budget <= 0:
            # Return graceful fallback response
            reply = "سلام! خوش آمدید. در حال حاضر سیستم شلوغ است. لطفاً دوباره تلاش کنید."
            order_id = None
            status = None
        else:
            # Set a timeout for the agent execution
            try:
                result = sales_agent_turn(db, payload.message, state)
                save_conversation_state(db, payload.conversation_id, result.get("state", {}))
                reply = result.get("reply", "")
                order_id = result.get("order_id")
                status = result.get("status")
            except Exception as e:
                # Graceful fallback on any agent error
                reply = "سلام! خوش آمدید. متاسفانه خطایی رخ داده است. لطفاً دوباره تلاش کنید."
                order_id = None
                status = None
        
        # Log assistant message
        assistant_msg = ChatMessage(
            conversation_id=payload.conversation_id,
            role="assistant",
            text=reply
        )
        db.add(assistant_msg)
        db.commit()
        
        # Track token usage (if available in result)
        if "usage" in result:
            usage = result["usage"]
            track_openai_usage(
                session_id=payload.conversation_id,
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                model="gpt-3.5-turbo"
            )
        
        return {
            "reply": reply,
            "order_id": order_id,
            "status": status,
        }
        
    except Exception as e:
        # Return graceful fallback on any error
        return {
            "reply": "متاسفانه خطایی رخ داده است. لطفاً دوباره تلاش کنید.",
            "order_id": None,
            "status": None,
        }

# NEW: Make /api/chat default to graph
@router.post("/")
def chat_default(payload: ChatPayload, db: Session = Depends(get_db)):
    try:
        return chat_via_graph(payload, db)
    except Exception as e:
        # Fallback to simple response if agent fails
        return {
            "reply": f"متاسفانه خطایی رخ داد: {str(e)}",
            "order_id": None,
            "status": "error"
        }