from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, Enum, Numeric, JSON, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
from datetime import datetime
import enum

# Import Base from database to avoid conflicts
from database import Base

class OrderStatus(enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    SOLD = "sold"
    CANCELLED = "cancelled"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class Customer(Base):
    __tablename__ = "customers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    customer_code: Mapped[str] = mapped_column(String(50), nullable=True, index=True)  # Will be NOT NULL after backfill
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="customer")

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
    order_code = Column(String(50), nullable=True, index=True)  # Stable business code, will be NOT NULL after backfill
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Optional for guest orders
    
    # CRM Integration
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    customer_snapshot = Column(JSON, nullable=True)  # Immutable copy at purchase time
    
    # Customer Information (legacy fields, kept for backward compatibility)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    customer_address = Column(Text, nullable=True)
    customer_instagram = Column(String, nullable=True)
    
    # Order Details
    total_amount = Column(Float, nullable=False)
    shipping_cost = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    final_amount = Column(Float, nullable=False)
    items_count = Column(Integer, default=0)  # Total quantity of items
    
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
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    receipts = relationship("Receipt", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)  # Support for variants
    
    # Product details at time of order (in case product changes later)
    product_name = Column(String, nullable=False)
    product_code = Column(String, nullable=False)  # Store product code snapshot
    product_price = Column(Float, nullable=False)
    product_image_url = Column(String, nullable=True)
    
    # Variant details (new system)
    sku_code = Column(String(50), nullable=True, index=True)  # SKU code for variant
    variant_attributes_snapshot = Column(JSON, nullable=True)  # Snapshot of variant attributes
    unit_price_snapshot = Column(Numeric(10, 2), nullable=True)  # Snapshot of unit price
    
    # Legacy variant details (backward compatibility)
    variant_size = Column(String, nullable=True)
    variant_color = Column(String, nullable=True)
    
    # Order details
    quantity = Column(Integer, nullable=False, default=1)
    size = Column(String, nullable=True)  # Legacy field, keep for backward compatibility
    unit_price = Column(Float, nullable=False)  # Unit price snapshot (base + variant delta)
    total_price = Column(Float, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    variant = relationship("ProductVariant")

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

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    prefix = Column(String, nullable=False, unique=True)  # A, B, C, etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to products
    products = relationship("Product", back_populates="category")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', prefix='{self.prefix}')>"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, nullable=False, default=5)
    code = Column(String, nullable=False, unique=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    image_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    sizes = Column(String, nullable=True)  # Comma-separated sizes (legacy)
    available_sizes_json = Column(Text, nullable=True)  # JSON array of available sizes
    available_colors_json = Column(Text, nullable=True)  # JSON array of available colors
    tags = Column(String, nullable=True)  # Comma-separated keywords
    labels_json = Column(Text, nullable=True)  # JSON array of labels
    attributes_json = Column(Text, nullable=True)  # JSON dict of attributes (key -> list[str])
    attribute_schema = Column(JSON, nullable=True)  # Schema defining required attributes and allowed values
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to category
    category = relationship("Category", back_populates="products")
    
    # Relationship to variants
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")

class ProductVariant(Base):
    __tablename__ = "product_variants"
    
    id = Column(Integer, primary_key=True, index=True)
    sku_code = Column(String(50), unique=True, nullable=False, index=True)  # Primary SKU identifier
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    attributes = Column(JSON, nullable=False, default={})  # Generic attributes (color, size, capacity, etc.)
    price_override = Column(Numeric(10, 2), nullable=True)  # Override product price if needed
    stock_qty = Column(Integer, default=0, nullable=False)  # Current stock quantity
    is_active = Column(Boolean, default=True, nullable=False, index=True)  # Whether variant is available
    attributes_hash = Column(String(64), nullable=True)  # Hash of attributes for uniqueness
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Legacy fields for backward compatibility
    size = Column(String, nullable=True)  # e.g., "S", "M", "L", "XL", "43", "44"
    color = Column(String, nullable=True)  # e.g., "قرمز", "آبی", "مشکی"
    sku = Column(String, nullable=True)  # Stock Keeping Unit (optional)
    stock = Column(Integer, default=0, nullable=False)
    price_delta = Column(Float, default=0.0, nullable=False)  # Optional price adjustment
    
    # Relationship to product
    product = relationship("Product", back_populates="variants")
    
    def __repr__(self):
        return f"<ProductVariant(id={self.id}, product_id={self.product_id}, size={self.size}, color={self.color}, stock={self.stock})>"

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


# ===============================
# TELEGRAM INTEGRATION MODELS
# ===============================

class MessageDirection(enum.Enum):
    IN = "in"      # From user to bot
    OUT = "out"    # From bot to user


class ReportPeriod(enum.Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TelegramConfig(Base):
    __tablename__ = "telegram_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_token = Column(String, nullable=False, unique=True)
    webhook_url = Column(String, nullable=False)
    webhook_secret = Column(String, nullable=False)  # Secret for webhook validation
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<TelegramConfig(id={self.id}, bot_token='{self.bot_token[:10]}...', is_active={self.is_active})>"


class TelegramUser(Base):
    __tablename__ = "telegram_users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    language_code = Column(String(8), nullable=True)
    first_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    visits_count = Column(Integer, default=1, nullable=False)
    phone = Column(String, nullable=True)
    note = Column(Text, nullable=True)
    is_blocked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    messages = relationship("TelegramMessage", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TelegramUser(id={self.id}, telegram_id={self.telegram_user_id}, username='{self.username}', visits={self.visits_count})>"


class TelegramMessage(Base):
    __tablename__ = "telegram_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("telegram_users.id"), nullable=False, index=True)
    direction = Column(String, nullable=False)  # "in" or "out"
    text = Column(Text, nullable=False)
    payload_json = Column(Text, nullable=True)  # Raw Telegram update or reply metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("TelegramUser", back_populates="messages")
    
    def __repr__(self):
        return f"<TelegramMessage(id={self.id}, user_id={self.user_id}, direction='{self.direction}', text='{self.text[:50]}...')>"


class FAQ(Base):
    __tablename__ = "faqs"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    tags = Column(String, nullable=True)  # Comma-separated tags
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<FAQ(id={self.id}, question='{self.question[:50]}...', is_active={self.is_active})>"


class SalesReport(Base):
    __tablename__ = "sales_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    period = Column(String, nullable=False)  # "weekly" or "monthly"
    start_date = Column(String, nullable=False)  # Store as string to avoid SQLite date issues
    end_date = Column(String, nullable=False)
    totals_json = Column(Text, nullable=False)  # JSON string with report data
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<SalesReport(id={self.id}, period='{self.period}', {self.start_date} to {self.end_date})>"

class SupportRequestStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class SupportRequest(Base):
    __tablename__ = "support_requests"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(32), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[SupportRequestStatus] = mapped_column(Enum(SupportRequestStatus), default=SupportRequestStatus.PENDING)
    telegram_user_id: Mapped[str] = mapped_column(String(50), nullable=True)  # For future Telegram integration
    admin_notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<SupportRequest(id={self.id}, customer='{self.customer_name}', status='{self.status}')>"


class ZimmerTenant(Base):
    __tablename__ = "zimmer_tenants"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_automation_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    integration_status: Mapped[str] = mapped_column(String(20), default="pending")
    service_url: Mapped[str] = mapped_column(String(500), nullable=True)
    demo_tokens: Mapped[int] = mapped_column(Integer, default=0)
    paid_tokens: Mapped[int] = mapped_column(Integer, default=0)
    kb_status: Mapped[str] = mapped_column(String(20), default="empty")
    kb_last_updated: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    kb_total_documents: Mapped[int] = mapped_column(Integer, default=0)
    kb_healthy: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ZimmerTenant(user_automation_id={self.user_automation_id}, status='{self.integration_status}')>"
