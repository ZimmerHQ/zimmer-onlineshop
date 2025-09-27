import requests
import json

def test_new_order_flow():
    """Test the new order flow with validation"""
    
    # Test 1: Order with missing customer fields
    print("=== Test 1: Order with missing customer fields ===")
    body = {
        "conversation_id": "test_missing_fields",
        "message": "کد A0001 رو میخوام سفارش بدم، 2 عدد"
    }
    
    response = requests.post("http://localhost:8000/api/chat/", json=body)
    if response.status_code == 200:
        data = response.json()
        print("Response:", data.get("reply", "")[:200] + "...")
    else:
        print(f"Error: {response.status_code}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Provide customer info
    print("=== Test 2: Provide customer info ===")
    body = {
        "conversation_id": "test_missing_fields",
        "message": "اسمم علی رضاییه، شماره 09123456789، آدرس تهران، کدپستی 1234567890"
    }
    
    response = requests.post("http://localhost:8000/api/chat/", json=body)
    if response.status_code == 200:
        data = response.json()
        print("Response:", data.get("reply", "")[:200] + "...")
    else:
        print(f"Error: {response.status_code}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Try to order again
    print("=== Test 3: Try to order again ===")
    body = {
        "conversation_id": "test_missing_fields",
        "message": "کد A0001 رو میخوام سفارش بدم، 2 عدد"
    }
    
    response = requests.post("http://localhost:8000/api/chat/", json=body)
    if response.status_code == 200:
        data = response.json()
        print("Response:", data.get("reply", "")[:300] + "...")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    test_new_order_flow()

