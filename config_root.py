import os
from dotenv import load_dotenv

# Load environment variables from .env file at project root
load_dotenv()

# Load required API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Zimmer integration settings
ZIMMER_SERVICE_TOKEN = os.getenv("ZIMMER_SERVICE_TOKEN")
CHAT_BUDGET_SECONDS = int(os.getenv("CHAT_BUDGET_SECONDS", "7"))
CHAT_API_TIMEOUT = int(os.getenv("CHAT_API_TIMEOUT", "9"))
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "6"))
AGENT_MAX_ITERS = int(os.getenv("AGENT_MAX_ITERS", "3"))
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-3.5-turbo")

# Config override hook for future config servers
def load_config_override():
    """Hook for future config server integration (AWS SSM, Vault, etc.)"""
    # This is where we would override config values from external sources
    # For now, just return the current config
    return {
        "ZIMMER_SERVICE_TOKEN": ZIMMER_SERVICE_TOKEN,
        "CHAT_BUDGET_SECONDS": CHAT_BUDGET_SECONDS,
        "CHAT_API_TIMEOUT": CHAT_API_TIMEOUT,
        "LLM_TIMEOUT": LLM_TIMEOUT,
        "AGENT_MAX_ITERS": AGENT_MAX_ITERS,
        "CHAT_MODEL": CHAT_MODEL
    }

# Check for missing keys and print warnings
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY environment variable is missing")

if not TELEGRAM_TOKEN:
    print("Warning: TELEGRAM_TOKEN environment variable is missing")

if not ZIMMER_SERVICE_TOKEN:
    print("Warning: ZIMMER_SERVICE_TOKEN environment variable is missing")
