#!/usr/bin/env python3
"""
Test the LLM directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gpt_service import call_llm_for_action

def test_llm():
    """Test the LLM directly"""
    print("🧪 Testing LLM directly...")
    
    # Test 1: Product search query
    print("\n🔍 Test 1: 'شلوار دارین؟'")
    result1 = call_llm_for_action("شلوار دارین؟")
    print(f"Result: {result1}")
    
    # Test 2: Order creation query
    print("\n🛒 Test 2: 'همینو میخوام'")
    result2 = call_llm_for_action("همینو میخوام")
    print(f"Result: {result2}")
    
    # Test 3: Simple order query
    print("\n🛒 Test 3: 'میخوام'")
    result3 = call_llm_for_action("میخوام")
    print(f"Result: {result3}")
    
    print("\n✅ LLM test complete!")

if __name__ == "__main__":
    test_llm() 