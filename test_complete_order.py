import requests
import json

def test_complete_order():
    """Test complete order flow"""
    
    # Test 1: Order with customer info
    print("=== Test 1: Order with customer info ===")
    body = {
        "conversation_id": "test_complete",
        "message": "کد A0001 رو میخوام سفارش بدم، 2 عدد. اسمم علی رضاییه، شماره 09123456789، آدرس تهران، کدپستی 1234567890"
    }
    
    response = requests.post("http://localhost:8000/api/chat/", json=body)
    if response.status_code == 200:
        data = response.json()
        print("Response:", data.get("reply", "")[:300] + "...")
    else:
        print(f"Error: {response.status_code}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Confirm order
    print("=== Test 2: Confirm order ===")
    body = {
        "conversation_id": "test_complete",
        "message": "تایید"
    }
    
    response = requests.post("http://localhost:8000/api/chat/", json=body)
    if response.status_code == 200:
        data = response.json()
        print("Response:", data.get("reply", "")[:300] + "...")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    test_complete_order()

