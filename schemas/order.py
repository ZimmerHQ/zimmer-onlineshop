from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Literal
from models import OrderStatus, PaymentStatus


class OrderItemCreate(BaseModel):
    product_id: int = Field(..., gt=0, description="Product ID")
    variant_id: Optional[int] = Field(None, gt=0, description="Product variant ID (optional)")
    quantity: int = Field(..., gt=0, description="Quantity to order")


class OrderItemCreateByCode(BaseModel):
    product_code: str = Field(..., min_length=1, description="Product code")
    variant_id: Optional[int] = Field(None, gt=0, description="Product variant ID (optional)")
    quantity: int = Field(..., gt=0, description="Quantity to order")

class OrderItemCreateBySku(BaseModel):
    sku_code: str = Field(..., min_length=1, description="SKU code")
    quantity: int = Field(..., gt=0, description="Quantity to order")


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    variant_id: Optional[int]
    product_name: str
    product_code: str
    product_price: float
    product_image_url: Optional[str]
    # New variant fields
    sku_code: Optional[str] = None
    variant_attributes_snapshot: Optional[dict] = None
    unit_price_snapshot: Optional[float] = None
    # Legacy variant fields
    variant_size: Optional[str]
    variant_color: Optional[str]
    quantity: int
    unit_price: float
    total_price: float
    
    class Config:
        from_attributes = True


class OrderDraftIn(BaseModel):
    customer_name: str = Field(..., min_length=1, description="Customer name")
    contact: str = Field(..., min_length=1, description="Contact info (phone/telegram)")
    items: List[OrderItemCreate] = Field(..., min_items=1, description="Order items")
    note: Optional[str] = Field(None, description="Additional notes")


class OrderDraftByCodeIn(BaseModel):
    customer_code: Optional[str] = Field(None, description="Customer code (if existing customer)")
    customer_name: str = Field(..., min_length=1, description="Customer name")
    contact: str = Field(..., min_length=1, description="Contact info (phone/telegram)")
    items: List[OrderItemCreateByCode] = Field(..., min_items=1, description="Order items by product code")
    note: Optional[str] = Field(None, description="Additional notes")

class OrderDraftBySkuIn(BaseModel):
    customer_code: Optional[str] = Field(None, description="Customer code (if existing customer)")
    customer_name: str = Field(..., min_length=1, description="Customer name")
    contact: str = Field(..., min_length=1, description="Contact info (phone/telegram)")
    items: List[OrderItemCreateBySku] = Field(..., min_items=1, description="Order items by SKU code")
    note: Optional[str] = Field(None, description="Additional notes")


class OrderConfirmIn(BaseModel):
    order_id: int = Field(..., gt=0, description="Order ID to confirm")


class OrderUpdateStatusIn(BaseModel):
    status: Literal["pending", "approved", "sold", "cancelled"] = Field(..., description="New order status")


class OrderOut(BaseModel):
    id: int
    order_number: str
    order_code: Optional[str] = None
    customer_name: str
    customer_phone: str
    customer_address: Optional[str]
    customer_instagram: Optional[str]
    total_amount: float
    shipping_cost: float
    discount_amount: float
    final_amount: float
    status: OrderStatus
    payment_status: PaymentStatus
    payment_method: Optional[str]
    shipping_method: Optional[str]
    tracking_number: Optional[str]
    estimated_delivery: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime]
    shipped_at: Optional[datetime]
    delivered_at: Optional[datetime]
    admin_notes: Optional[str]
    customer_notes: Optional[str]
    customer_snapshot: Optional[dict] = None
    items_count: Optional[int] = 0
    
    # Include items
    items: List[OrderItemOut] = []
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class OrderSummary(BaseModel):
    id: int
    order_number: str
    customer_name: str
    total_amount: float
    status: OrderStatus
    created_at: datetime
    items_count: int
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 