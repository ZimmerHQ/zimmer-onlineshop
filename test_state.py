#!/usr/bin/env python3
"""
Test chat state management
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.chat_state import get_state, set_state, clear_state

def test_state():
    """Test basic state operations"""
    print("🧪 Testing chat state management...")
    
    conv_id = "test123"
    
    # Test 1: Get initial state
    state = get_state(conv_id)
    print(f"Initial state: {state}")
    
    # Test 2: Set state
    test_state = {"selected_product": {"id": 1, "name": "Test Product"}, "stage": "await_confirm"}
    set_state(conv_id, test_state)
    print(f"Set state: {test_state}")
    
    # Test 3: Get state again
    state = get_state(conv_id)
    print(f"Retrieved state: {state}")
    
    # Test 4: Update state
    set_state(conv_id, {"wanted": {"qty": 2}})
    state = get_state(conv_id)
    print(f"Updated state: {state}")
    
    # Test 5: Clear state
    clear_state(conv_id)
    state = get_state(conv_id)
    print(f"After clear: {state}")
    
    print("✅ State management test complete!")

if __name__ == "__main__":
    test_state() 