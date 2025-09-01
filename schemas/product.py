from pydantic import BaseModel, Field, field_validator, computed_field
from datetime import datetime
from typing import Optional, List, Dict
import json
from models import Product as ProductModel


class VariantBase(BaseModel):
    size: Optional[str] = Field(None, description="Product size (e.g., S, M, L, XL, 43, 44)")
    color: Optional[str] = Field(None, description="Product color (e.g., قرمز, آبی, مشکی)")
    sku: Optional[str] = Field(None, description="Stock Keeping Unit")
    stock: int = Field(0, ge=0, description="Available stock for this variant")
    price_delta: float = Field(0.0, description="Price adjustment for this variant")


class VariantCreate(VariantBase):
    product_id: int = Field(..., gt=0, description="Product ID")


class VariantUpdate(BaseModel):
    size: Optional[str] = None
    color: Optional[str] = None
    sku: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)
    price_delta: Optional[float] = None


class VariantOut(VariantBase):
    id: int
    product_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    description: Optional[str] = Field(None, max_length=1000, description="Product description")
    price: float = Field(..., gt=0, description="Product price")
    stock: int = Field(0, ge=0, description="Available stock quantity")
    low_stock_threshold: Optional[int] = Field(5, gt=0, description="Low stock threshold (default: 5)")
    category_id: int = Field(..., gt=0, description="Category ID")
    image_url: Optional[str] = Field(None, description="Product image URL")
    thumbnail_url: Optional[str] = Field(None, description="Product thumbnail URL (preferred for list views)")
    sizes: Optional[List[str]] = Field(None, description="List of available sizes")
    available_sizes: Optional[List[str]] = Field(None, description="List of available sizes")
    available_colors: Optional[List[str]] = Field(None, description="List of available colors")
    tags: Optional[str] = Field(None, max_length=500, description="Comma-separated tags")
    labels: Optional[List[str]] = Field(None, description="List of product labels")
    attributes: Optional[Dict[str, List[str]]] = Field(None, description="Product attributes (key -> list of values)")
    labels: Optional[List[str]] = Field(None, description="List of product labels")
    attributes: Optional[Dict[str, List[str]]] = Field(None, description="Product attributes (key -> list of values)")
    is_active: bool = Field(True, description="Product active status")
    
    @field_validator('sizes', mode='before')
    @classmethod
    def validate_sizes(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            # If it's already a string, split it and return as list
            return [s.strip() for s in v.split(',') if s.strip()]
        if isinstance(v, list):
            # If it's a list, validate each item
            return [str(s).strip() for s in v if str(s).strip()]
        return None
    
    @field_validator('available_sizes', 'available_colors', mode='before')
    @classmethod
    def validate_arrays(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            # If it's a string, split by comma and normalize
            items = [s.strip() for s in v.split(',') if s.strip()]
            return [normalize_persian_digits(item) for item in items]
        if isinstance(v, list):
            # If it's a list, normalize each item
            return [normalize_persian_digits(str(s).strip()) for s in v if str(s).strip()]
        return []
    
    @field_validator('available_colors', mode='before')
    @classmethod
    def validate_colors(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            # If it's a string, split by comma and normalize
            items = [s.strip() for s in v.split(',') if s.strip()]
            return [normalize_color(item) for item in items]
        if isinstance(v, list):
            # If it's a list, normalize each item
            return [normalize_color(str(s).strip()) for s in v if str(s).strip()]
        return []


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, gt=0)
    category_id: Optional[int] = Field(None, gt=0)
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    sizes: Optional[List[str]] = Field(None, description="List of available sizes")
    available_sizes: Optional[List[str]] = Field(None, description="List of available sizes")
    available_colors: Optional[List[str]] = Field(None, description="List of available colors")
    tags: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    
    @field_validator('sizes', mode='before')
    @classmethod
    def validate_sizes(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            # If it's already a string, split it and return as list
            return [s.strip() for s in v.split(',') if s.strip()]
        if isinstance(v, list):
            # If it's a list, validate each item
            return [str(s).strip() for s in v if str(s).strip()]
        return None
    
    @field_validator('available_sizes', 'available_colors', mode='before')
    @classmethod
    def validate_arrays(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            # If it's a string, split by comma and normalize
            items = [s.strip() for s in v.split(',') if s.strip()]
            return [normalize_persian_digits(item) for item in items]
        if isinstance(v, list):
            # If it's a list, normalize each item
            return [normalize_persian_digits(str(s).strip()) for s in v if str(s).strip()]
        return []
    
    @field_validator('available_colors', mode='before')
    @classmethod
    def validate_colors(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            # If it's a string, split by comma and normalize
            items = [s.strip() for s in v.split(',') if s.strip()]
            return [normalize_color(item) for item in items]
        if isinstance(v, list):
            # If it's a list, normalize each item
            return [normalize_color(str(s).strip()) for s in v if str(s).strip()]
        return []


class ProductOut(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str]
    price: float
    stock: int
    low_stock: bool
    low_stock_threshold: int
    category_id: int
    category_name: str
    image_url: Optional[str]
    thumbnail_url: Optional[str] = None
    tags: Optional[str]
    labels: List[str] = []  # Product labels
    attributes: Dict[str, List[str]] = {}  # Product attributes
    sizes: List[str] = []  # Will be populated from database string
    available_sizes: List[str] = []  # Structured sizes from JSON
    available_colors: List[str] = []  # Structured colors from JSON
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # New fields for variants
    variants: List[VariantOut] = []
    total_stock: int = 0  # Computed field: sum of variant stocks or product stock
    
    @field_validator('sizes', mode='before')
    @classmethod
    def validate_sizes_output(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            # Convert comma-separated string to list
            return [s.strip() for s in v.split(',') if s.strip()]
        if isinstance(v, list):
            return v
        return []
    
    @field_validator('available_sizes', 'available_colors', mode='before')
    @classmethod
    def validate_json_arrays(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            try:
                # Try to parse as JSON
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
                return []
            except (json.JSONDecodeError, TypeError):
                return []
        if isinstance(v, list):
            return v
        return []
    
    @field_validator('labels', mode='before')
    @classmethod
    def validate_labels(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            try:
                # Try to parse as JSON
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
                return []
            except (json.JSONDecodeError, TypeError):
                return []
        if isinstance(v, list):
            return v
        return []
    
    @field_validator('attributes', mode='before')
    @classmethod
    def validate_attributes(cls, v):
        if v is None:
            return {}
        if isinstance(v, str):
            try:
                # Try to parse as JSON
                parsed = json.loads(v)
                if isinstance(parsed, dict):
                    return parsed
                return {}
            except (json.JSONDecodeError, TypeError):
                return {}
        if isinstance(v, dict):
            return v
        return {}
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Product search result (minimal info for suggestions)
class ProductSearchResult(BaseModel):
    id: int
    code: str
    name: str
    price: float
    total_stock: int
    category_name: str
    thumbnail_url: Optional[str] = None
    
    class Config:
        from_attributes = True


# Product details for Q&A (full info with variants)
class ProductDetails(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str]
    price: float
    total_stock: int
    category: dict  # {id, name, prefix}
    images: List[str]  # [thumbnail_url, image_url]
    variants: List[VariantOut]
    available_sizes: List[str]
    available_colors: List[str]
    tags: Optional[str]
    
    class Config:
        from_attributes = True


# Utility functions for normalization
def normalize_persian_digits(text: str) -> str:
    """Convert Persian digits to ASCII digits."""
    persian_to_ascii = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    }
    for persian, ascii in persian_to_ascii.items():
        text = text.replace(persian, ascii)
    return text


def normalize_color(text: str) -> str:
    """Normalize color text for matching."""
    return text.lower().strip() 