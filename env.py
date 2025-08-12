# backend/env.py
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (the folder that contains `backend/`)
ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=False)

def get_required_env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        logging.error(f"Missing required env var: {name}")
        raise RuntimeError(f"{name} is not set")
    return val

def assert_openai_key():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        logging.error("OPENAI_API_KEY is missing. Create a .env in project root and set it.")
        raise RuntimeError("OPENAI_API_KEY is missing")
    # Masked log
    tail = key[-6:] if len(key) >= 6 else "******"
    logging.info(f"OPENAI_API_KEY loaded (…{tail})")

def allow_mock() -> bool:
    return os.getenv("ALLOW_MOCK", "0") in ("1", "true", "True") 