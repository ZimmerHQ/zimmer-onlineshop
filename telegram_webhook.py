from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import json
import re
from datetime import datetime

# Import our modules
from database import get_db
from models import User, Message, BotConfig, TelegramUser, TelegramMessage, Product, Order, OrderItem, FAQ
from gpt_service import ask_gpt
from receipt_handler import handle_receipt
from fallback_logger import log_fallback
from telegram_send import send_telegram_message
from intent_classifier import detect_intent

app = FastAPI()

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle incoming Telegram webhook messages with enhanced chatbot logic.
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
        first_name = message_data.get("from", {}).get("first_name")
        last_name = message_data.get("from", {}).get("last_name")
        text = message_data.get("text")
        
        # Handle photo messages (receipts)
        photo_id = None
        if "photo" in message_data:
            photo_sizes = message_data["photo"]
            largest_photo = max(photo_sizes, key=lambda x: x.get("file_size", 0))
            photo_id = largest_photo["file_id"]
        
        # Update or create TelegramUser
        telegram_user = db.query(TelegramUser).filter(TelegramUser.telegram_user_id == int(chat_id)).first()
        if not telegram_user:
            telegram_user = TelegramUser(
                telegram_user_id=int(chat_id),
                username=username,
                first_name=first_name,
                last_name=last_name,
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
                visits_count=1
            )
            db.add(telegram_user)
        else:
            telegram_user.last_seen = datetime.utcnow()
            telegram_user.visits_count += 1
        
        db.commit()
        db.refresh(telegram_user)
        
        # Log incoming message
        incoming_message = TelegramMessage(
            user_id=telegram_user.id,
            direction="in",
            text=text or "",
            payload_json=json.dumps(message_data)
        )
        db.add(incoming_message)
        db.commit()
        
        # Process commands and natural queries
        response = None
        
        if text:
            text = text.strip()
            
            # Handle commands
            if text.startswith('/'):
                response = handle_command(text, telegram_user, db)
            else:
                # Handle natural queries (product search, orders, etc.)
                response = handle_natural_query(text, telegram_user, db)
        
        elif photo_id:
            # Handle photo (receipt processing)
            response = handle_receipt(telegram_user.id, photo_id, db)
        
        # Default response if nothing else
        if not response:
            response = "سلام! چطور می‌تونم کمکتون کنم؟ 😊\n\nبرای دیدن دستورات موجود، /help را تایپ کنید."
        
        # Log outgoing message
        outgoing_message = TelegramMessage(
            user_id=telegram_user.id,
            direction="out",
            text=response,
            payload_json=json.dumps({"response": response})
        )
        db.add(outgoing_message)
        db.commit()
        
        # Send response via Telegram API
        await send_telegram_response(chat_id, response)
        
        return JSONResponse({"status": "ok"})
        
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return JSONResponse({"status": "ok"})


def handle_command(command: str, user: TelegramUser, db: Session) -> str:
    """Handle Telegram bot commands."""
    command = command.lower()
    
    if command == '/start':
        if user.visits_count == 1:
            return "🎉 سلام! به ربات فروشگاه خوش آمدید!\n\n" + \
                   "می‌تونید:\n" + \
                   "• محصولات را جستجو کنید\n" + \
                   "• سفارش ثبت کنید\n" + \
                   "• سوالات متداول را ببینید\n\n" + \
                   "برای شروع، نام محصول مورد نظرتان را تایپ کنید."
        else:
            return f"👋 سلام {user.first_name or user.username or 'کاربر'}! دوباره خوش آمدید!\n\n" + \
                   "چطور می‌تونم کمکتون کنم؟"
    
    elif command == '/help':
        return "📋 دستورات موجود:\n\n" + \
               "/start - شروع کار\n" + \
               "/help - راهنما\n" + \
               "/faq - سوالات متداول\n" + \
               "/orders - سفارشات شما\n\n" + \
               "یا کافیست نام محصول مورد نظرتان را تایپ کنید!"
    
    elif command == '/faq':
        return get_faq_summary(db)
    
    elif command == '/orders':
        return get_user_orders(user, db)
    
    else:
        return "❓ دستور ناشناخته. برای دیدن دستورات موجود، /help را تایپ کنید."


