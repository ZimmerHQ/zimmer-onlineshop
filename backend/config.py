"""
Configuration settings for the Zimmer backend application.
Supports both local development and production deployment.
"""

import os
from typing import Optional

# Environment
ENV = os.getenv("ENV", "development")
IS_PRODUCTION = ENV == "production"

# Database Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./app.db" if not IS_PRODUCTION else None
)

# API Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if IS_PRODUCTION and not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is required in production")

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET")

# CORS Configuration
CORS_ORIGINS = [
    FRONTEND_URL,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8006",  # Add local development port
    "http://127.0.0.1:8006",  # Add local development port
]

# Add any additional CORS origins from environment
if os.getenv("ADDITIONAL_CORS_ORIGINS"):
    CORS_ORIGINS.extend(os.getenv("ADDITIONAL_CORS_ORIGINS", "").split(","))

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if IS_PRODUCTION else "DEBUG")

# Database connection pool settings
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))

# API Rate Limiting
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

# File Upload
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./static/uploads")

# Print configuration summary (non-sensitive)
def print_config_summary():
    """Print a summary of the current configuration."""
    print("🔧 Configuration Summary:")
    print(f"  Environment: {ENV}")
    print(f"  Database: {'PostgreSQL' if IS_PRODUCTION else 'SQLite'}")
    print(f"  Backend URL: {BACKEND_URL}")
    print(f"  Frontend URL: {FRONTEND_URL}")
    print(f"  OpenAI API: {'Configured' if OPENAI_API_KEY else 'Not configured'}")
    print(f"  Telegram Bot: {'Configured' if TELEGRAM_BOT_TOKEN else 'Not configured'}")
    print(f"  CORS Origins: {CORS_ORIGINS}")

if __name__ == "__main__":
    print_config_summary() 