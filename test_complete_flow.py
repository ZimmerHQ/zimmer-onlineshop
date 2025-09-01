#!/usr/bin/env python3
"""
Test the complete chat flow using Python requests
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_complete_order_flow():
    """Test the complete order creation flow"""
    conversation_id = "test-order-flow"
    
    print("🔄 Testing complete order creation flow...")
    
    # Test 1: Search for product
    print("\n🔍 Test 1: Searching for product A0001...")
    response1 = requests.post(f"{BASE_URL}/api/chat", json={
        "conversation_id": conversation_id,
        "message": "A0001"
    })
    
    if response1.status_code == 200:
        data1 = response1.json()
        print(f"✅ Search response: {data1['reply'][:100]}...")
        print(f"Debug: {data1.get('debug', {})}")
    else:
        print(f"❌ Search failed: {response1.status_code}")
        return
    
    # Test 2: Create order summary
    print("\n🛒 Test 2: Creating order summary...")
    response2 = requests.post(f"{BASE_URL}/api/chat", json={
        "conversation_id": conversation_id,
        "message": "همینو میخوام"
    })
    
    if response2.status_code == 200:
        data2 = response2.json()
        print(f"✅ Order creation response: {data2['reply'][:100]}...")
        print(f"Debug: {data2.get('debug', {})}")
    else:
        print(f"❌ Order creation failed: {response2.status_code}")
        return
    
    # Test 3: Confirm order
    print("\n✅ Test 3: Confirming order...")
    response3 = requests.post(f"{BASE_URL}/api/chat", json={
        "conversation_id": conversation_id,
        "message": "تایید میکنم"
    })
    
    if response3.status_code == 200:
        data3 = response3.json()
        print(f"✅ Order confirmation response: {data3['reply']}")
        print(f"Debug: {data3.get('debug', {})}")
        
        if data3.get('order_id'):
            print(f"🎉 SUCCESS! Order created with ID: {data3['order_id']}")
        else:
            print("⚠️ Order ID not returned in response")
    else:
        print(f"❌ Order confirmation failed: {response3.status_code}")
        return

if __name__ == "__main__":
    test_complete_order_flow() 