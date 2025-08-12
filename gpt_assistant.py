import os
import logging
import json
from typing import List, Dict, Optional, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime
import openai
from .models import Product, Message, User, Order, OrderItem, OrderStatus, PaymentStatus
from .schemas import OrderCreate, OrderItemCreate
from .product_handler import search_products_by_name, get_products

# Configure logging
logger = logging.getLogger(__name__)

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def detect_intent(message: str) -> str:
    """Detect user intent from message"""
    message = message.strip().lower()
    
    # Check for greeting
    if "سلام" in message:
        return "greeting"
    
    # Check for order intent (including order details)
    order_keywords = ["می‌خوام", "بخرم", "سفارش", "ثبت", "سایز", "رنگ", "تعداد", "عدد", "دانه"]
    if any(keyword in message for keyword in order_keywords):
        return "order"
    
    # Check for search intent
    search_keywords = ["چی دارید", "محصول", "دارید", "شلوار", "پیراهن", "کفش", "دارین"]
    if any(keyword in message for keyword in search_keywords):
        return "search"
    
    # Check for confirmation
    if any(keyword in message for keyword in ["تایید", "تأیید", "بله"]):
        return "confirmation"
    
    return "unknown"

def get_system_prompt() -> str:
    """Get the system prompt for GPT"""
    return """
    شما یک فروشنده‌ی حرفه‌ای در فروشگاه آنلاین هستید. لطفاً مؤدب و غیررسمی باشید و فقط در اولین پیام سلام دهید.
    - اگر کاربر قصد خرید دارد، جزئیات سفارش را به ترتیب بپرس: سایز، رنگ، تعداد
    - اگر دنبال محصول است، از دیتابیس اطلاعات بده (نام، قیمت، سایزها، موجودی)
    - اگر سفارش کامل شد، خلاصه سفارش را بده و تایید بگیر
    - پاسخ‌ها همیشه به زبان فارسی و طبیعی باشند
    """

