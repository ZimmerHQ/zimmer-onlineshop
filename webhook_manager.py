import requests
import json
import os
from typing import Dict, Optional, Tuple
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import BotConfig
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhook", tags=["webhook"])

class BotTokenRequest(BaseModel):
    bot_token: str
    webhook_url: Optional[str] = None

class WebhookResponse(BaseModel):
    success: bool
    message: str
    bot_info: Optional[Dict] = None
    webhook_info: Optional[Dict] = None

def validate_bot_token(bot_token: str) -> Tuple[bool, Optional[Dict], str]:
    """
    Validate a Telegram bot token by calling the getMe API.
    
    Returns:
        Tuple[bool, Optional[Dict], str]: (is_valid, bot_info, error_message)
    """
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot_info = data.get("result", {})
                return True, bot_info, ""
            else:
                return False, None, f"Telegram API error: {data.get('description', 'Unknown error')}"
        else:
            return False, None, f"HTTP {response.status_code}: {response.text}"
            
    except requests.exceptions.RequestException as e:
        return False, None, f"Network error: {str(e)}"
    except Exception as e:
        return False, None, f"Validation error: {str(e)}"

def set_webhook(bot_token: str, webhook_url: str) -> Tuple[bool, Optional[Dict], str]:
    """
    Set webhook for a Telegram bot.
    
    Returns:
        Tuple[bool, Optional[Dict], str]: (success, webhook_info, error_message)
    """
    try:
        url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        payload = {
            "url": webhook_url,
            "allowed_updates": ["message", "callback_query"],
            "drop_pending_updates": True
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                return True, data.get("result", {}), ""
            else:
                return False, None, f"Telegram API error: {data.get('description', 'Unknown error')}"
        else:
            return False, None, f"HTTP {response.status_code}: {response.text}"
            
    except requests.exceptions.RequestException as e:
        return False, None, f"Network error: {str(e)}"
    except Exception as e:
        return False, None, f"Webhook setup error: {str(e)}"

def get_webhook_info(bot_token: str) -> Tuple[bool, Optional[Dict], str]:
    """
    Get current webhook information for a bot.
    
    Returns:
        Tuple[bool, Optional[Dict], str]: (success, webhook_info, error_message)
    """
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                return True, data.get("result", {}), ""
            else:
                return False, None, f"Telegram API error: {data.get('description', 'Unknown error')}"
        else:
            return False, None, f"HTTP {response.status_code}: {response.text}"
            
    except requests.exceptions.RequestException as e:
        return False, None, f"Network error: {str(e)}"
    except Exception as e:
        return False, None, f"Webhook info error: {str(e)}"

def delete_webhook(bot_token: str) -> Tuple[bool, str]:
    """
    Delete webhook for a Telegram bot.
    
    Returns:
        Tuple[bool, str]: (success, error_message)
    """
    try:
        url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
        response = requests.post(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                return True, ""
            else:
                return False, f"Telegram API error: {data.get('description', 'Unknown error')}"
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
            
    except requests.exceptions.RequestException as e:
        return False, f"Network error: {str(e)}"
    except Exception as e:
        return False, f"Webhook deletion error: {str(e)}"

@router.post("/setup", response_model=WebhookResponse)
async def setup_webhook(request: BotTokenRequest, db: Session = Depends(get_db)):
    """
    Set up webhook for a Telegram bot.
    """
    try:
        # Validate bot token
        is_valid, bot_info, error_msg = validate_bot_token(request.bot_token)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid bot token: {error_msg}")
        
        # Generate webhook URL if not provided
        if not request.webhook_url:
            # Use the current server URL
            base_url = os.getenv("BASE_URL", "http://localhost:8000")
            request.webhook_url = f"{base_url}/telegram/webhook"
        
        # Set webhook
        webhook_success, webhook_info, webhook_error = set_webhook(request.bot_token, request.webhook_url)
        if not webhook_success:
            raise HTTPException(status_code=400, detail=f"Webhook setup failed: {webhook_error}")
        
        # Save bot configuration to database
        bot_config = BotConfig(
            bot_token=request.bot_token,
            bot_username=bot_info.get("username", ""),
            bot_name=bot_info.get("first_name", ""),
            webhook_url=request.webhook_url,
            is_active=True
        )
        
        # Check if config already exists
        existing_config = db.query(BotConfig).filter(BotConfig.bot_token == request.bot_token).first()
        if existing_config:
            existing_config.bot_username = bot_info.get("username", "")
            existing_config.bot_name = bot_info.get("first_name", "")
            existing_config.webhook_url = request.webhook_url
            existing_config.is_active = True
            db.commit()
        else:
            db.add(bot_config)
            db.commit()
        
        logger.info(f"✅ Webhook setup successful for bot @{bot_info.get('username', 'unknown')}")
        
        return WebhookResponse(
            success=True,
            message=f"Webhook setup successful for bot @{bot_info.get('username', 'unknown')}",
            bot_info=bot_info,
            webhook_info=webhook_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Webhook setup error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/status", response_model=WebhookResponse)
async def get_webhook_status(db: Session = Depends(get_db)):
    """
    Get current webhook status for all configured bots.
    """
    try:
        configs = db.query(BotConfig).filter(BotConfig.is_active == True).all()
        
        if not configs:
            return WebhookResponse(
                success=False,
                message="No active bot configurations found"
            )
        
        webhook_statuses = []
        for config in configs:
            success, webhook_info, error = get_webhook_info(config.bot_token)
            if success:
                webhook_statuses.append({
                    "bot_username": config.bot_username,
                    "bot_name": config.bot_name,
                    "webhook_url": webhook_info.get("url", ""),
                    "is_active": webhook_info.get("url", "") != "",
                    "last_error": webhook_info.get("last_error_message", "")
                })
            else:
                webhook_statuses.append({
                    "bot_username": config.bot_username,
                    "bot_name": config.bot_name,
                    "webhook_url": config.webhook_url,
                    "is_active": False,
                    "last_error": error
                })
        
        return WebhookResponse(
            success=True,
            message=f"Found {len(configs)} bot configuration(s)",
            webhook_info={"bots": webhook_statuses}
        )
        
    except Exception as e:
        logger.error(f"❌ Webhook status error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/{bot_token}")
async def delete_webhook_endpoint(bot_token: str, db: Session = Depends(get_db)):
    """
    Delete webhook for a specific bot.
    """
    try:
        # Delete webhook from Telegram
        success, error = delete_webhook(bot_token)
        if not success:
            raise HTTPException(status_code=400, detail=f"Webhook deletion failed: {error}")
        
        # Update database
        config = db.query(BotConfig).filter(BotConfig.bot_token == bot_token).first()
        if config:
            config.is_active = False
            db.commit()
        
        return {"success": True, "message": "Webhook deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Webhook deletion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 