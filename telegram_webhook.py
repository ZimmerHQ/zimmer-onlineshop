from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import json

# Import our modules
from database import get_db
from models import User, Message, BotConfig
from gpt_service import ask_gpt
# Order processing will be handled differently now
from receipt_handler import handle_receipt
from fallback_logger import log_fallback
from telegram_send import send_telegram_message
from intent_classifier import detect_intent

app = FastAPI()

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle incoming Telegram webhook messages.
    """
    try:
        # Parse the incoming webhook data
        body = await request.json()
        
        # Extract message data
        if "message" not in body:
            return JSONResponse({"status": "ok"})
        
        message_data = body["message"]
        chat_id = str(message_data.get("chat", {}).get("id"))
        username = message_data.get("from", {}).get("username")
        text = message_data.get("text")
        
        # Handle photo messages (receipts)
        photo_id = None
        if "photo" in message_data:
            # Get the largest photo size
            photo_sizes = message_data["photo"]
            largest_photo = max(photo_sizes, key=lambda x: x.get("file_size", 0))
            photo_id = largest_photo["file_id"]
        
        # Check if user exists in the database; create if not
        user = db.query(User).filter(User.chat_id == int(chat_id)).first()
        if not user:
            user = User(chat_id=int(chat_id), username=username)
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Log the message into models.Message table
        db_message = Message(
            user_id=user.id,
            chat_id=chat_id,
            text=text,
            photo_id=photo_id,
            intent="pending"  # Will be updated after intent detection
        )
        db.add(db_message)
        db.commit()
        
        # Call intent_classifier.detect_intent(message)
        intent = detect_intent(text) if text else "receipt" if photo_id else "fallback"
        
        # Update message with detected intent
        db_message.intent = intent
        db.commit()
        
        # Process based on intent
        response = None
        
        if intent == "question" and text:
            # If "question": call gpt_service.ask_gpt(message) → send reply
            try:
                response = ask_gpt(text)
                if not response or response.strip() == "":
                    response = "متاسفم، الان نمی‌تونم پاسخ بدم. لطفاً دوباره تلاش کنید."
            except Exception as e:
                print(f"Error in GPT service: {e}")
                response = "متاسفم، الان نمی‌تونم پاسخ بدم. لطفاً دوباره تلاش کنید."
        
        elif intent == "order" and text:
            # Order processing - for now, just acknowledge the order request
            response = "برای ثبت سفارش، لطفاً از طریق وب‌سایت اقدام کنید یا با پشتیبانی تماس بگیرید."
        
        elif intent == "receipt" and photo_id:
            # If "receipt": call receipt_handler.handle_receipt(user_id, photo_id)
            try:
                response = handle_receipt(user.id, photo_id, db)
                if not response:
                    response = "متاسفم، نتوانستم رسید شما را پردازش کنم. لطفاً دوباره تلاش کنید."
            except Exception as e:
                print(f"Error in receipt handler: {e}")
                response = "متاسفم، نتوانستم رسید شما را پردازش کنم. لطفاً دوباره تلاش کنید."
        
        elif intent == "chitchat" and text:
            # Handle casual conversation
            response = "سلام! چطور می‌تونم کمکتون کنم؟ 😊"
        
        else:
            # If fallback or unknown intent
            if text and len(text.strip()) > 0:
                # Try to treat as a question if it's not empty
                try:
                    response = ask_gpt(text)
                    if not response or response.strip() == "":
                        response = "متاسفم، متوجه نشدم. چطور می‌تونم کمکتون کنم؟"
                except Exception as e:
                    print(f"Error in fallback GPT: {e}")
                    response = "متاسفم، متوجه نشدم. چطور می‌تونم کمکتون کنم؟"
            else:
                response = "سلام! چطور می‌تونم کمکتون کنم؟ 😊"
        
        # Use telegram_send.send_telegram_message(chat_id, response) to reply
        if response:
            send_telegram_message(int(chat_id), response, db)
        
        # Return JSON {"status": "ok"}
        return JSONResponse({"status": "ok"})
        
    except Exception as e:
        print(f"Error processing webhook: {e}")
        # Still return ok to prevent Telegram from retrying
        return JSONResponse({"status": "ok"})

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
