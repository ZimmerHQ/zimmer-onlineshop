from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class OrderStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    messages = relationship("Message", back_populates="user")
    orders = relationship("Order", back_populates="user")
    fallback_questions = relationship("FallbackQuestion", back_populates="user")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    text = Column(String)
    role = Column(String, default="user")  # "user" or "assistant"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="messages")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)  # "user", "assistant", "system"
    text = Column(Text, nullable=False)
    intent = Column(String, nullable=True)
    slots_json = Column(Text, nullable=True)  # JSON string of slots
    created_at = Column(DateTime, default=datetime.utcnow)

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)  # e.g., "ORD-2024-001"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Optional for guest orders
    
    # Customer Information
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    customer_address = Column(Text, nullable=True)
    customer_instagram = Column(String, nullable=True)
    
    # Order Details
    total_amount = Column(Float, nullable=False)
    shipping_cost = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    final_amount = Column(Float, nullable=False)
    
    # Status and Payment
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(String, nullable=True)  # "cash", "online", "bank_transfer"
    
    # Shipping Information
    shipping_method = Column(String, nullable=True)  # "standard", "express", "pickup"
    tracking_number = Column(String, nullable=True)
    estimated_delivery = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    
    # Notes
    admin_notes = Column(Text, nullable=True)
    customer_notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    receipts = relationship("Receipt", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Product details at time of order (in case product changes later)
    product_name = Column(String, nullable=False)
    product_price = Column(Float, nullable=False)
    product_image_url = Column(String, nullable=True)
    
    # Order details
    quantity = Column(Integer, nullable=False, default=1)
    size = Column(String, nullable=True)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")

class Receipt(Base):
    __tablename__ = "receipts"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    image_url = Column(String)
    verified = Column(Boolean, default=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    order = relationship("Order", back_populates="receipts")

class FallbackQuestion(Base):
    __tablename__ = "fallback_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="fallback_questions")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    sizes = Column(String, nullable=True)  # Comma-separated sizes
    image_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)  # Thumbnail URL for faster loading
    stock = Column(Integer, nullable=True, default=None)  # Optional stock field
    created_at = Column(DateTime, default=datetime.utcnow)

class BotConfig(Base):
    __tablename__ = "bot_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_token = Column(String, unique=True, nullable=False)
    bot_username = Column(String, nullable=True)
    bot_name = Column(String, nullable=True)
    webhook_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
