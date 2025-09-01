#!/usr/bin/env python3
"""
Test script to verify the fixed chat order creation flow
"""

import requests
import json

def test_chat_flow():
    base_url = "http://localhost:8000"
    conv_id = "test-fix"
    
    print("🧪 Testing fixed chat order creation flow...")
    
    # Step 1: Search for products
    print("\n1️⃣ Searching for products...")
    response = requests.post(
        f"{base_url}/api/chat",
        json={
            "conversation_id": conv_id,
            "message": "شلوار دارین"
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Search failed: {response.status_code}")
        return
    
    data = response.json()
    print(f"✅ Search response: {data.get('reply', 'No reply')[:100]}...")
    print(f"Debug: {data.get('debug', {})}")
    
    # Step 2: Select a product by code
    print("\n2️⃣ Selecting product A0001...")
    response = requests.post(
        f"{base_url}/api/chat",
        json={
            "conversation_id": conv_id,
            "message": "A0001"
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Product selection failed: {response.status_code}")
        return
    
    data = response.json()
    print(f"✅ Product selection: {data.get('reply', 'No reply')[:100]}...")
    print(f"Debug: {data.get('debug', {})}")
    
    # Step 3: Create order
    print("\n3️⃣ Creating order...")
    response = requests.post(
        f"{base_url}/api/chat",
        json={
            "conversation_id": conv_id,
            "message": "همینو میخوام"
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Order creation failed: {response.status_code}")
        return
    
    data = response.json()
    print(f"✅ Order creation: {data.get('reply', 'No reply')[:100]}...")
    print(f"Debug: {data.get('debug', {})}")
    
    # Step 4: Confirm order
    print("\n4️⃣ Confirming order...")
    response = requests.post(
        f"{base_url}/api/chat",
        json={
            "conversation_id": conv_id,
            "message": "تایید"
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Order confirmation failed: {response.status_code}")
        return
    
    data = response.json()
    print(f"✅ Order confirmation: {data.get('reply', 'No reply')[:100]}...")
    print(f"Debug: {data.get('debug', {})}")
    
    if data.get('order_id'):
        print(f"🎉 SUCCESS! Order created with ID: {data['order_id']}")
        print(f"Status: {data.get('status', 'Unknown')}")
    else:
        print("⚠️ Order ID not returned in response")

if __name__ == "__main__":
    test_chat_flow() 