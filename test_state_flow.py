#!/usr/bin/env python3
"""
Test the complete state flow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db
from services.chat_tools import handle_tool
from services.chat_state import get_state, set_state, clear_state

def test_state_flow():
    """Test the complete state flow"""
    print("🧪 Testing complete state flow...")
    
    conv_id = "test123"
    db = next(get_db())
    
    # Clear any existing state
    clear_state(conv_id)
    print(f"Initial state: {get_state(conv_id)}")
    
    # Step 1: Search for product (A0001)
    print("\n🔍 Step 1: Searching for product A0001...")
    reply, extra = handle_tool(
        action="SEARCH_PRODUCTS",
        slots={"code": "A0001"},
        db=db,
        rid="test123",
        conv_id=conv_id,
        message_text="A0001"
    )
    print(f"Reply: {reply}")
    print(f"Extra: {extra}")
    print(f"State after search: {get_state(conv_id)}")
    
    # Step 2: Try to create order
    print("\n🛒 Step 2: Trying to create order...")
    reply, extra = handle_tool(
        action="CREATE_ORDER",
        slots={},
        db=db,
        rid="test123",
        conv_id=conv_id,
        message_text="همینو میخوام"
    )
    print(f"Reply: {reply}")
    print(f"Extra: {extra}")
    print(f"State after create order: {get_state(conv_id)}")
    
    print("\n✅ State flow test complete!")

if __name__ == "__main__":
    test_state_flow() 