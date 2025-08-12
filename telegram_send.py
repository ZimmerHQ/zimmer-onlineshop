import requests
from sqlalchemy.orm import Session
from models import BotConfig
from config import TELEGRAM_TOKEN

def send_telegram_message(chat_id: int, text: str, db: Session = None) -> None:
    """
    Send a plain text message to a Telegram user using Telegram Bot API.
    """
    bot_token = None
    
    # Try to get bot token from database first
    if db:
        bot_config = db.query(BotConfig).filter(BotConfig.is_active == True).first()
        if bot_config:
            bot_token = bot_config.bot_token
    
    # Fallback to config if no database config
    if not bot_token:
        bot_token = TELEGRAM_TOKEN
    
    if not bot_token:
        print("No bot token found in database or config")
        return
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print(f"Message sent successfully to chat_id: {chat_id}")
        
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
