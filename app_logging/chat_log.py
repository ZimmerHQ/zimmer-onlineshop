from datetime import datetime, timezone
import json

def log_message(db_session, conversation_id: str, role: str, text: str, intent: str | None = None, slots: dict | None = None):
    """
    Log chat messages using the ChatMessage model.
    """
    try:
        from models import ChatMessage
        
        # Convert slots to JSON string if it's a dict
        slots_json = json.dumps(slots, ensure_ascii=False) if slots else "{}"
        
        # Create ChatMessage object
        chat_message = ChatMessage(
            conversation_id=conversation_id,
            role=role,
            text=text or "",
            intent=intent,
            slots_json=slots_json,
            created_at=datetime.now(timezone.utc)
        )
        
        # Add and commit
        db_session.add(chat_message)
        db_session.commit()
        print(f"📝 Logged {role} message: {text[:50]}...")
    except Exception as e:
        print("⚠️ log_message failed:", repr(e))
        # Don't fail the main flow if logging fails 