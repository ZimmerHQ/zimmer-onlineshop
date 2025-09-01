#!/usr/bin/env python3
"""
Test import and LLM call
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the same way the server does
from gpt_service import call_llm_for_action

def test_import():
    """Test the import and LLM call"""
    print("🧪 Testing import and LLM call...")
    
    # Test the LLM call
    result = call_llm_for_action("همینو میخوام")
    print(f"Result for 'همینو میخوام': {result}")
    
    print("✅ Import test complete!")

if __name__ == "__main__":
    test_import() 