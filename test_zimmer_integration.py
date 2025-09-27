#!/usr/bin/env python3
"""
Zimmer Integration Test Script
Tests all Zimmer endpoints to ensure they work correctly
"""

import requests
import os
import time
import json

# Configuration
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
ZIMMER_SERVICE_TOKEN = os.getenv("ZIMMER_SERVICE_TOKEN", "test-token-123")

def test_health_endpoint():
    """Test the public health endpoint."""
    print("🔍 Testing Health Endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["status", "version", "uptime"]
            
            if all(field in data for field in required_fields):
                print("✅ Health endpoint: PASS")
                print(f"   Status: {data['status']}")
                print(f"   Version: {data['version']}")
                print(f"   Uptime: {data['uptime']}")
                return True
            else:
                print("❌ Health endpoint: FAIL - Missing required fields")
                return False
        else:
            print(f"❌ Health endpoint: FAIL - Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health endpoint: FAIL - {str(e)}")
        return False

def test_provision_endpoint():
    """Test the provision endpoint."""
    print("\n🔍 Testing Provision Endpoint...")
    
    headers = {
        "Content-Type": "application/json",
        "X-Zimmer-Service-Token": ZIMMER_SERVICE_TOKEN
    }
    
    payload = {
        "user_automation_id": 123,
        "user_id": 456,
        "demo_tokens": 1000,
        "service_url": "https://example.com"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/zimmer/provision",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["success", "message", "provisioned_at", "integration_status"]
            
            if all(field in data for field in required_fields) and data["success"]:
                print("✅ Provision endpoint: PASS")
                print(f"   Status: {data['integration_status']}")
                print(f"   Message: {data['message']}")
                return True
            else:
                print("❌ Provision endpoint: FAIL - Invalid response structure")
                return False
        else:
            print(f"❌ Provision endpoint: FAIL - Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Provision endpoint: FAIL - {str(e)}")
        return False

def test_usage_consume_endpoint():
    """Test the usage consume endpoint."""
    print("\n🔍 Testing Usage Consume Endpoint...")
    
    headers = {
        "Content-Type": "application/json",
        "X-Zimmer-Service-Token": ZIMMER_SERVICE_TOKEN
    }
    
    payload = {
        "user_automation_id": 123,
        "units": 10,
        "usage_type": "chat",
        "meta": {"conversation_id": "test123"}
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/zimmer/usage/consume",
            headers=headers,
            json=payload,
            timeout=3
        )
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["accepted", "remaining_demo_tokens", "remaining_paid_tokens", "message"]
            
            if all(field in data for field in required_fields):
                print("✅ Usage consume endpoint: PASS")
                print(f"   Accepted: {data['accepted']}")
                print(f"   Remaining demo tokens: {data['remaining_demo_tokens']}")
                print(f"   Remaining paid tokens: {data['remaining_paid_tokens']}")
                return True
            else:
                print("❌ Usage consume endpoint: FAIL - Invalid response structure")
                return False
        else:
            print(f"❌ Usage consume endpoint: FAIL - Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Usage consume endpoint: FAIL - {str(e)}")
        return False

def test_kb_status_endpoint():
    """Test the KB status endpoint."""
    print("\n🔍 Testing KB Status Endpoint...")
    
    headers = {
        "X-Zimmer-Service-Token": ZIMMER_SERVICE_TOKEN
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/zimmer/kb/status?user_automation_id=123",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["status", "total_documents", "healthy"]
            
            if all(field in data for field in required_fields):
                print("✅ KB status endpoint: PASS")
                print(f"   Status: {data['status']}")
                print(f"   Total documents: {data['total_documents']}")
                print(f"   Healthy: {data['healthy']}")
                return True
            else:
                print("❌ KB status endpoint: FAIL - Invalid response structure")
                return False
        else:
            print(f"❌ KB status endpoint: FAIL - Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ KB status endpoint: FAIL - {str(e)}")
        return False

def test_kb_reset_endpoint():
    """Test the KB reset endpoint."""
    print("\n🔍 Testing KB Reset Endpoint...")
    
    headers = {
        "X-Zimmer-Service-Token": ZIMMER_SERVICE_TOKEN
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/zimmer/kb/reset?user_automation_id=123",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["success", "message", "reset_at"]
            
            if all(field in data for field in required_fields) and data["success"]:
                print("✅ KB reset endpoint: PASS")
                print(f"   Success: {data['success']}")
                print(f"   Message: {data['message']}")
                return True
            else:
                print("❌ KB reset endpoint: FAIL - Invalid response structure")
                return False
        else:
            print(f"❌ KB reset endpoint: FAIL - Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ KB reset endpoint: FAIL - {str(e)}")
        return False

def test_authentication():
    """Test authentication with missing and wrong tokens."""
    print("\n🔍 Testing Authentication...")
    
    # Test missing token
    try:
        response = requests.get(f"{BASE_URL}/api/zimmer/kb/status?user_automation_id=123")
        if response.status_code == 401:
            print("✅ Missing token: PASS (401)")
        else:
            print(f"❌ Missing token: FAIL - Expected 401, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Missing token: FAIL - {str(e)}")
        return False
    
    # Test wrong token
    try:
        headers = {"X-Zimmer-Service-Token": "wrong-token"}
        response = requests.get(
            f"{BASE_URL}/api/zimmer/kb/status?user_automation_id=123",
            headers=headers
        )
        if response.status_code == 401:
            print("✅ Wrong token: PASS (401)")
        else:
            print(f"❌ Wrong token: FAIL - Expected 401, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Wrong token: FAIL - {str(e)}")
        return False
    
    return True

def test_chat_timeout():
    """Test chat API timeout."""
    print("\n🔍 Testing Chat API Timeout...")
    
    payload = {
        "conversation_id": "test123",
        "message": "سلام"
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            timeout=10
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200 and elapsed < 9:
            data = response.json()
            if "reply" in data:
                print("✅ Chat API timeout: PASS")
                print(f"   Response time: {elapsed:.2f}s")
                print(f"   Reply: {data['reply'][:50]}...")
                return True
            else:
                print("❌ Chat API timeout: FAIL - Invalid response structure")
                return False
        else:
            print(f"❌ Chat API timeout: FAIL - Status {response.status_code} or timeout {elapsed:.2f}s")
            return False
            
    except Exception as e:
        print(f"❌ Chat API timeout: FAIL - {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🚀 Zimmer Integration Test Suite")
    print("=" * 50)
    print(f"Base URL: {BASE_URL}")
    print(f"Service Token: {ZIMMER_SERVICE_TOKEN[:10]}...")
    print("=" * 50)
    
    tests = [
        test_health_endpoint,
        test_provision_endpoint,
        test_usage_consume_endpoint,
        test_kb_status_endpoint,
        test_kb_reset_endpoint,
        test_authentication,
        test_chat_timeout
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Zimmer integration is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
