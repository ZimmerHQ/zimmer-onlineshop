from pydantic import BaseModel
from typing import Optional

class CustomerUpdateIn(BaseModel):
    """Schema for updating customer information"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    notes: Optional[str] = None

class CustomerOut(BaseModel):
    """Schema for customer output"""
    customer_id: int
    customer_code: Optional[str] = None
    first_name: str
    last_name: str
    phone: str
    address: str
    postal_code: str
    notes: Optional[str] = None
    total_spent: Optional[float] = None
    orders_count: Optional[int] = None
    last_order_at: Optional[str] = None

class CustomerCreateIn(BaseModel):
    """Schema for creating a new customer"""
    first_name: str
    last_name: str
    phone: str
    address: str
    postal_code: str
    notes: Optional[str] = ""
