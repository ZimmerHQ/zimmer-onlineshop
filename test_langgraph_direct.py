#!/usr/bin/env python3
"""
Direct test of LangGraph integration without server
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all imports work"""
    print("Testing imports...")
    
    try:
        from backend.ai.tools import tool_search_products, tool_get_product_by_code, tool_create_order
        print("✅ Tools imported successfully")
    except Exception as e:
        print(f"❌ Tools import failed: {e}")
        return False
    
    try:
        from backend.ai.graph import app as chat_graph
        print("✅ Graph imported successfully")
    except Exception as e:
        print(f"❌ Graph import failed: {e}")
        return False
    
    try:
        from routers.chat import router
        print("✅ Chat router imported successfully")
    except Exception as e:
        print(f"❌ Chat router import failed: {e}")
        return False
    
    return True

def test_graph_execution():
    """Test that the graph can be executed"""
    print("\nTesting graph execution...")
    
    try:
        from backend.ai.graph import app as chat_graph
        
        # Test state
        state = {
            "msg": "A0001",
            "reply": "",
            "stage": "idle",
            "product": None,
            "candidates": [],
            "qty": 1,
            "size": None,
            "color": None,
            "order": None
        }
        
        print("Invoking graph...")
        result = chat_graph.invoke(state)
        print(f"✅ Graph executed successfully")
        print(f"Result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Graph execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🧪 Testing LangGraph Integration Directly")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed")
        sys.exit(1)
    
    # Test graph execution
    if not test_graph_execution():
        print("\n❌ Graph execution tests failed")
        sys.exit(1)
    
    print("\n✅ All tests passed! LangGraph integration is working.")
    print("\nTo test with server:")
    print("1. Start server: python -m uvicorn main:app --host 127.0.0.1 --port 8000")
    print("2. Run smoke test: python backend/scripts/smoke_langgraph.py")

if __name__ == "__main__":
    main()