def handle_natural_query(text: str, user: TelegramUser, db: Session) -> str:
    """Handle natural language queries for products and orders."""
    
    # Check if it's a product search
    if any(word in text.lower() for word in ['قیمت', 'قیمت', 'هزینه', 'هزینه', 'چقدر', 'چقدر']):
        return search_product_by_text(text, db)
    
    # Check if it's an order request
    if any(word in text.lower() for word in ['سفارش', 'خرید', 'خرید', 'تعداد', 'عدد', 'سایز']):
        return process_order_request(text, user, db)
    
    # Default: treat as general question
    try:
        response = ask_gpt(text)
        if response and response.strip():
            return response
        else:
            return "متاسفم، متوجه نشدم. می‌تونید:\n" + \
                   "• نام محصول را تایپ کنید\n" + \
                   "• سوال خود را بپرسید\n" + \
                   "• از دستور /help استفاده کنید"
    except Exception as e:
        print(f"Error in GPT service: {e}")
        return "متاسفم، الان نمی‌تونم پاسخ بدم. لطفاً دوباره تلاش کنید."


def search_product_by_text(text: str, db: Session) -> str:
    """Search for products by text query."""
    try:
        # Extract product code or name from text
        # Look for patterns like "A0001", "قیمت A0001", etc.
        product_match = re.search(r'[A-Z]\d{4}', text.upper())
        if product_match:
            product_code = product_match.group()
            product = db.query(Product).filter(Product.code == product_code).first()
            
            if product:
                return f"📦 محصول: {product.name}\n" + \
                       f"💰 قیمت: {product.price:,} تومان\n" + \
                       f"📏 سایزهای موجود: {', '.join(product.sizes)}\n" + \
                       f"📦 موجودی: {product.stock} عدد\n\n" + \
                       f"برای سفارش، تعداد و سایز مورد نظرتان را مشخص کنید."
            else:
                return f"❌ محصول با کد {product_code} یافت نشد."
        
        # Search by name
        search_terms = text.replace('قیمت', '').replace('هزینه', '').replace('چقدر', '').strip()
        if len(search_terms) > 2:
            products = db.query(Product).filter(
                Product.name.ilike(f"%{search_terms}%")
            ).limit(3).all()
            
            if products:
                result = "🔍 محصولات یافت شده:\n\n"
                for product in products:
                    result += f"📦 {product.name}\n" + \
                              f"💰 {product.price:,} تومان\n" + \
                              f"📏 سایز: {', '.join(product.sizes)}\n\n"
                result += "برای سفارش، کد محصول و جزئیات را مشخص کنید."
                return result
            else:
                return f"❌ محصولی با نام '{search_terms}' یافت نشد."
        
        return "لطفاً کد محصول (مثل A0001) یا نام محصول را وارد کنید."
        
    except Exception as e:
        print(f"Error searching products: {e}")
        return "متاسفم، خطا در جستجوی محصولات. لطفاً دوباره تلاش کنید."