class GPTAssistant:
    def __init__(self):
        self.system_prompt = """شما یک فروشنده حرفه‌ای و دوستانه در فروشگاه آنلاین هستید که به زبان فارسی صحبت می‌کنید. 

نکات مهم:
1. فقط در اولین پیام خوش‌آمدگویی کنید
2. مثل یک فروشنده واقعی رفتار کنید - گرم، حرفه‌ای و مفید
3. وقتی مشتری قصد خرید دارد، جزئیات را جمع‌آوری کنید:
   - سایز مورد نظر
   - رنگ دلخواه  
   - تعداد
4. اطلاعات جمع‌آوری شده را در حافظه نگه دارید
5. خلاصه سفارش را نشان دهید و تأیید بگیرید
6. همیشه به زبان فارسی و با لحن طبیعی پاسخ دهید

هدف: کمک به مشتری برای خرید راحت و سریع"""

    def search_products(self, db: Session, query: str) -> List[Product]:
        """Search for products based on user query using product_handler"""
        try:
            # Use the search function from product_handler
            products = search_products_by_name(db, query)
            
            logger.info(f"🔍 Found {len(products)} products for query: '{query}'")
            return products
            
        except Exception as e:
            logger.error(f"❌ Error searching products: {str(e)}")
            return []

    def format_product_list(self, products: List[Product]) -> str:
        """Format product list for GPT response"""
        if not products:
            return "متأسفانه محصولی با این مشخصات پیدا نکردم."
        
        product_list = "محصولات موجود:\n\n"
        for i, product in enumerate(products, 1):
            stock_info = f"موجودی: {product.stock}" if product.stock is not None else "موجود"
            sizes_info = f"سایزهای موجود: {', '.join(product.sizes.split(','))}" if product.sizes is not None else "سایز: یکسان"
            
            product_list += f"{i}. {product.name}\n"
            product_list += f"   قیمت: {product.price:,} تومان\n"
            product_list += f"   {stock_info}\n"
            product_list += f"   {sizes_info}\n"
            product_list += f"   توضیحات: {product.description}\n\n"
        
        return product_list

    def detect_order_intent(self, message: str) -> Dict[str, Any]:
        """Detect if user wants to place an order and extract order details"""
        message_lower = message.lower()
        
        # Keywords indicating order intent
        order_keywords = [
            'سفارش', 'خرید', 'می‌خوام', 'می‌خواهم', 'بخر', 'بخرم', 'می‌خوام بخرم',
            'order', 'buy', 'want', 'purchase', 'get'
        ]
        
        # Keywords indicating confirmation
        confirm_keywords = [
            'بله', 'بله درست', 'بله بله', 'آره', 'آره درست', 'بله سفارش بده', 'درست',
            'yes', 'yeah', 'correct', 'right', 'confirm'
        ]
        
        # Keywords indicating cancellation
        cancel_keywords = [
            'نه', 'نه ممنون', 'نه فعلاً', 'نه الان نه', 'بعداً', 'نه الان',
            'no', 'not now', 'later', 'cancel'
        ]
        
        # Keywords for size information
        size_keywords = ['سایز', 'size', 'اندازه']
        
        # Keywords for color information
        color_keywords = ['رنگ', 'color', 'رنگی']
        
        # Keywords for quantity information
        quantity_keywords = ['تعداد', 'quantity', 'چند', 'عدد', 'دانه']
        
        # Check for order intent
        if any(keyword in message_lower for keyword in order_keywords):
            return {"intent": "order_intent", "confidence": 0.8}
        
        # Check for confirmation
        if any(keyword in message_lower for keyword in confirm_keywords):
            return {"intent": "confirm_order", "confidence": 0.9}
        
        # Check for cancellation
        if any(keyword in message_lower for keyword in cancel_keywords):
            return {"intent": "cancel_order", "confidence": 0.8}
        
        # Check for size information
        if any(keyword in message_lower for keyword in size_keywords):
            return {"intent": "provide_size", "confidence": 0.7}
        
        # Check for color information
        if any(keyword in message_lower for keyword in color_keywords):
            return {"intent": "provide_color", "confidence": 0.7}
        
        # Check for quantity information
        if any(keyword in message_lower for keyword in quantity_keywords):
            return {"intent": "provide_quantity", "confidence": 0.7}
        
        return {"intent": "general", "confidence": 0.5}

    def extract_order_details(self, message: str) -> Dict[str, Any]:
        """Extract order details from user message"""
        message_lower = message.lower()
        details = {}
        
        # Extract size information - improved patterns for Persian
        size_patterns = [
            r'سایز\s*(\d+)', r'size\s*(\d+)', r'اندازه\s*(\d+)',
            r'(\d+)\s*سایز', r'(\d+)\s*size', r'سایز\s*(\d+)', r'(\d+)'
        ]
        for pattern in size_patterns:
            import re
            match = re.search(pattern, message_lower)
            if match:
                details['size'] = match.group(1)
                break
        
        # Extract color information - improved patterns for Persian
        color_patterns = [
            r'رنگ\s*(\w+)', r'color\s*(\w+)', r'(\w+)\s*رنگ',
            r'مشکی', r'سفید', r'آبی', r'قرمز', r'سبز', r'زرد', r'نارنجی', r'بنفش'
        ]
        for pattern in color_patterns:
            import re
            match = re.search(pattern, message_lower)
            if match:
                details['color'] = match.group(1) if match.groups() else match.group(0)
                break
        
        # Extract quantity information - improved patterns for Persian
        quantity_patterns = [
            r'(\d+)\s*عدد', r'(\d+)\s*دانه', r'(\d+)\s*تا',
            r'تعداد\s*(\d+)', r'quantity\s*(\d+)', r'یک\s*عدد', r'یک\s*دانه',
            r'سدونه', r'یک\s*تا', r'(\d+)'
        ]
        for pattern in quantity_patterns:
            import re
            match = re.search(pattern, message_lower)
            if match:
                if 'یک' in pattern or 'سدونه' in pattern:
                    details['quantity'] = 1
                else:
                    details['quantity'] = int(match.group(1))
                break
        
        # If no quantity found, default to 1
        if 'quantity' not in details:
            details['quantity'] = 1
        
        return details

    def check_order_completeness(self, order_details: Dict[str, Any]) -> Dict[str, Any]:
        """Check if order details are complete and return missing information"""
        missing = []
        complete = True
        
        if not order_details.get('size'):
            missing.append('سایز')
            complete = False
        
        if not order_details.get('color'):
            missing.append('رنگ')
            complete = False
        
        if not order_details.get('quantity'):
            missing.append('تعداد')
            complete = False
        
        return {
            'complete': complete,
            'missing': missing,
            'details': order_details
        }

    def generate_order_summary_persian(self, product_name: str, order_details: Dict[str, Any]) -> str:
        """Generate order summary in Persian"""
        size = order_details.get('size', 'نامشخص')
        color = order_details.get('color', 'نامشخص')
        quantity = order_details.get('quantity', 1)
        
        summary = f"شما یک {product_name} {color} سایز {size} می‌خواهید. "
        if quantity > 1:
            summary += f"تعداد: {quantity} عدد. "
        
        summary += "تأیید می‌کنید؟"
        return summary

    def ask_for_missing_order_details(self, conversation_context: Dict) -> str:
        """Ask for missing order details"""
        try:
            order_details = conversation_context.get('order_details', {})
            missing = []
            
            if not order_details.get('size'):
                missing.append('سایز')
            if not order_details.get('color'):
                missing.append('رنگ')
            if not order_details.get('quantity'):
                missing.append('تعداد')
            
            if missing:
                missing_str = '، '.join(missing)
                return f"لطفاً {missing_str} مورد نظرتان را بفرمایید."
            else:
                return "تمام جزئیات سفارش جمع‌آوری شد. خلاصه سفارش را نشان می‌دهم."
        except Exception as e:
            logger.error(f"[❌ GPT Order Details Error] {str(e)}")
            print(f"[❌ GPT Order Details Error] {str(e)}")
            return "خطا در بررسی جزئیات سفارش. لطفاً دوباره تلاش کنید."

    def format_product_list_response(self, products: List[Product]) -> str:
        """Format product list for response"""
        try:
            if not products:
                return "متأسفانه محصولی با این مشخصات پیدا نکردم. می‌توانید محصول دیگری جستجو کنید؟"
            
            response = "محصولات موجود:\n\n"
            for i, product in enumerate(products, 1):
                try:
                    # Safe string operations
                    sizes_list = product.sizes.split(",") if product.sizes else []
                    sizes_str = ", ".join(sizes_list) if sizes_list else "یکسان"
                    stock_info = f"موجودی: {product.stock}" if product.stock is not None else "موجود"
                    
                    # Safe price formatting
                    price_str = f"{product.price:,}" if product.price is not None else "نامشخص"
                    
                    response += f"{i}. {product.name or 'نامشخص'}\n"
                    response += f"   قیمت: {price_str} تومان\n"
                    response += f"   سایزهای موجود: {sizes_str}\n"
                    response += f"   {stock_info}\n"
                    response += f"   توضیحات: {product.description or 'بدون توضیحات'}\n\n"
                except Exception as e:
                    logger.error(f"[❌ GPT Product Formatting Error - Individual Product] {str(e)}")
                    print(f"[❌ GPT Product Formatting Error - Individual Product] {str(e)}")
                    # Skip this product and continue with others
                    continue
            
            response += "کدام محصول را می‌خواهید؟"
            return response
            
        except Exception as e:
            logger.error(f"[❌ GPT Product Formatting Error - Overall] {str(e)}")
            print(f"[❌ GPT Product Formatting Error - Overall] {str(e)}")
            return "خطا در نمایش اطلاعات محصول. لطفاً دوباره تلاش کنید."

    def finalize_and_confirm_order(self, conversation_context: Dict) -> str:
        """Finalize order and ask for confirmation"""
        try:
            order_details = conversation_context.get('order_details', {})
            selected_product = conversation_context.get('selected_product')
            
            if not selected_product:
                return "متأسفانه محصولی انتخاب نشده است. لطفاً ابتدا محصول مورد نظرتان را انتخاب کنید."
            
            if not order_details:
                return "جزئیات سفارش کامل نیست. لطفاً سایز، رنگ و تعداد را مشخص کنید."
            
            summary = self.generate_order_summary_persian(selected_product['name'], order_details)
            return summary
        except Exception as e:
            logger.error(f"[❌ GPT Order Finalization Error] {str(e)}")
            print(f"[❌ GPT Order Finalization Error] {str(e)}")
            return "خطا در نهایی کردن سفارش. لطفاً دوباره تلاش کنید."

    def create_order_summary(self, selected_products: List[Dict]) -> str:
        """Create order summary for confirmation"""
        if not selected_products:
            return "هیچ محصولی انتخاب نشده است."
        
        summary = "خلاصه سفارش شما:\n\n"
        total_amount = 0
        
        for product in selected_products:
            item_total = product['price'] * product['quantity']
            total_amount += item_total
            
            summary += f"• {product['name']}\n"
            summary += f"  تعداد: {product['quantity']}\n"
            if product.get('size'):
                summary += f"  سایز: {product['size']}\n"
            summary += f"  قیمت واحد: {product['price']:,} تومان\n"
            summary += f"  جمع: {item_total:,} تومان\n\n"
        
        summary += f"💰 جمع کل: {total_amount:,} تومان\n"
        summary += f"🚚 هزینه ارسال: 50,000 تومان\n"
        summary += f"💳 مبلغ نهایی: {total_amount + 50000:,} تومان\n\n"
        summary += "آیا می‌خواهید این سفارش را ثبت کنید؟"
        
        return summary

    def save_message(self, db: Session, user_id: Optional[int], text: str, role: str = "user") -> Optional[Message]:
        """Save message to database"""
        try:
            message = Message(
                user_id=user_id,
                text=text,
                role=role
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            logger.info(f"💾 Saved {role} message: {text[:50]}...")
            return message
        except Exception as e:
            logger.error(f"❌ Error saving message: {str(e)}")
            db.rollback()
            return None

    def load_conversation_history(self, db: Session, user_id: int, limit: int = 10) -> List[Dict[str, str]]:
        """Load recent conversation history from database"""
        try:
            # Get recent messages for the user, ordered by creation time
            messages = db.query(Message).filter(
                Message.user_id == user_id
            ).order_by(Message.id.desc()).limit(limit).all()
            
            # Reverse to get chronological order and convert to GPT format
            conversation_history = []
            for message in reversed(messages):
                # Use the role field from the database
                role = message.role if message.role else "user"
                
                conversation_history.append({
                    "role": role,
                    "content": message.text
                })
            
            logger.info(f"📚 Loaded {len(conversation_history)} messages from conversation history")
            return conversation_history
            
        except Exception as e:
            logger.error(f"❌ Error loading conversation history: {str(e)}")
            return []

    def create_order_from_products(self, db: Session, selected_products: List[Dict], customer_info: Dict) -> Optional[Order]:
        """Create order from selected products"""
        try:
            # Prepare order items
            order_items = []
            for product in selected_products:
                order_item = OrderItemCreate(
                    product_id=product['id'],
                    quantity=product['quantity'],
                    size=product.get('size')
                )
                order_items.append(order_item)
            
            # Create order data
            order_data = OrderCreate(
                customer_name=customer_info.get('name', 'مشتری'),
                customer_phone=customer_info.get('phone', ''),
                customer_address=customer_info.get('address'),
                customer_instagram=customer_info.get('instagram'),
                items=order_items,
                shipping_cost=50000.0,  # Default shipping cost
                discount_amount=0.0,
                payment_method='cash',
                shipping_method='standard',
                customer_notes='سفارش از طریق چت'
            )
            
            # Import order creation function
            from order_handler import create_order
            order = create_order(order_data, db)
            
            logger.info(f"✅ Order created successfully: {order.order_number}")
            return order
            
        except Exception as e:
            logger.error(f"❌ Error creating order: {str(e)}")
            return None

    async def process_message(self, db: Session, user_message: str, user_id: Optional[int] = None, conversation_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process user message and generate GPT response with smart order detail collection"""
        try:
            # Use default user_id if not provided
            if user_id is None:
                user_id = 1  # Default user ID for now
            
            # Save user message
            self.save_message(db, user_id, user_message, "user")
            
            # Initialize context if not provided
            if conversation_context is None:
                conversation_context = {
                    "is_new_conversation": True,
                    "selected_products": [],
                    "customer_info": {},
                    "order_stage": "greeting",
                    "order_details": {},
                    "message_count": 0
                }
            
            # Increment message count
            conversation_context["message_count"] = conversation_context.get("message_count", 0) + 1
            
            # Load recent conversation history (last 10 messages)
            conversation_history = self.load_conversation_history(db, user_id, limit=10)
            
            # Detect intent using new function
            intent = detect_intent(user_message)
            order_details = self.extract_order_details(user_message)
            
            # Update order details in context
            if order_details:
                conversation_context["order_details"].update(order_details)
            
            # Check if this is first message (for greeting control)
            is_first_message = conversation_context["message_count"] == 1
            
            # Search for products if needed
            products = []
            if intent == "search" or intent == "order":
                try:
                    products = self.search_products(db, user_message)
                    logger.info(f"🔍 Searching for products with query: '{user_message}'")
                    logger.info(f"📦 Found {len(products)} products")
                except Exception as e:
                    logger.error(f"[❌ GPT Search Error] {str(e)}")
                    print(f"[❌ GPT Search Error] {str(e)}")
                    # Return clean error response
                    response = "خطا در جستجوی محصول. لطفاً دوباره تلاش کنید."
                    self.save_message(db, user_id, response, "assistant")
                    return {
                        "response": response,
                        "action": "error",
                        "products": [],
                        "conversation_context": conversation_context
                    }
            
            # Handle different intents with branching logic
            if intent == "greeting" and is_first_message:
                response = "سلام! به فروشگاه ما خوش اومدی. با چه محصولی می‌تونم کمکت کنم؟"
                
                # Save assistant message
                self.save_message(db, user_id, response, "assistant")
                
                return {
                    "response": response,
                    "action": "greeting",
                    "products": [],
                    "conversation_context": conversation_context
                }
                
            elif intent == "order":
                # Check if order details are complete
                order_completeness = self.check_order_completeness(conversation_context.get("order_details", {}))
                
                if order_completeness['complete']:
                    # Order is complete, create the order
                    try:
                        # Get the selected product (assuming the first product from search)
                        if products:
                            selected_product = {
                                'id': products[0].id,
                                'name': products[0].name,
                                'price': products[0].price,
                                'quantity': order_completeness['details']['quantity'],
                                'size': order_completeness['details']['size'],
                                'color': order_completeness['details']['color']
                            }
                            
                            # Create order in database
                            customer_info = {
                                'name': f'مشتری {user_id}',
                                'phone': '',
                                'address': 'آدرس از طریق چت',
                                'instagram': ''
                            }
                            
                            order = self.create_order_from_products(db, [selected_product], customer_info)
                            
                            if order:
                                response = f"✅ سفارش شما با موفقیت ثبت شد!\n\n"
                                response += f"شماره سفارش: {order.order_number}\n"
                                response += f"محصول: {selected_product['name']}\n"
                                response += f"سایز: {selected_product['size']}\n"
                                response += f"رنگ: {selected_product['color']}\n"
                                response += f"تعداد: {selected_product['quantity']}\n"
                                response += f"قیمت کل: {order.final_amount:,} تومان\n\n"
                                response += "سفارش شما در صفحه سفارشات قابل مشاهده است."
                                
                                # Clear order details from context
                                conversation_context["order_details"] = {}
                                conversation_context["selected_product"] = None
                            else:
                                response = "❌ متأسفانه مشکلی در ثبت سفارش پیش آمد. لطفاً دوباره تلاش کنید."
                        else:
                            response = "❌ محصولی برای سفارش انتخاب نشده است. لطفاً ابتدا محصول مورد نظرتان را جستجو کنید."
                    except Exception as e:
                        logger.error(f"❌ Error creating order: {str(e)}")
                        response = "❌ خطا در ثبت سفارش. لطفاً دوباره تلاش کنید."
                else:
                    # Order is incomplete, ask for missing details
                    response = self.ask_for_missing_order_details(conversation_context)
                
                # Save assistant message
                self.save_message(db, user_id, response, "assistant")
                
                return {
                    "response": response,
                    "action": "collect_details" if not order_completeness['complete'] else "order_created",
                    "products": products,
                    "conversation_context": conversation_context
                }
                
            elif intent == "search":
                # Format product list response
                try:
                    response = self.format_product_list_response(products)
                except Exception as e:
                    logger.error(f"[❌ GPT Product Formatting Error] {str(e)}")
                    print(f"[❌ GPT Product Formatting Error] {str(e)}")
                    response = "خطا در نمایش اطلاعات محصول. لطفاً دوباره تلاش کنید."
                
                # Save assistant message
                self.save_message(db, user_id, response, "assistant")
                
                return {
                    "response": response,
                    "action": "show_products",
                    "products": products,
                    "conversation_context": conversation_context
                }
                
            elif intent == "confirmation":
                # Finalize and confirm order
                response = self.finalize_and_confirm_order(conversation_context)
                
                # Save assistant message
                self.save_message(db, user_id, response, "assistant")
                
                return {
                    "response": response,
                    "action": "confirm_order",
                    "products": products,
                    "conversation_context": conversation_context
                }
                
            else:
                # Unknown intent - use GPT for natural response
                response = "میشه لطفاً بیشتر توضیح بدید تا بهتر راهنمایی‌تون کنم؟"
                
                # Save assistant message
                self.save_message(db, user_id, response, "assistant")
                
                return {
                    "response": response,
                    "action": "continue",
                    "products": [],
                    "conversation_context": conversation_context
                }
            
            # Prepare context for GPT
            context = {
                "user_message": user_message,
                "intent": intent,
                "products_found": len(products),
                "conversation_stage": conversation_context.get("order_stage", "greeting"),
                "selected_products_count": len(conversation_context.get("selected_products", [])),
                "is_first_message": is_first_message,
                "order_details": conversation_context.get("order_details", {})
            }
            
            # Generate GPT response with full conversation history
            gpt_response = await self.generate_gpt_response_with_history(
                context, products, conversation_context, conversation_history
            )
            
            # Save assistant message
            self.save_message(db, user_id, gpt_response["response"], "assistant")
            
            # Update conversation context
            updated_context = self.update_conversation_context(conversation_context, user_message, gpt_response, products)
            
            return {
                "response": gpt_response["response"],
                "action": gpt_response.get("action", "continue"),
                "products": products,
                "conversation_context": updated_context
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {str(e)}")
            return {
                "response": "متأسفانه مشکلی پیش آمد. لطفاً دوباره تلاش کنید.",
                "action": "error",
                "products": [],
                "conversation_context": conversation_context or {}
            }

    async def generate_gpt_response_with_history(self, context: Dict, products: List[Product], conversation_context: Dict, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate GPT response using OpenAI API with full conversation history"""
        try:
            # Start with system message using new function
            messages = [{"role": "system", "content": get_system_prompt()}]
            
            # Add conversation history
            messages.extend(conversation_history)
            
            # Add current user message
            messages.append({"role": "user", "content": context["user_message"]})
            
            logger.info(f"📤 Sending {len(messages)} messages to GPT (including {len(conversation_history)} history messages)")
            
            # Call OpenAI API
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            gpt_response = response.choices[0].message.content
            
            # Determine action based on context and response
            action = self.determine_action(context, gpt_response, products)
            
            return {
                "response": gpt_response,
                "action": action
            }
            
        except Exception as e:
            logger.error(f"❌ Error calling OpenAI API: {str(e)}")
            # Fallback response
            return {
                "response": "سلام! به فروشگاه ما خوش آمدید. چطور می‌تونم کمکتون کنم؟",
                "action": "continue"
            }

    async def generate_gpt_response(self, context: Dict, products: List[Product], conversation_context: Dict) -> Dict[str, Any]:
        """Generate GPT response using OpenAI API (legacy method)"""
        try:
            # Prepare messages for GPT
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.build_user_prompt(context, products, conversation_context)}
            ]
            
            # Call OpenAI API
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            gpt_response = response.choices[0].message.content
            
            # Determine action based on context and response
            action = self.determine_action(context, gpt_response, products)
            
            return {
                "response": gpt_response,
                "action": action
            }
            
        except Exception as e:
            logger.error(f"❌ Error calling OpenAI API: {str(e)}")
            # Fallback response
            return {
                "response": "سلام! به فروشگاه ما خوش آمدید. چطور می‌تونم کمکتون کنم؟",
                "action": "continue"
            }

    def build_user_prompt(self, context: Dict, products: List[Product], conversation_context: Dict) -> str:
        """Build user prompt for GPT with smart seller behavior"""
        prompt = f"پیام کاربر: {context['user_message']}\n\n"
        
        # Add conversation stage
        stage = context.get("conversation_stage", "greeting")
        prompt += f"مرحله گفتگو: {stage}\n"
        
        # Check if this is first message
        is_first_message = context.get("is_first_message", False)
        if is_first_message:
            prompt += "⚠️ این اولین پیام کاربر است. فقط یک بار خوش‌آمدگویی کنید.\n"
        
        # Add order details if available
        order_details = context.get("order_details", {})
        if order_details:
            prompt += f"\nجزئیات سفارش جمع‌آوری شده:\n"
            for key, value in order_details.items():
                prompt += f"- {key}: {value}\n"
        
        # Add product information if available
        if products:
            prompt += f"\nمحصولات پیدا شده ({len(products)} عدد):\n"
            for i, product in enumerate(products, 1):
                # Get sizes as list
                sizes_list = product.sizes.split(",") if product.sizes else []
                sizes_str = ", ".join(sizes_list) if sizes_list else "یکسان"
                
                # Get stock information
                stock_info = f"موجودی: {product.stock}" if product.stock is not None else "موجود"
                
                prompt += f"{i}. {product.name}\n"
                prompt += f"   قیمت: {product.price:,} تومان\n"
                prompt += f"   سایزهای موجود: {sizes_str}\n"
                prompt += f"   {stock_info}\n"
                prompt += f"   توضیحات: {product.description}\n\n"
        
        # Add selected products if any
        selected_products = conversation_context.get("selected_products", [])
        if selected_products:
            prompt += f"\nمحصولات انتخاب شده:\n"
            for product in selected_products:
                prompt += f"- {product['name']} (تعداد: {product['quantity']})\n"
        
        # Add specific instructions based on context
        intent = context.get("intent", {}).get("intent", "general")
        
        if intent == "confirm_order":
            prompt += "\nکاربر می‌خواهد سفارش را تأیید کند. خلاصه سفارش را نشان دهید و تأیید نهایی بخواهید."
        elif intent == "order_intent":
            prompt += "\nکاربر قصد خرید دارد. جزئیات سفارش را جمع‌آوری کنید (سایز، رنگ، تعداد)."
        elif intent in ["provide_size", "provide_color", "provide_quantity"]:
            prompt += "\nکاربر اطلاعات سفارش را ارائه می‌دهد. اطلاعات را تأیید کنید و اگر چیزی کم است بپرسید."
        elif products:
            prompt += "\nمحصولات را معرفی کنید و از کاربر بپرسید کدام را می‌خواهد."
        elif is_first_message:
            prompt += "\nخوش‌آمدگویی کنید و از کاربر بپرسید چه کمکی می‌توانید بکنید."
        else:
            prompt += "\nبه سوال کاربر پاسخ دهید و کمک کنید."
        
        return prompt

    def determine_action(self, context: Dict, gpt_response: str, products: List[Product]) -> str:
        """Determine what action to take based on context and response"""
        intent = context.get("intent", {}).get("intent", "general")
        
        if intent == "confirm_order":
            return "confirm_order"
        elif intent == "cancel_order":
            return "cancel_order"
        elif products:
            return "show_products"
        elif context.get("conversation_stage") == "greeting":
            return "greeting"
        else:
            return "continue"

    def update_conversation_context(self, context: Dict, user_message: str, gpt_response: Dict, products: List[Product]) -> Dict:
        """Update conversation context based on interaction"""
        updated_context = context.copy()
        
        # Update conversation stage
        if context.get("is_new_conversation", True):
            updated_context["is_new_conversation"] = False
            updated_context["order_stage"] = "product_search"
        
        # Update based on intent
        intent = self.detect_order_intent(user_message)
        if intent["intent"] == "confirm_order":
            updated_context["order_stage"] = "order_confirmation"
        elif intent["intent"] == "cancel_order":
            updated_context["order_stage"] = "greeting"
            updated_context["selected_products"] = []
        
        # Add products to context if found
        if products:
            updated_context["available_products"] = [
                {
                    "id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "sizes": p.sizes.split(",") if p.sizes else [],
                    "stock": p.stock
                }
                for p in products
            ]
        
        return updated_context

# Create global instance
gpt_assistant = GPTAssistant() 