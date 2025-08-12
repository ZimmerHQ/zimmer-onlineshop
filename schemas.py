from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from models import OrderStatus, PaymentStatus


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    sizes: List[str]
    image_url: str
    thumbnail_url: Optional[str] = None
    stock: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "پیراهن مردانه کلاسیک",
                "description": "پیراهن مردانه با طراحی کلاسیک و کیفیت بالا",
                "price": 850000.0,
                "sizes": ["L", "XL"],
                "image_url": "http://localhost:8000/static/images/product.jpg",
                "thumbnail_url": "http://localhost:8000/static/images/thumbnails/product.jpg",
                "stock": 10
            }
        }


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    sizes: Optional[List[str]] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    stock: Optional[int] = None


class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    price: float
    sizes: List[str]
    image_url: str
    thumbnail_url: Optional[str] = None
    stock: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Order Item Schemas
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = 1
    size: Optional[str] = None


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_price: float
    product_image_url: Optional[str] = None
    quantity: int
    size: Optional[str] = None
    unit_price: float
    total_price: float
    
    class Config:
        from_attributes = True


# Order Schemas
class OrderCreate(BaseModel):
    customer_name: str
    customer_phone: str
    customer_address: Optional[str] = None
    customer_instagram: Optional[str] = None
    items: List[OrderItemCreate]
    shipping_cost: float = 0.0
    discount_amount: float = 0.0
    payment_method: Optional[str] = None
    shipping_method: Optional[str] = None
    customer_notes: Optional[str] = None


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    payment_method: Optional[str] = None
    shipping_method: Optional[str] = None
    tracking_number: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    admin_notes: Optional[str] = None
    customer_notes: Optional[str] = None


class OrderOut(BaseModel):
    id: int
    order_number: str
    user_id: Optional[int] = None
    
    # Customer Information
    customer_name: str
    customer_phone: str
    customer_address: Optional[str] = None
    customer_instagram: Optional[str] = None
    
    # Order Details
    total_amount: float
    shipping_cost: float
    discount_amount: float
    final_amount: float
    
    # Status and Payment
    status: OrderStatus
    payment_status: PaymentStatus
    payment_method: Optional[str] = None
    
    # Shipping Information
    shipping_method: Optional[str] = None
    tracking_number: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    
    # Notes
    admin_notes: Optional[str] = None
    customer_notes: Optional[str] = None
    
    # Items
    items: List[OrderItemOut] = []
    
    class Config:
        from_attributes = True


# Order Summary for lists
class OrderSummary(BaseModel):
    id: int
    order_number: str
    customer_name: str
    customer_phone: str
    final_amount: float
    status: OrderStatus
    payment_status: PaymentStatus
    created_at: datetime
    items_count: int
    
    class Config:
        from_attributes = True


# Message and Conversation Schemas
class MessageOut(BaseModel):
    id: str
    userId: str
    content: str
    timestamp: datetime
    isFromUser: bool
    
    class Config:
        from_attributes = True


class ConversationOut(BaseModel):
    id: str
    userId: str
    messages: List[MessageOut] = []
    lastMessage: str
    lastMessageTime: datetime
    
    class Config:
        from_attributes = True 