def process_order_request(text: str, user: TelegramUser, db: Session) -> str:
    """Process order requests from text."""
    try:
        # Parse order text like "۲ عدد A0001 سایز M"
        # This is a simplified parser - you might want to enhance it
        
        # Look for product code
        product_match = re.search(r'[A-Z]\d{4}', text.upper())
        if not product_match:
            return "لطفاً کد محصول را مشخص کنید (مثل A0001)."
        
        product_code = product_match.group()
        product = db.query(Product).filter(Product.code == product_code).first()
        
        if not product:
            return f"❌ محصول با کد {product_code} یافت نشد."
        
        # Look for quantity
        quantity_match = re.search(r'(\d+)\s*عدد', text)
        quantity = int(quantity_match.group(1)) if quantity_match else 1
        
        # Look for size
        size_match = re.search(r'سایز\s*([A-Z]+)', text.upper())
        size = size_match.group(1) if size_match else None
        
        if size and size not in product.sizes:
            return f"❌ سایز {size} برای محصول {product.name} موجود نیست.\n" + \
                   f"سایزهای موجود: {', '.join(product.sizes)}"
        
        # Create draft order
        order = Order(
            order_number=f"TG-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            customer_name=f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or f"User{user.telegram_user_id}",
            customer_phone=user.phone or "نامشخص",
            total_amount=product.price * quantity,
            final_amount=product.price * quantity,
            status="pending",
            payment_status="pending"
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        
        # Add order item
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            unit_price=product.price,
            size=size or product.sizes[0] if product.sizes else None
        )
        db.add(order_item)
        db.commit()
        
        return f"✅ سفارش شما ثبت شد!\n\n" + \
               f"📦 محصول: {product.name}\n" + \
               f"📏 سایز: {size or 'پیش‌فرض'}\n" + \
               f"🔢 تعداد: {quantity} عدد\n" + \
               f"💰 مبلغ کل: {order.final_amount:,} تومان\n" + \
               f"🆔 شماره سفارش: {order.order_number}\n\n" + \
               f"سفارش شما در وضعیت 'در انتظار تایید' قرار دارد."
        
    except Exception as e:
        print(f"Error processing order: {e}")
        return "متاسفم، خطا در ثبت سفارش. لطفاً دوباره تلاش کنید."


def get_faq_summary(db: Session) -> str:
    """Get FAQ summary for users."""
    try:
        faqs = db.query(FAQ).filter(FAQ.is_active == True).limit(5).all()
        
        if not faqs:
            return "📚 سوالات متداول در حال حاضر موجود نیست."
        
        result = "📚 سوالات متداول:\n\n"
        for i, faq in enumerate(faqs, 1):
            result += f"{i}. {faq.question}\n"
            result += f"   {faq.answer[:100]}...\n\n"
        
        result += "برای اطلاعات بیشتر، از وب‌سایت استفاده کنید."
        return result
        
    except Exception as e:
        print(f"Error getting FAQs: {e}")
        return "متاسفم، خطا در دریافت سوالات متداول."


def get_user_orders(user: TelegramUser, db: Session) -> str:
    """Get user's recent orders."""
    try:
        # Try to find orders by phone number
        orders = []
        if user.phone:
            orders = db.query(Order).filter(
                Order.customer_phone == user.phone
            ).order_by(Order.created_at.desc()).limit(3).all()
        
        if not orders:
            return "📋 سفارشی برای شما یافت نشد.\n\n" + \
                   "برای ثبت سفارش جدید، نام محصول مورد نظرتان را تایپ کنید."
        
        result = "📋 آخرین سفارشات شما:\n\n"
        for order in orders:
            result += f"🆔 {order.order_number}\n" + \
                      f"💰 مبلغ: {order.final_amount:,} تومان\n" + \
                      f"📊 وضعیت: {order.status}\n" + \
                      f"📅 تاریخ: {order.created_at.strftime('%Y/%m/%d')}\n\n"
        
        return result
        
    except Exception as e:
        print(f"Error getting user orders: {e}")
        return "متاسفم، خطا در دریافت سفارشات."


async def send_telegram_response(chat_id: str, text: str):
    """Send response via Telegram API."""
    try:
        # This would need to be implemented to actually send via Telegram API
        # For now, we'll just print the response
        print(f"Sending to {chat_id}: {text}")
        
        # TODO: Implement actual Telegram API call
        # import requests
        # config = db.query(TelegramConfig).first()
        # if config and config.bot_token:
        #     response = requests.post(
        #         f"https://api.telegram.org/bot{config.bot_token}/sendMessage",
        #         json={
        #             "chat_id": chat_id,
        #             "text": text,
        #             "parse_mode": "HTML"
        #         }
        #     )
        
    except Exception as e:
        print(f"Error sending Telegram response: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
