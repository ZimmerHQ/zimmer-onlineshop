#!/usr/bin/env python3
"""
Debug script to isolate the ProductOut error
"""

import requests
import json

def test_debug():
    print("🔍 Testing debug endpoint...")
    
    # Test the CONFIRM_ORDER action directly
    payload = {
        "conversation_id": "test_debug",
        "message": "تایید میکنم"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Debug info: {data.get('debug', {})}")
            
            if 'error' in data.get('debug', {}):
                print(f"❌ Error: {data['debug']['error']}")
            else:
                print("✅ No error in response")
                
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_debug() 