from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
import json


# Telegram Webhook Input Schema
class TelegramWebhookIn(BaseModel):
    update_id: int
    message: Optional[dict] = None
    callback_query: Optional[dict] = None
    
    class Config:
        extra = "allow"  # Allow extra fields from Telegram


# Telegram Config Schemas
class TelegramConfigCreate(BaseModel):
    bot_token: str = Field(..., description="Telegram Bot Token")
    webhook_url: str = Field(..., description="Webhook URL for receiving updates")
    webhook_secret: str = Field(..., description="Secret for webhook validation")
    is_active: bool = Field(True, description="Whether the bot is active")


class TelegramConfigUpdate(BaseModel):
    bot_token: Optional[str] = Field(None, description="Telegram Bot Token")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for receiving updates")
    webhook_secret: Optional[str] = Field(None, description="Secret for webhook validation")
    is_active: Optional[bool] = Field(None, description="Whether the bot is active")


class TelegramConfigOut(BaseModel):
    id: int
    bot_token: str
    webhook_url: str
    webhook_secret: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Telegram User Schemas
class TelegramUserOut(BaseModel):
    id: int
    telegram_user_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    language_code: Optional[str]
    first_seen: datetime
    last_seen: datetime
    visits_count: int
    phone: Optional[str]
    note: Optional[str]
    is_blocked: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TelegramUserSummary(BaseModel):
    id: int
    telegram_user_id: int
    username: Optional[str]
    first_name: Optional[str]
    visits_count: int
    last_seen: datetime
    phone: Optional[str]
    is_blocked: bool


# Telegram Message Schemas
class TelegramMessageOut(BaseModel):
    id: int
    user_id: int
    direction: str  # "in" or "out"
    text: str
    payload_json: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# FAQ Schemas
class FAQCreate(BaseModel):
    question: str = Field(..., min_length=1, description="FAQ question")
    answer: str = Field(..., min_length=1, description="FAQ answer")
    tags: Optional[str] = Field(None, description="Comma-separated tags")
    is_active: bool = Field(True, description="Whether FAQ is active")


class FAQUpdate(BaseModel):
    question: Optional[str] = Field(None, min_length=1, description="FAQ question")
    answer: Optional[str] = Field(None, min_length=1, description="FAQ answer")
    tags: Optional[str] = Field(None, description="Comma-separated tags")
    is_active: Optional[bool] = Field(None, description="Whether FAQ is active")


class FAQOut(BaseModel):
    id: int
    question: str
    answer: str
    tags: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Sales Report Schemas
class ReportTriggerIn(BaseModel):
    period: str = Field(..., description="Report period: weekly or monthly")
    start_date: Optional[date] = Field(None, description="Custom start date")
    end_date: Optional[date] = Field(None, description="Custom end date")


class SalesReportOut(BaseModel):
    id: int
    period: str
    start_date: date
    end_date: date
    totals_json: str
    generated_at: datetime
    
    class Config:
        from_attributes = True


class SalesReportSummary(BaseModel):
    id: int
    period: str
    start_date: date
    end_date: date
    generated_at: datetime
    
    # Parsed totals for easy access
    total_orders: int
    total_revenue: float
    avg_order_value: float
    
    class Config:
        from_attributes = True


# Bot Response Schemas
class BotResponse(BaseModel):
    text: str
    reply_markup: Optional[dict] = None  # Inline keyboard markup


# Telegram API Response Schemas
class TelegramApiResponse(BaseModel):
    ok: bool
    result: Optional[dict] = None
    description: Optional[str] = None 