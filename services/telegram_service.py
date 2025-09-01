import logging
import json
import httpx
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from models import TelegramUser, TelegramMessage, TelegramConfig, FAQ
from models import Product, Order
from schemas.telegram import BotResponse, TelegramWebhookIn
from services.product_service import search_products_by_name, get_product_by_code

logger = logging.getLogger(__name__)


class TelegramService:
    def __init__(self, db: Session):
        self.db = db
        self.config = self._get_active_config()
    
    def _get_active_config(self) -> Optional[TelegramConfig]:
        """Get active Telegram configuration"""
        return self.db.query(TelegramConfig).filter(TelegramConfig.is_active == True).first()
    
    def get_or_create_user(self, from_user: dict) -> TelegramUser:
        """Get or create Telegram user, update last_seen and visits_count"""
        telegram_user_id = from_user.get('id')
        if not telegram_user_id:
            raise ValueError("Invalid user data: missing user ID")
        
        # Try to find existing user
        user = self.db.query(TelegramUser).filter(
            TelegramUser.telegram_user_id == telegram_user_id
        ).first()
        
        if user:
            # Check if this is a returning visit (more than 24 hours since last message)
            now = datetime.utcnow()
            time_diff = now - user.last_seen
            
            if time_diff > timedelta(hours=24):
                user.visits_count += 1
                logger.info(f"User {telegram_user_id} returning visit, count: {user.visits_count}")
            
            user.last_seen = now
            user.username = from_user.get('username', user.username)
            user.first_name = from_user.get('first_name', user.first_name)
            user.last_name = from_user.get('last_name', user.last_name)
            user.language_code = from_user.get('language_code', user.language_code)
            
        else:
            # Create new user
            user = TelegramUser(
                telegram_user_id=telegram_user_id,
                username=from_user.get('username'),
                first_name=from_user.get('first_name'),
                last_name=from_user.get('last_name'),
                language_code=from_user.get('language_code'),
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
                visits_count=1
            )
            self.db.add(user)
            logger.info(f"Created new Telegram user: {telegram_user_id}")
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def log_message(self, user: TelegramUser, direction: str, text: str, payload: Optional[dict] = None):
        """Log a Telegram message (inbound or outbound)"""
        message = TelegramMessage(
            user_id=user.id,
            direction=direction,
            text=text,
            payload_json=json.dumps(payload) if payload else None
        )
        self.db.add(message)
        self.db.commit()
        logger.info(f"Logged {direction} message for user {user.telegram_user_id}: {text[:50]}...")
    
    def compose_welcome(self, user: TelegramUser, returning: bool = False) -> str:
        """Compose welcome message in Persian"""
        name = user.first_name or user.username or "کاربر"
        
        if returning:
            return f"خوش برگشتی {name}! 👋 امروز چطور می‌تونم کمکت کنم؟"
        else:
            return (
                f"سلام {name}! خوش آمدی 👋\n\n"
                "من می‌تونم درباره‌ی محصولات، قیمت‌ها و موجودی کمکت کنم.\n\n"
                "برای شروع بگو:\n"
                "• \"لیست محصولات\"\n"
                "• \"قیمت A0001\"\n"
                "• \"/faq\" برای سوالات متداول\n"
                "• \"/start\" برای راهنما"
            )
    
    def handle_command(self, command: str, args: str, user: TelegramUser) -> BotResponse:
        """Handle bot commands and return appropriate response"""
        command = command.lower()
        
        if command == "start":
            return BotResponse(text=self.compose_welcome(user, user.visits_count > 1))
        
        elif command == "faq":
            return self._handle_faq_command(args)
        
        elif command == "contact":
            return self._handle_contact_command(args, user)
        
        elif command == "orders":
            return self._handle_orders_command(user)
        
        elif command == "help":
            return BotResponse(text=self._get_help_text())
        
        else:
            return BotResponse(text=f"دستور \"{command}\" شناخته نشد. برای راهنما \"/help\" را بزنید.")
    
    def _handle_faq_command(self, args: str) -> BotResponse:
        """Handle /faq command"""
        faqs = self.db.query(FAQ).filter(FAQ.is_active == True).limit(5).all()
        
        if not faqs:
            return BotResponse(text="هیچ سوال متداولی در حال حاضر موجود نیست.")
        
        text = "سوالات پرتکرار:\n\n"
        for i, faq in enumerate(faqs, 1):
            text += f"{i}. {faq.question}\n"
            text += f"   {faq.answer}\n\n"
        
        # Add navigation buttons
        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "بیشتر", "callback_data": "faq_next"},
                    {"text": "قبلی", "callback_data": "faq_prev"}
                ]
            ]
        }
        
        return BotResponse(text=text, reply_markup=reply_markup)
    
    def _handle_contact_command(self, args: str, user: TelegramUser) -> BotResponse:
        """Handle /contact command to attach phone number"""
        if not args:
            return BotResponse(text="لطفاً شماره تلفن را وارد کنید. مثال: /contact 09123456789")
        
        # Simple phone validation (Iranian format)
        phone = args.strip()
        if not phone.startswith('09') or len(phone) != 11:
            return BotResponse(text="شماره تلفن باید ۱۱ رقم و با ۰۹ شروع شود.")
        
        user.phone = phone
        self.db.commit()
        
        return BotResponse(text=f"شماره تلفن {phone} با موفقیت ثبت شد.")
    
    def _handle_orders_command(self, user: TelegramUser) -> BotResponse:
        """Handle /orders command to show user's orders"""
        # Find orders by phone number
        if not user.phone:
            return BotResponse(text="برای مشاهده سفارشات، ابتدا شماره تلفن خود را با /contact ثبت کنید.")
        
        orders = self.db.query(Order).filter(
            and_(
                Order.customer_phone == user.phone,
                Order.status.in_(['pending', 'approved', 'sold'])
            )
        ).order_by(Order.created_at.desc()).limit(5).all()
        
        if not orders:
            return BotResponse(text="هیچ سفارش فعالی برای شما یافت نشد.")
        
        text = "سفارشات شما:\n\n"
        for order in orders:
            status_persian = {
                'pending': 'در انتظار تأیید',
                'approved': 'تأیید شده',
                'sold': 'فروخته شده'
            }.get(order.status, order.status)
            
            text += f"🛍️ {order.order_number}\n"
            text += f"   مبلغ: {order.final_amount:,} تومان\n"
            text += f"   وضعیت: {status_persian}\n"
            text += f"   تاریخ: {order.created_at.strftime('%Y/%m/%d')}\n\n"
        
        return BotResponse(text=text)
    
    def _get_help_text(self) -> str:
        """Get help text for bot commands"""
        return (
            "🤖 راهنمای ربات:\n\n"
            "دستورات موجود:\n"
            "• /start - شروع کار با ربات\n"
            "• /faq - سوالات متداول\n"
            "• /contact [شماره] - ثبت شماره تلفن\n"
            "• /orders - مشاهده سفارشات\n"
            "• /help - این راهنما\n\n"
            "سوالات آزاد:\n"
            "• \"قیمت [کد محصول]\" - دریافت قیمت\n"
            "• \"موجودی [نام محصول]\" - بررسی موجودی\n"
            "• \"لیست محصولات\" - مشاهده همه محصولات"
        )
    
    def handle_product_query(self, text: str) -> BotResponse:
        """Handle product-related queries"""
        text = text.strip().lower()
        
        # Check if it's a price query
        if text.startswith('قیمت') or text.startswith('price'):
            # Extract product code
            parts = text.split()
            if len(parts) >= 2:
                code = parts[1].upper()
                return self._get_product_price(code)
        
        # Check if it's a stock query
        if text.startswith('موجودی') or text.startswith('stock'):
            parts = text.split()
            if len(parts) >= 2:
                product_name = ' '.join(parts[1:])
                return self._get_product_stock(product_name)
        
        # Check if it's a general product search
        if text.startswith('لیست') or text.startswith('list'):
            return self._get_product_list()
        
        # Try to search products by name
        products = search_products_by_name(self.db, text, limit=3)
        if products:
            return self._format_product_search_results(products)
        
        # Fallback response
        return BotResponse(
            text=(
                "برای دریافت اطلاعات محصول، یکی از این موارد را امتحان کنید:\n\n"
                "• \"قیمت A0001\" - دریافت قیمت محصول\n"
                "• \"موجودی شلوار نایک\" - بررسی موجودی\n"
                "• \"لیست محصولات\" - مشاهده همه محصولات\n"
                "• \"/faq\" - سوالات متداول"
            )
        )
    
    def _get_product_price(self, code: str) -> BotResponse:
        """Get product price by code"""
        try:
            product = get_product_by_code(self.db, code)
            if not product:
                return BotResponse(text=f"محصولی با کد {code} یافت نشد.")
            
            # Parse sizes and colors if available
            sizes = []
            colors = []
            
            if hasattr(product, 'available_sizes_json') and product.available_sizes_json:
                try:
                    sizes = json.loads(product.available_sizes_json)
                except:
                    pass
            
            if hasattr(product, 'available_colors_json') and product.available_colors_json:
                try:
                    colors = json.loads(product.available_colors_json)
                except:
                    pass
            
            # Fallback to legacy sizes field
            if not sizes and hasattr(product, 'sizes') and product.sizes:
                sizes = product.sizes.split(',') if isinstance(product.sizes, str) else product.sizes
            
            text = f"📦 {product.name} (کد {product.code})\n\n"
            text += f"💰 قیمت: {product.price:,} تومان\n"
            text += f"📊 موجودی: {product.stock or 0}\n"
            
            if sizes:
                text += f"📏 سایزها: {', '.join(sizes)}\n"
            
            if colors:
                text += f"🎨 رنگ‌ها: {', '.join(colors)}\n"
            
            if product.description:
                text += f"\n📝 توضیحات: {product.description}\n"
            
            text += "\n💡 برای سفارش بگویید: \"۱ عدد سایز M مشکی\""
            
            return BotResponse(text=text)
            
        except Exception as e:
            logger.error(f"Error getting product price for code {code}: {e}")
            return BotResponse(text="خطا در دریافت اطلاعات محصول. لطفاً دوباره تلاش کنید.")
    
    def _get_product_stock(self, product_name: str) -> BotResponse:
        """Get product stock by name"""
        try:
            products = search_products_by_name(self.db, product_name, limit=3)
            if not products:
                return BotResponse(text=f"محصولی با نام \"{product_name}\" یافت نشد.")
            
            if len(products) == 1:
                product = products[0]
                text = f"📦 {product.name}\n"
                text += f"📊 موجودی: {product.stock or 0}\n"
                text += f"💰 قیمت: {product.price:,} تومان\n"
                text += f"🏷️ کد: {product.code}"
            else:
                text = f"چند محصول با نام \"{product_name}\" یافت شد:\n\n"
                for product in products:
                    text += f"• {product.name} (کد: {product.code})\n"
                    text += f"  موجودی: {product.stock or 0}, قیمت: {product.price:,} تومان\n\n"
                text += "برای اطلاعات دقیق‌تر، کد محصول را وارد کنید."
            
            return BotResponse(text=text)
            
        except Exception as e:
            logger.error(f"Error getting product stock for {product_name}: {e}")
            return BotResponse(text="خطا در دریافت اطلاعات موجودی. لطفاً دوباره تلاش کنید.")
    
    def _get_product_list(self) -> BotResponse:
        """Get list of available products"""
        try:
            products = self.db.query(Product).filter(Product.is_active == True).limit(10).all()
            
            if not products:
                return BotResponse(text="هیچ محصول فعالی یافت نشد.")
            
            text = "📋 محصولات موجود:\n\n"
            for product in products:
                text += f"• {product.name}\n"
                text += f"  کد: {product.code}, قیمت: {product.price:,} تومان\n"
                text += f"  موجودی: {product.stock or 0}\n\n"
            
            text += "💡 برای اطلاعات بیشتر، کد محصول را وارد کنید."
            
            return BotResponse(text=text)
            
        except Exception as e:
            logger.error(f"Error getting product list: {e}")
            return BotResponse(text="خطا در دریافت لیست محصولات. لطفاً دوباره تلاش کنید.")
    
    def _format_product_search_results(self, products: List[Product]) -> BotResponse:
        """Format product search results"""
        if len(products) == 1:
            # Single product found, show detailed info
            product = products[0]
            return self._get_product_price(product.code)
        
        # Multiple products found
        text = f"🔍 {len(products)} محصول یافت شد:\n\n"
        for product in products:
            text += f"• {product.name}\n"
            text += f"  کد: {product.code}, قیمت: {product.price:,} تومان\n"
            text += f"  موجودی: {product.stock or 0}\n\n"
        
        text += "💡 برای اطلاعات دقیق‌تر، کد محصول را وارد کنید."
        
        return BotResponse(text=text)
    
    def send_message(self, chat_id: int, text: str, reply_markup: Optional[dict] = None) -> bool:
        """Send message via Telegram Bot API"""
        if not self.config:
            logger.error("No active Telegram configuration found")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.config.bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            
            if reply_markup:
                data["reply_markup"] = reply_markup
            
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, json=data)
                response.raise_for_status()
                
                result = response.json()
                if result.get("ok"):
                    logger.info(f"Message sent to chat {chat_id}")
                    return True
                else:
                    logger.error(f"Telegram API error: {result.get('description')}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test bot connection by calling getMe"""
        if not self.config:
            return False, "No active configuration found"
        
        try:
            url = f"https://api.telegram.org/bot{self.config.bot_token}/getMe"
            
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url)
                response.raise_for_status()
                
                result = response.json()
                if result.get("ok"):
                    bot_info = result.get("result", {})
                    bot_name = bot_info.get("first_name", "Unknown")
                    bot_username = bot_info.get("username", "Unknown")
                    
                    return True, f"Bot connected successfully: {bot_name} (@{bot_username})"
                else:
                    return False, f"Telegram API error: {result.get('description')}"
                    
        except Exception as e:
            return False, f"Connection error: {str(e)}" 