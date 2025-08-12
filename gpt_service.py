from openai import OpenAI
from config import OPENAI_API_KEY
from typing import Optional

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
        return "متاسفم، الان نمی‌تونم پاسخ بدم. لطفاً دوباره تلاش کنید."
    
    # Determine model - use gpt-4 if available, else gpt-3.5-turbo
    try:
        # Try to use gpt-4 first
        model = "gpt-4"
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant for an online shop. Answer in Persian."},
                {"role": "user", "content": message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        # If gpt-4 fails, try gpt-3.5-turbo
        try:
            model = "gpt-3.5-turbo"
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for an online shop. Answer in Persian."},
                    {"role": "user", "content": message}
            ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e2:
            print(f"Error calling GPT: {e2}")
            return "متاسفم، الان نمی‌تونم پاسخ بدم. لطفاً دوباره تلاش کنید."
