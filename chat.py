from .gpt_assistant import gpt_assistant
from .database import SessionLocal
import asyncio

async def chat_with_gpt():
    """Interactive chat with GPT assistant"""
    print("🤖 GPT Assistant Chat - Type 'quit' to exit")
    print("=" * 50)
    
    db = SessionLocal()
    conversation_context = None
    
    try:
        while True:
            msg = input("You: ")
            if msg.lower() == "quit":
                break
            
            # Process message with GPT assistant
            result = await gpt_assistant.process_message(
                db=db,
                user_message=msg,
                user_id=1,  # Default user ID
                conversation_context=conversation_context
            )
            
            print(f"🤖 Assistant: {result['response']}")
            
            # Update conversation context
            conversation_context = result.get('conversation_context', {})
            
            # Show action if any
            if result.get('action'):
                print(f"🎯 Action: {result['action']}")
            
            # Show products if any
            if result.get('products'):
                print(f"📦 Products found: {len(result['products'])}")
            
            print("-" * 30)
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(chat_with_gpt())