#!/usr/bin/env python3
"""
Production Smoke Test for Zimmer Integration
Tests all endpoints with environment placeholders
"""

import os
import requests
import time
import json
import sys

def get_env_or_exit(key, description):
    """Get environment variable or exit with helpful message."""
    value = os.getenv(key)
    if not value:
        print(f"❌ Missing required environment variable: {key}")
        print(f"   Description: {description}")
        print(f"   Example: export {key}=your-value-here")
        sys.exit(1)
    return value

def test_health(base_url):
    """Test health endpoint."""
    print("🔍 Testing Health Endpoint...")
    
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/health", timeout=5)
        latency = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["status", "version", "uptime"]
            
            if all(field in data for field in required_fields):
                print(f"✅ Health: PASS (latency: {latency:.1f}ms)")
                return True
            else:
                print(f"❌ Health: FAIL - Missing fields: {required_fields}")
                return False
        else:
            print(f"❌ Health: FAIL - Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health: FAIL - {str(e)}")
        return False

def test_provision(base_url, token):
    """Test provision endpoint."""
    print("🔍 Testing Provision Endpoint...")
    
    headers = {
        "Content-Type": "application/json",
        "X-Zimmer-Service-Token": token
    }
    
    payload = {
        "user_automation_id": 999,
        "user_id": 888,
        "demo_tokens": 1000,
        "service_url": "https://example.com"
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/zimmer/provision",
            headers=headers,
            json=payload,
            timeout=10
        )
        latency = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["success", "message", "provisioned_at", "integration_status"]
            
            if all(field in data for field in required_fields) and data["success"]:
                print(f"✅ Provision: PASS (latency: {latency:.1f}ms)")
                return True
            else:
                print(f"❌ Provision: FAIL - Invalid response structure")
                return False
        else:
            print(f"❌ Provision: FAIL - Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Provision: FAIL - {str(e)}")
        return False

def test_usage_consume(base_url, token):
    """Test usage consume endpoint."""
    print("🔍 Testing Usage Consume Endpoint...")
    
    headers = {
        "Content-Type": "application/json",
        "X-Zimmer-Service-Token": token
    }
    
    payload = {
        "user_automation_id": 999,
        "units": 10,
        "usage_type": "chat",
        "meta": {"conversation_id": "smoke_test"}
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/zimmer/usage/consume",
            headers=headers,
            json=payload,
            timeout=3
        )
        latency = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["accepted", "remaining_demo_tokens", "remaining_paid_tokens", "message"]
            
            if all(field in data for field in required_fields):
                print(f"✅ Usage Consume: PASS (latency: {latency:.1f}ms)")
                print(f"   Remaining demo tokens: {data['remaining_demo_tokens']}")
                return True
            else:
                print(f"❌ Usage Consume: FAIL - Invalid response structure")
                return False
        else:
            print(f"❌ Usage Consume: FAIL - Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Usage Consume: FAIL - {str(e)}")
        return False

def test_kb_status(base_url, token):
    """Test KB status endpoint."""
    print("🔍 Testing KB Status Endpoint...")
    
    headers = {
        "X-Zimmer-Service-Token": token
    }
    
    try:
        start_time = time.time()
        response = requests.get(
            f"{base_url}/api/zimmer/kb/status?user_automation_id=999",
            headers=headers,
            timeout=15
        )
        latency = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["status", "total_documents", "healthy"]
            
            if all(field in data for field in required_fields):
                print(f"✅ KB Status: PASS (latency: {latency:.1f}ms)")
                print(f"   Status: {data['status']}, Documents: {data['total_documents']}")
                return True
            else:
                print(f"❌ KB Status: FAIL - Invalid response structure")
                return False
        else:
            print(f"❌ KB Status: FAIL - Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ KB Status: FAIL - {str(e)}")
        return False

def test_kb_reset(base_url, token):
    """Test KB reset endpoint."""
    print("🔍 Testing KB Reset Endpoint...")
    
    headers = {
        "X-Zimmer-Service-Token": token
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/zimmer/kb/reset?user_automation_id=999",
            headers=headers,
            timeout=15
        )
        latency = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["success", "message", "reset_at"]
            
            if all(field in data for field in required_fields) and data["success"]:
                print(f"✅ KB Reset: PASS (latency: {latency:.1f}ms)")
                return True
            else:
                print(f"❌ KB Reset: FAIL - Invalid response structure")
                return False
        else:
            print(f"❌ KB Reset: FAIL - Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ KB Reset: FAIL - {str(e)}")
        return False

def test_chat_api(base_url):
    """Test chat API with timeout validation."""
    print("🔍 Testing Chat API (timeout validation)...")
    
    payload = {
        "conversation_id": "smoke_test",
        "message": "سلام"
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/chat",
            json=payload,
            timeout=10
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200 and elapsed < 9:
            data = response.json()
            if "reply" in data:
                print(f"✅ Chat API: PASS (latency: {elapsed:.2f}s)")
                print(f"   Reply: {data['reply'][:50]}...")
                return True
            else:
                print(f"❌ Chat API: FAIL - Invalid response structure")
                return False
        else:
            print(f"❌ Chat API: FAIL - Status {response.status_code} or timeout {elapsed:.2f}s")
            return False
            
    except Exception as e:
        print(f"❌ Chat API: FAIL - {str(e)}")
        return False

def test_authentication(base_url, token):
    """Test authentication with missing and wrong tokens."""
    print("🔍 Testing Authentication...")
    
    # Test missing token
    try:
        response = requests.get(f"{base_url}/api/zimmer/kb/status?user_automation_id=999")
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
            f"{base_url}/api/zimmer/kb/status?user_automation_id=999",
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

def main():
    """Run production smoke test."""
    print("🚀 Zimmer Integration Production Smoke Test")
    print("=" * 60)
    
    # Get environment variables
    base_url = get_env_or_exit("BASE_URL", "Base URL of the deployed service")
    token = get_env_or_exit("ZIMMER_SERVICE_TOKEN", "Zimmer service token for authentication")
    
    print(f"Base URL: {base_url}")
    print(f"Service Token: {token[:10]}...")
    print("=" * 60)
    
    # Run tests
    tests = [
        test_health,
        lambda: test_provision(base_url, token),
        lambda: test_usage_consume(base_url, token),
        lambda: test_kb_status(base_url, token),
        lambda: test_kb_reset(base_url, token),
        test_chat_api,
        lambda: test_authentication(base_url, token)
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print("=" * 60)
    print(f"📊 Smoke Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All smoke tests passed! Production deployment is healthy.")
        return True
    else:
        print("❌ Some smoke tests failed. Check the deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

