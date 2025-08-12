import os
from dotenv import load_dotenv

# Load environment variables from .env file at project root
load_dotenv()

# Load required API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Check for missing keys and print warnings
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY environment variable is missing")

if not TELEGRAM_TOKEN:
    print("Warning: TELEGRAM_TOKEN environment variable is missing")
