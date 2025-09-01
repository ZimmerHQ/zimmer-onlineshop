from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import os
import logging
from uuid import uuid4

from database import get_db
from schemas.chat import ChatIn, ChatOut
from services.chat_tools import handle_tool
from gpt_service import call_gpt_for_intent, call_llm_for_action

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/chat", response_model=ChatOut)
async def chat_endpoint(payload: ChatIn, db: Session = Depends(get_db)):
    rid = uuid4().hex
    logger.info(f"⬅️ [{rid}] POST /api/chat: {payload.message}")

    try:
        # Simplified: bypass LLM, use deterministic flow
        action = None
        slots = {}

        logger.info(f"🤖 [{rid}] Using simplified deterministic flow (no LLM)")

        # 2) dispatch
        reply, extra = handle_tool(action, slots, db, rid=rid, conv_id=payload.conversation_id, message_text=payload.message)

        out = {"reply": reply, "slots": extra.get("slots", {})}
        if extra.get("order_id"): out["order_id"] = extra["order_id"]
        if extra.get("status"):   out["status"]   = extra["status"]

        # attach debug if not prod
        if os.getenv("ENV") != "prod":
            out["debug"] = {
              "rid": rid, "action": action, "slots_in": slots, "tool_debug": extra.get("debug", {}),
              "original_message": payload.message
            }

        logger.info(f"📝 [{rid}] Reply: {reply[:120]!r}")
        return out

    except Exception as e:
        logger.exception(f"❌ [{rid}] chat failure: {e}")
        msg = "یک خطای موقت رخ داد. لطفاً دوباره تلاش کنید."
        debug = None
        if os.getenv("ENV") != "prod":
            debug = {"rid": rid, "error": str(e)}
        return {"reply": msg, "slots": {}, "debug": debug} 