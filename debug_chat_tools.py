#!/usr/bin/env python3
"""
Debug script for chat tools
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db
from services.chat_tools import handle_tool
from services.product_service import get_by_code, to_product_out

def test_get_by_code():
    """Test get_by_code function"""
    print("🔍 Testing get_by_code...")
    db = next(get_db())
    try:
        product = get_by_code(db, "A0001")
        if product:
            print(f"✅ Found product: {product.name} (ID: {product.id})")
            return product
        else:
            print("❌ Product not found")
            return None
    except Exception as e:
        print(f"❌ Error in get_by_code: {e}")
        return None

def test_to_product_out():
    """Test to_product_out function"""
    print("🔍 Testing to_product_out...")
    db = next(get_db())
    try:
        product = get_by_code(db, "A0001")
        if product:
            po = to_product_out(db, product)
            print(f"✅ ProductOut created: {po.name} (ID: {po.id})")
            return po
        else:
            print("❌ No product to convert")
            return None
    except Exception as e:
        print(f"❌ Error in to_product_out: {e}")
        return None

def test_handle_tool_search():
    """Test handle_tool with SEARCH_PRODUCTS"""
    print("🔍 Testing handle_tool SEARCH_PRODUCTS...")
    db = next(get_db())
    try:
        reply, extra = handle_tool(
            action="SEARCH_PRODUCTS",
            slots={"code": "A0001"},
            db=db,
            rid="test123",
            conv_id="test123",
            message_text="A0001"
        )
        print(f"✅ Reply: {reply}")
        print(f"✅ Extra: {extra}")
        return reply, extra
    except Exception as e:
        print(f"❌ Error in handle_tool: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    print("🚀 Starting chat tools debug...")
    
    # Test 1: get_by_code
    product = test_get_by_code()
    
    # Test 2: to_product_out
    if product:
        po = test_to_product_out()
    
    # Test 3: handle_tool
    reply, extra = test_handle_tool_search()
    
    print("✅ Debug complete!") 