#!/usr/bin/env python3
"""
Test if all models are being imported and registered properly.
"""
from models import Base

def test_imports():
    """Test if all models are imported and registered."""
    try:
        print("🔍 Testing model imports...")
        
        # Import all models explicitly
        from models import (
            User, Message, ChatMessage, Order, OrderItem, 
            Receipt, FallbackQuestion, BotConfig, Category, Product
        )
        print("✅ All models imported successfully")
        
        # Check Base metadata
        print(f"📋 Base metadata tables: {list(Base.metadata.tables.keys())}")
        
        # Check if specific tables are registered
        expected_tables = ['users', 'messages', 'chat_messages', 'orders', 'order_items', 
                          'receipts', 'fallback_questions', 'bot_configs', 'categories', 'products']
        
        for table in expected_tables:
            if table in Base.metadata.tables:
                print(f"✅ Table '{table}' registered")
            else:
                print(f"❌ Table '{table}' NOT registered")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_imports() 