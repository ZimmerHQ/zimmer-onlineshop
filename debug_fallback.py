#!/usr/bin/env python3
"""
Debug script to test the fallback mechanism in chat_tools.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.chat_tools import handle_tool
from database import get_db
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_fallback():
    """Test the fallback mechanism"""
    print("🧪 Testing fallback mechanism...")
    
    # Get database session
    db = next(get_db())
    conversation_id = "test-conversation"
    
    # Test case 1: Persian product query that should trigger fallback
    print("\n📝 Test 1: Persian product query")
    action = "SMALL_TALK"
    slots = {}
    original_message = "شلوار دارین؟"
    rid = "test_123"
    
    try:
        reply, extra = handle_tool(action, slots, db, rid, original_message, conversation_id)
        print(f"✅ Reply: {reply}")
        print(f"✅ Extra: {extra}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test case 2: English product query
    print("\n📝 Test 2: English product query")
    action = "SMALL_TALK"
    slots = {}
    original_message = "do you have pants?"
    rid = "test_456"
    
    try:
        reply, extra = handle_tool(action, slots, db, rid, original_message, conversation_id)
        print(f"✅ Reply: {reply}")
        print(f"✅ Extra: {extra}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test case 3: Normal SEARCH_PRODUCTS action
    print("\n📝 Test 3: Normal SEARCH_PRODUCTS action")
    action = "SEARCH_PRODUCTS"
    slots = {"q": "شلوار"}
    original_message = "شلوار دارین؟"
    rid = "test_789"
    
    try:
        reply, extra = handle_tool(action, slots, db, rid, original_message, conversation_id)
        print(f"✅ Reply: {reply}")
        print(f"✅ Extra: {extra}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test case 4: Order creation flow
    print("\n📝 Test 4: Order creation flow")
    action = "CREATE_ORDER"
    slots = {}
    original_message = "همینو میخوام"
    rid = "test_order"
    
    try:
        reply, extra = handle_tool(action, slots, db, rid, original_message, conversation_id)
        print(f"✅ Reply: {reply}")
        print(f"✅ Extra: {extra}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fallback() 