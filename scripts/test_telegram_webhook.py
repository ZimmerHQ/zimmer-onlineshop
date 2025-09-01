# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Telegram Webhook Simulator for Local Testing
Posts fake Telegram updates to /api/telegram/webhook for testing
"""

import sys
import json
import requests
from datetime import datetime
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
WEBHOOK_ENDPOINT = "/api/telegram/webhook"
TIMEOUT = 10

def create_telegram_update(message_text: str, chat_id: int = 12345, user_id: int = 12345) -> Dict[str, Any]:
    """Create a fake Telegram update structure"""
    return {
        "update_id": int(datetime.now().timestamp()),
        "message": {
            "message_id": int(datetime.now().timestamp()),
            "from": {
                "id": user_id,
                "is_bot": False,
                "first_name": "Test",
                "last_name": "User",
                "username": "testuser",
                "language_code": "fa"
            },
            "chat": {
                "id": chat_id,
                "first_name": "Test",
                "last_name": "User",
                "username": "testuser",
                "type": "private"
            },
            "date": int(datetime.now().timestamp()),
            "text": message_text
        }
    }

def send_webhook_update(update_data: Dict[str, Any]) -> requests.Response:
    """Send webhook update to the local endpoint"""
    url = f"{BASE_URL}{WEBHOOK_ENDPOINT}?secret=test-secret"
    try:
        response = requests.post(
            url,
            json=update_data,
            timeout=TIMEOUT,
            headers={"Content-Type": "application/json"}
        )
        return response
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {e}")

def test_webhook_endpoint() -> bool:
    """Test if webhook endpoint is accessible"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=TIMEOUT)
        return response.status_code == 200
    except:
        return False

def main():
    """Main webhook simulation"""
    print("🤖 Telegram Webhook Simulator for Local Testing")
    print("=" * 60)
    
    # Check if backend is running
    if not test_webhook_endpoint():
        print("❌ Backend is not running or not accessible")
        print("   Please start the backend with: python main.py")
        sys.exit(1)
    
    print("✅ Backend is running and accessible")
    print(f"📡 Webhook endpoint: {BASE_URL}{WEBHOOK_ENDPOINT}")
    print("\n🚀 Starting webhook simulation...")
    
    # Test messages to send
    test_messages = [
        "/start",
        "قیمت شلوار نایک؟",
        "۱ عدد A0001 سایز M",
        "سلام، چطور می‌تونم کمکتون کنم؟",
        "/help"
    ]
    
    results = []
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}️⃣ Sending: {message}")
        
        # Create update data
        update_data = create_telegram_update(message)
        
        try:
            # Send webhook
            response = send_webhook_update(update_data)
            
            # Check response
            if response.status_code == 200:
                print(f"   ✅ Status: {response.status_code} OK")
                try:
                    response_data = response.json()
                    if response_data.get("status") == "ok":
                        print("   📨 Response: OK (webhook processed)")
                    else:
                        print(f"   ⚠️  Response: {response_data}")
                except:
                    print(f"   📨 Response: {response.text[:100]}...")
            else:
                print(f"   ❌ Status: {response.status_code}")
                print(f"   📨 Response: {response.text[:100]}...")
            
            results.append({
                "message": message,
                "status_code": response.status_code,
                "success": response.status_code == 200
            })
            
        except Exception as e:
            print(f"   💥 Error: {e}")
            results.append({
                "message": message,
                "status_code": None,
                "success": False,
                "error": str(e)
            })
        
        # Small delay between requests
        import time
        time.sleep(0.5)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 WEBHOOK SIMULATION SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['message']} -> {result['status_code'] or 'ERROR'}")
    
    print(f"\n📈 Success Rate: {successful}/{total} ({(successful/total*100):.1f}%)")
    
    if successful == total:
        print("\n🎉 All webhook updates sent successfully!")
        print("\n💡 Note: This is local testing only.")
        print("   For real Telegram bot functionality, you need:")
        print("   1. A public HTTPS webhook URL (ngrok, Render, etc.)")
        print("   2. A valid bot token configured in Settings → Integrations")
        print("   3. Webhook set via Telegram API")
        sys.exit(0)
    else:
        print(f"\n💥 {total - successful} webhook update(s) failed.")
        print("   Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 