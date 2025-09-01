from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import requests
import logging

from database import get_db
from models import TelegramConfig

router = APIRouter()
logger = logging.getLogger(__name__)


class TelegramConfigRequest(BaseModel):
    bot_token: str | None = None
    webhook_url: str | None = None
    secret: str | None = None


class TelegramConfigResponse(BaseModel):
    bot_token_exists: bool
    webhook_url: str | None
    secret_exists: bool


@router.get("/telegram/config", response_model=TelegramConfigResponse)
def get_telegram_config(db: Session = Depends(get_db)):
    """Get current Telegram configuration (without exposing sensitive data)"""
    try:
        config = db.query(TelegramConfig).first()
        
        if not config:
            return TelegramConfigResponse(
                bot_token_exists=False,
                webhook_url=None,
                secret_exists=False
            )
        
        return TelegramConfigResponse(
            bot_token_exists=bool(config.bot_token),
            webhook_url=config.webhook_url,
            secret_exists=bool(config.webhook_secret)
        )
    except Exception as e:
        logger.error(f"Error getting Telegram config: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Telegram configuration")


@router.post("/telegram/config")
def update_telegram_config(
    config_data: TelegramConfigRequest,
    db: Session = Depends(get_db)
):
    """Update Telegram configuration"""
    try:
        config = db.query(TelegramConfig).first()
        
        if not config:
            config = TelegramConfig(
                bot_token=config_data.bot_token or "",
                webhook_url=config_data.webhook_url or "",
                webhook_secret=config_data.secret or ""
            )
            db.add(config)
        else:
            if config_data.bot_token is not None:
                config.bot_token = config_data.bot_token
            if config_data.webhook_url is not None:
                config.webhook_url = config_data.webhook_url
            if config_data.secret is not None:
                config.webhook_secret = config_data.secret
        
        db.commit()
        
        return {"message": "Telegram configuration updated successfully"}
    except Exception as e:
        logger.error(f"Error updating Telegram config: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update Telegram configuration")


@router.get("/telegram/test")
def test_telegram_connection(db: Session = Depends(get_db)):
    """Test Telegram bot connection using stored token"""
    try:
        config = db.query(TelegramConfig).first()
        
        if not config or not config.bot_token:
            raise HTTPException(status_code=400, detail="No bot token configured")
        
        # Test connection by calling getMe
        response = requests.get(
            f"https://api.telegram.org/bot{config.bot_token}/getMe",
            timeout=10
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid bot token")
        
        bot_info = response.json()
        
        if not bot_info.get("ok"):
            raise HTTPException(status_code=400, detail="Telegram API error")
        
        return {
            "ok": True,
            "info": {
                "bot_id": bot_info["result"]["id"],
                "bot_name": bot_info["result"]["first_name"],
                "username": bot_info["result"]["username"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing Telegram connection: {e}")
        raise HTTPException(status_code=500, detail="Failed to test Telegram connection")


@router.post("/telegram/set_webhook")
def set_telegram_webhook(db: Session = Depends(get_db)):
    """Set Telegram webhook using stored configuration"""
    try:
        config = db.query(TelegramConfig).first()
        
        if not config or not config.bot_token:
            raise HTTPException(status_code=400, detail="No bot token configured")
        
        if not config.webhook_url:
            raise HTTPException(status_code=400, detail="No webhook URL configured")
        
        # Build webhook URL with secret if configured
        webhook_url = config.webhook_url
        if config.webhook_secret:
            webhook_url = f"{webhook_url}?secret={config.webhook_secret}"
        
        # Set webhook via Telegram API
        response = requests.post(
            f"https://api.telegram.org/bot{config.bot_token}/setWebhook",
            json={"url": webhook_url},
            timeout=10
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to set webhook via Telegram API")
        
        webhook_result = response.json()
        
        if not webhook_result.get("ok"):
            raise HTTPException(
                status_code=400, 
                detail=f"Telegram webhook error: {webhook_result.get('description', 'Unknown error')}"
            )
        
        return {
            "ok": True,
            "description": "Webhook set successfully",
            "webhook_url": webhook_url
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting Telegram webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to set Telegram webhook") 