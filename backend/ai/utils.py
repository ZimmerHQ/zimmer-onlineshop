"""
Utility functions for the sales agent
"""
import re
import random
from typing import List, Dict, Any

# Constants
PRICE_UNIT = "تومان"
YES_RE = re.compile(r"(تایید|تایید میکنم|اوکی|باشه|بله|بزن بریم|بخر|خوبه|Yes|OK)", re.I)
CANCEL_RE = re.compile(r"(لغو|بیخیال|cancel)", re.I)
GREET_RE = re.compile(r"\b(hi|hello|سلام|درود|hey|هلو|الو)\b", re.I)
CODE_RE = re.compile(r"\b([A-Za-z]\d{3,}|[A-Za-z]{1,3}\d{2,}|[A-Z0-9]{4,})\b")

def extract_search_terms(message: str) -> str:
    """Extract key search terms from user message, removing question words and common phrases"""
    question_words = [
        "داری", "دارید", "هست", "هستید", "می‌خوای", "می‌خواهید", 
        "می‌خوایم", "می‌خواهیم", "چی", "چه", "کدام", "کدوم",
        "؟", "?", "!", "!", ":", ":", "،", ",", ".", "."
    ]
    
    cleaned = message.strip()
    for word in question_words:
        cleaned = cleaned.replace(word, " ").strip()
    
    return " ".join(cleaned.split())

def format_price(price: float) -> str:
    """Format price with Persian number formatting"""
    try:
        n = int(float(price))
        s = f"{n:,}".replace(",", "٬")
    except Exception:
        s = str(price)
    return f"{s} {PRICE_UNIT}".strip()

def format_products(products: List[Dict[str, Any]], with_examples: bool = True) -> str:
    """Format a list of products for display"""
    if not products:
        return "فعلاً محصولی برای نمایش نداریم. می‌تونی اسم یا کد محصول رو بگی."
    
    lines = []
    for i, p in enumerate(products, 1):
        name = p.get("name") or "—"
        code = p.get("code") or "—"
        price = format_price(p.get("price", 0))
        lines.append(f"{i}) {name} (کد {code}) — {price}")
    
    body = "\n".join(lines)
    if with_examples:
        body += "\n\nمثال‌ها: «کفش مشکی ۴۳»، «کد A0001»، «شلوار جین ارزان»"
    
    return body

def random_no_match() -> str:
    """Get a random no-match message"""
    from .prompts import NO_MATCH_TEMPLATES
    return random.choice(NO_MATCH_TEMPLATES)

def is_greeting(message: str) -> bool:
    """Check if message is a greeting or very short (but not a number)"""
    import re
    # Don't treat single digits as greetings
    if re.match(r'^\d+$', message.strip()):
        return False
    return bool(GREET_RE.search(message) or len(message.strip()) <= 2)

def is_cancellation(message: str) -> bool:
    """Check if message is a cancellation"""
    return bool(CANCEL_RE.search(message))

def extract_product_code(message: str) -> str:
    """Extract product code from message"""
    match = CODE_RE.search(message)
    return match.group(1) if match else None

def is_confirmation(message: str) -> bool:
    """Check if message is a confirmation"""
    return bool(YES_RE.search(message))
