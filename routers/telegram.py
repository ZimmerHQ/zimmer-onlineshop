import logging
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session

from database import get_db
from services.telegram_service import TelegramService
from services.faq_service import FAQService
from services.crm_service import list_customers_with_stats, get_customer_detail, get_customer_by_phone, get_crm_overview
from schemas.telegram import (
    TelegramWebhookIn, TelegramConfigCreate, TelegramConfigUpdate, 
    TelegramConfigOut, TelegramUserOut, TelegramMessageOut,
    FAQCreate, FAQUpdate, FAQOut, ReportTriggerIn, SalesReportOut
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["telegram"])


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    secret: str = Query(..., description="Webhook secret for validation"),
    db: Session = Depends(get_db)
):
    """Receive Telegram webhook updates"""
    try:
        # Validate webhook secret
        telegram_service = TelegramService(db)
        if not telegram_service.config:
            raise HTTPException(status_code=500, detail="No active Telegram configuration")
        
        if telegram_service.config.webhook_secret != secret:
            logger.warning(f"Invalid webhook secret: {secret}")
            raise HTTPException(status_code=403, detail="Invalid webhook secret")
        
        # Parse the update
        body = await request.json()
        logger.info(f"Received Telegram webhook: {body.get('update_id')}")
        
        # Extract message data
        message = body.get('message', {})
        if not message:
            # Handle callback queries or other update types
            return {"status": "ok", "message": "No message in update"}
        
        # Extract user information
        from_user = message.get('from', {})
        if not from_user:
            logger.warning("No user information in message")
            return {"status": "ok", "message": "No user information"}
        
        # Get or create user
        try:
            user = telegram_service.get_or_create_user(from_user)
        except Exception as e:
            logger.error(f"Error creating/getting user: {e}")
            return {"status": "error", "message": "User management error"}
        
        # Check if user is blocked
        if user.is_blocked:
            logger.info(f"Blocked user {user.telegram_user_id} attempted to send message")
            return {"status": "ok", "message": "User blocked"}
        
        # Extract message text
        text = message.get('text', '').strip()
        if not text:
            return {"status": "ok", "message": "No text in message"}
        
        # Log inbound message
        telegram_service.log_message(user, 'in', text, body)
        
        # Handle commands
        if text.startswith('/'):
            parts = text.split(' ', 1)
            command = parts[0][1:]  # Remove leading slash
            args = parts[1] if len(parts) > 1 else ""
            
            response = telegram_service.handle_command(command, args, user)
        else:
            # Handle product queries or general messages
            response = telegram_service.handle_product_query(text)
        
        # Send response to user
        chat_id = message.get('chat', {}).get('id')
        if chat_id:
            success = telegram_service.send_message(
                chat_id, 
                response.text, 
                response.reply_markup
            )
            
            if success:
                # Log outbound message
                telegram_service.log_message(user, 'out', response.text, {
                    'reply_markup': response.reply_markup
                })
            else:
                logger.error(f"Failed to send message to chat {chat_id}")
        
        return {"status": "ok", "message": "Update processed"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/config")
async def create_telegram_config(
    config: TelegramConfigCreate,
    db: Session = Depends(get_db)
):
    """Create or update Telegram bot configuration"""
    try:
        # Check if config already exists
        existing_config = db.query(TelegramConfig).first()
        
        if existing_config:
            # Update existing config
            existing_config.bot_token = config.bot_token
            existing_config.webhook_url = config.webhook_url
            existing_config.webhook_secret = config.webhook_secret
            existing_config.is_active = config.is_active
            db.commit()
            db.refresh(existing_config)
            
            logger.info("Updated existing Telegram configuration")
            return existing_config
        else:
            # Create new config
            from models import TelegramConfig
            new_config = TelegramConfig(
                bot_token=config.bot_token,
                webhook_url=config.webhook_url,
                webhook_secret=config.webhook_secret,
                is_active=config.is_active
            )
            db.add(new_config)
            db.commit()
            db.refresh(new_config)
            
            logger.info("Created new Telegram configuration")
            return new_config
            
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating/updating Telegram config: {e}")
        raise HTTPException(status_code=500, detail="Failed to save configuration")


@router.get("/config")
async def get_telegram_config(db: Session = Depends(get_db)):
    """Get current Telegram bot configuration"""
    try:
        config = db.query(TelegramConfig).filter(TelegramConfig.is_active == True).first()
        if not config:
            raise HTTPException(status_code=404, detail="No active configuration found")
        
        return config
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Telegram config: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve configuration")


@router.post("/test-connection")
async def test_telegram_connection(db: Session = Depends(get_db)):
    """Test Telegram bot connection"""
    try:
        telegram_service = TelegramService(db)
        success, message = telegram_service.test_connection()
        
        return {
            "success": success,
            "message": message
        }
        
    except Exception as e:
        logger.error(f"Error testing Telegram connection: {e}")
        raise HTTPException(status_code=500, detail="Failed to test connection")


@router.get("/users")
async def list_telegram_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List Telegram users with pagination"""
    try:
        offset = (page - 1) * page_size
        
        users = db.query(TelegramUser).order_by(
            TelegramUser.last_seen.desc()
        ).offset(offset).limit(page_size).all()
        
        total = db.query(TelegramUser).count()
        
        return {
            "users": users,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "pages": (total + page_size - 1) // page_size
            }
        }
        
    except Exception as e:
        logger.error(f"Error listing Telegram users: {e}")
        raise HTTPException(status_code=500, detail="Failed to list users")


@router.get("/users/{user_id}")
async def get_telegram_user(user_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a Telegram user"""
    try:
        # Get Telegram user info
        from models import TelegramUser
        user = db.query(TelegramUser).filter(TelegramUser.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get CRM customer info if phone exists
        customer_info = None
        if user.phone:
            customer_info = get_customer_by_phone(db, user.phone)
        
        return {
            "user": {
                "id": user.id,
                "telegram_user_id": user.telegram_user_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
                "note": user.note,
                "first_seen": user.first_seen,
                "last_seen": user.last_seen,
                "visits_count": user.visits_count,
                "is_blocked": user.is_blocked
            },
            "customer": customer_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user information")


@router.get("/messages")
async def list_telegram_messages(
    user_id: Optional[int] = Query(None),
    direction: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """List Telegram messages with optional filtering"""
    try:
        from models import TelegramMessage, TelegramUser
        
        query = db.query(TelegramMessage).join(TelegramUser, TelegramMessage.user_id == TelegramUser.id)
        
        if user_id:
            query = query.filter(TelegramMessage.user_id == user_id)
        if direction:
            query = query.filter(TelegramMessage.direction == direction)
        
        messages = query.order_by(TelegramMessage.created_at.desc()).limit(limit).all()
        
        interactions = []
        for msg in messages:
            interactions.append({
                'id': msg.id,
                'direction': msg.direction,
                'text': msg.text,
                'created_at': msg.created_at,
                'user': {
                    'id': msg.user.id,
                    'telegram_user_id': msg.user.telegram_user_id,
                    'username': msg.user.username,
                    'first_name': msg.user.first_name,
                    'last_name': msg.user.last_name,
                    'phone': msg.user.phone
                }
            })
        
        return {"interactions": interactions}
        
    except Exception as e:
        logger.error(f"Error listing Telegram messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to list messages")


@router.get("/stats")
async def get_telegram_stats(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get unified CRM statistics (works for both bot and Telegram)"""
    try:
        # Get unified CRM overview
        crm_overview = get_crm_overview(db)
        
        # Get Telegram-specific stats
        from models import TelegramUser, TelegramMessage
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        telegram_users = db.query(TelegramUser).count()
        active_telegram_users = db.query(TelegramUser).filter(
            TelegramUser.last_seen >= cutoff_date
        ).count()
        
        telegram_messages = db.query(TelegramMessage).filter(
            TelegramMessage.created_at >= cutoff_date
        ).count()
        
        return {
            "period_days": days,
            "crm": crm_overview,
            "telegram": {
                "total_users": telegram_users,
                "active_users": active_telegram_users,
                "messages": telegram_messages
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


# FAQ endpoints
@router.get("/faq")
async def list_faqs(
    active_only: bool = Query(True),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List FAQ entries"""
    try:
        faq_service = FAQService(db)
        faqs = faq_service.list_faqs(active_only, limit)
        return {"faqs": faqs}
        
    except Exception as e:
        logger.error(f"Error listing FAQs: {e}")
        raise HTTPException(status_code=500, detail="Failed to list FAQs")


@router.post("/faq")
async def create_faq(
    faq: FAQCreate,
    db: Session = Depends(get_db)
):
    """Create a new FAQ entry"""
    try:
        faq_service = FAQService(db)
        new_faq = faq_service.create_faq(faq)
        return new_faq
        
    except Exception as e:
        logger.error(f"Error creating FAQ: {e}")
        raise HTTPException(status_code=500, detail="Failed to create FAQ")


@router.patch("/faq/{faq_id}")
async def update_faq(
    faq_id: int,
    faq_update: FAQUpdate,
    db: Session = Depends(get_db)
):
    """Update an FAQ entry"""
    try:
        faq_service = FAQService(db)
        updated_faq = faq_service.update_faq(faq_id, faq_update)
        
        if not updated_faq:
            raise HTTPException(status_code=404, detail="FAQ not found")
        
        return updated_faq
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating FAQ {faq_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update FAQ")


@router.delete("/faq/{faq_id}")
async def delete_faq(faq_id: int, db: Session = Depends(get_db)):
    """Delete an FAQ entry"""
    try:
        faq_service = FAQService(db)
        success = faq_service.delete_faq(faq_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="FAQ not found")
        
        return {"message": "FAQ deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting FAQ {faq_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete FAQ")


@router.get("/faq/stats")
async def get_faq_stats(db: Session = Depends(get_db)):
    """Get FAQ statistics"""
    try:
        faq_service = FAQService(db)
        stats = faq_service.get_faq_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting FAQ stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get FAQ statistics")


# Reports endpoints
@router.post("/reports/generate")
async def generate_report(
    report_request: ReportTriggerIn,
    db: Session = Depends(get_db)
):
    """Generate a sales report"""
    try:
        from services.reports_service import ReportsService
        reports_service = ReportsService(db)
        
        report = reports_service.generate_report(
            report_request.period,
            report_request.start_date,
            report_request.end_date
        )
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")


@router.get("/reports/latest")
async def get_latest_report(
    period: str = Query(..., description="Report period: weekly or monthly"),
    db: Session = Depends(get_db)
):
    """Get the latest report for a period"""
    try:
        from services.reports_service import ReportsService
        reports_service = ReportsService(db)
        
        report = reports_service.get_latest_report(period)
        if not report:
            raise HTTPException(status_code=404, detail=f"No {period} report found")
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest {period} report: {e}")
        raise HTTPException(status_code=500, detail="Failed to get report")


@router.get("/reports")
async def list_reports(
    period: Optional[str] = Query(None, description="Filter by period"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List recent reports"""
    try:
        from services.reports_service import ReportsService
        reports_service = ReportsService(db)
        
        reports = reports_service.list_reports(period, limit)
        return {"reports": reports}
        
    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        raise HTTPException(status_code=500, detail="Failed to list reports")


@router.get("/reports/{report_id}")
async def get_report_details(report_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a report"""
    try:
        from services.reports_service import ReportsService
        reports_service = ReportsService(db)
        
        summary = reports_service.get_report_summary(report_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get report")


@router.get("/reports/{report_id}/csv")
async def download_report_csv(report_id: int, db: Session = Depends(get_db)):
    """Download a report as CSV"""
    try:
        from services.reports_service import ReportsService
        reports_service = ReportsService(db)
        
        csv_content = reports_service.generate_csv(report_id)
        if not csv_content:
            raise HTTPException(status_code=404, detail="Report not found or CSV generation failed")
        
        from fastapi.responses import Response
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=report_{report_id}.csv"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating CSV for report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate CSV") 