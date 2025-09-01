from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
import re


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Category name")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Category name")
    prefix: Optional[str] = Field(None, description="Category prefix (1-2 uppercase letters)")
    
    @validator('prefix')
    def validate_prefix(cls, v):
        if v is not None:
            if not re.match(r'^[A-Z]{1,2}$', v):
                raise ValueError('Prefix must be 1-2 uppercase letters [A-Z]')
        return v


class CategoryOut(BaseModel):
    id: int
    name: str
    prefix: str
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 