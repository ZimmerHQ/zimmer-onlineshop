from openai import OpenAI
from backend.config import OPENAI_API_KEY
from typing import Optional

# Configure OpenAI client (same as gpt_service)
client = None
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)

def detect_intent(message: str) -> str:
    """
    Detect the intent of a message using GPT.
    Returns: 'question', 'order', 'receipt', 'chitchat', or 'fallback'
    """
    if not message or not message.strip():
        return "fallback"
    
    # Simple keyword-based fallback for common cases
    message_lower = message.lower().strip()
    
    # Check for order-related keywords
    order_keywords = ['خرید', 'سفارش', 'کفش', 'لباس', 'قیمت', 'چقدر', 'میخوام', 'می‌خوام']
    if any(keyword in message_lower for keyword in order_keywords):
        return "order"
    
    # Check for greeting keywords
    greeting_keywords = ['سلام', 'هی', 'درود', 'خوبی', 'چطوری']
    if any(keyword in message_lower for keyword in greeting_keywords):
        return "chitchat"
    
    # If no simple keywords match, try GPT classification
    if not OPENAI_API_KEY or not client:
        return "question"  # Default to question if no API key
    
    try:
        # Use GPT to classify the intent
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use 3.5-turbo for faster response
            messages=[
                {
                    "role": "system", 
                    "content": "You are an intent detection engine for a Persian shopping assistant. Classify the message type. Return only one word from: question, order, receipt, chitchat, fallback"
                },
                {
                    "role": "user", 
                    "content": message
                }
            ],
            max_tokens=10,  # Very short response
            temperature=0.1  # Low temperature for consistent classification
        )
        
        # Extract the response and clean it
        content = response.choices[0].message.content
        if not content:
            return "question"  # Default to question
            
        intent = content.strip().lower()
        
        # Validate the response is one of the allowed intents
        allowed_intents = ["question", "order", "receipt", "chitchat", "fallback"]
        if intent in allowed_intents:
            return intent
        else:
            return "question"  # Default to question
            
    except Exception as e:
        print(f"Error in intent detection: {e}")
        return "question"  # Default to question