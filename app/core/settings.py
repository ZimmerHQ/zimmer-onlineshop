"""
Zimmer integration settings and configuration.
Extends the existing backend configuration with Zimmer-specific settings.
"""

import os
from typing import Optional
from backend.config import *  # Import existing configuration

# Zimmer Integration Settings
SERVICE_TOKEN: Optional[str] = os.getenv("SERVICE_TOKEN")
SERVICE_TOKEN_HASH: Optional[str] = os.getenv("SERVICE_TOKEN_HASH")
PLATFORM_API_URL: Optional[str] = os.getenv("PLATFORM_API_URL")
NODE_ENV: str = os.getenv("NODE_ENV", "development")
SEED_TOKENS: int = int(os.getenv("SEED_TOKENS", "0"))
APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")

# Zimmer Configuration Settings
DEFAULT_AUTOMATION_ID: str = os.getenv("DEFAULT_AUTOMATION_ID", "18")
HTTP_TIMEOUT: float = float(os.getenv("HTTP_TIMEOUT", "30.0"))
WEBHOOK_PATH_TEMPLATE: str = os.getenv("WEBHOOK_PATH_TEMPLATE", "/webhook/{user_id}")

# Database field length limits (configurable for different database types)
USER_ID_MAX_LENGTH: int = int(os.getenv("USER_ID_MAX_LENGTH", "255"))
AUTOMATION_ID_MAX_LENGTH: int = int(os.getenv("AUTOMATION_ID_MAX_LENGTH", "255"))
EMAIL_MAX_LENGTH: int = int(os.getenv("EMAIL_MAX_LENGTH", "255"))
NAME_MAX_LENGTH: int = int(os.getenv("NAME_MAX_LENGTH", "255"))
SESSION_ID_MAX_LENGTH: int = int(os.getenv("SESSION_ID_MAX_LENGTH", "255"))
REASON_MAX_LENGTH: int = int(os.getenv("REASON_MAX_LENGTH", "255"))

# Validate required settings
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is required")

# Print Zimmer configuration summary
def print_zimmer_config_summary():
    """Print a summary of the Zimmer configuration."""
    print("🔧 Zimmer Configuration Summary:")
    print(f"  Service Token: {'Configured' if SERVICE_TOKEN else 'Not configured'}")
    print(f"  Service Token Hash: {'Configured' if SERVICE_TOKEN_HASH else 'Not configured'}")
    print(f"  Platform API URL: {PLATFORM_API_URL or 'Not configured'}")
    print(f"  Node Environment: {NODE_ENV}")
    print(f"  Seed Tokens: {SEED_TOKENS}")
    print(f"  App Version: {APP_VERSION}")
    print(f"  Default Automation ID: {DEFAULT_AUTOMATION_ID}")
    print(f"  HTTP Timeout: {HTTP_TIMEOUT}s")
    print(f"  Webhook Path Template: {WEBHOOK_PATH_TEMPLATE}")

if __name__ == "__main__":
    print_zimmer_config_summary()

