from openai import OpenAI
from backend.config import OPENAI_API_KEY
from typing import Optional
import logging

# Configure OpenAI client
client = None
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)

def ask_gpt(message: str) -> str:
    """
    Ask GPT a question and return the response.
    Uses OpenAI's ChatCompletion API with Persian-friendly system prompt.
    """
    if not OPENAI_API_KEY or not client:
        logging.error("❌ No OpenAI API key or client available")
        return "متاسفم، الان نمی‌تونم پاسخ بدم. لطفاً دوباره تلاش کنید."
    
    # Determine model - use gpt-4 if available, else gpt-3.5-turbo
    try:
        # Try to use gpt-4 first
        model = "gpt-4"
        logging.info(f"🤖 Attempting GPT call with model: {model}")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant for an online shop. Answer in Persian."},
                {"role": "user", "content": message}
            ],
            max_tokens=500,
            temperature=0.7,
            timeout=30  # Add timeout
        )
        
        result = response.choices[0].message.content.strip()
        logging.info(f"✅ GPT response received: {result[:50]}...")
        return result
        
    except Exception as e:
        logging.error(f"❌ GPT-4 failed: {type(e).__name__}: {str(e)}")
        # If gpt-4 fails, try gpt-3.5-turbo
        try:
            model = "gpt-3.5-turbo"
            logging.info(f"🤖 Retrying with model: {model}")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for an online shop. Answer in Persian."},
                    {"role": "user", "content": message}
            ],
                max_tokens=500,
                temperature=0.7,
                timeout=30  # Add timeout
            )
            
            result = response.choices[0].message.content.strip()
            logging.info(f"✅ GPT-3.5 response received: {result[:50]}...")
            return result
            
        except Exception as e2:
            logging.error(f"❌ GPT-3.5 also failed: {type(e2).__name__}: {str(e2)}")
            # Return a more specific error message
            if "timeout" in str(e2).lower() or "connection" in str(e2).lower():
                return "متاسفم، مشکل اتصال به سرور. لطفاً دوباره تلاش کنید."
            elif "quota" in str(e2).lower() or "billing" in str(e2).lower():
                return "متاسفم، مشکل در سرویس. لطفاً دوباره تلاش کنید."
            else:
                return f"متاسفم، خطا در سرویس: {type(e2).__name__}"

