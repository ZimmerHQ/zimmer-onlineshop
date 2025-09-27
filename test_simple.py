import requests
import json

def test_simple():
    """Test simple chat without order creation"""
    
    # Test 1: Simple greeting
    print("=== Test 1: Simple greeting ===")
    body = {
        "conversation_id": "test_simple",
        "message": "سلام"
    }
    
    response = requests.post("http://localhost:8000/api/chat/", json=body)
    if response.status_code == 200:
        data = response.json()
        print("Response:", data.get("reply", "")[:200] + "...")
    else:
        print(f"Error: {response.status_code}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Product search
    print("=== Test 2: Product search ===")
    body = {
        "conversation_id": "test_simple",
        "message": "شلوار میخوام"
    }
    
    response = requests.post("http://localhost:8000/api/chat/", json=body)
    if response.status_code == 200:
        data = response.json()
        print("Response:", data.get("reply", "")[:200] + "...")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    test_simple()