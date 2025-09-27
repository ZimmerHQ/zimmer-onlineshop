#!/usr/bin/env python3
"""
Comprehensive Smoke Test for Shop Automation System
Tests all major features and endpoints
"""

import requests
import json
import time
from datetime import datetime, timedelta
import sys

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "errors": []
}

def log_test(test_name, success, error_msg=None):
    """Log test results"""
    if success:
        print(f"✅ {test_name}")
        test_results["passed"] += 1
    else:
        print(f"❌ {test_name}: {error_msg}")
        test_results["failed"] += 1
        test_results["errors"].append(f"{test_name}: {error_msg}")

def make_request(method, url, **kwargs):
    """Make HTTP request with error handling"""
    try:
        # Set longer timeout for chat requests
        timeout = 30 if 'chat' in url else 10
        response = requests.request(method, url, timeout=timeout, **kwargs)
        return response, None
    except requests.exceptions.RequestException as e:
        return None, str(e)

def test_server_health():
    """Test if server is running"""
    print("\n🔍 Testing Server Health...")
    
    # Test docs endpoint instead of health
    response, error = make_request("GET", f"{BASE_URL}/docs")
    if error:
        log_test("Server Health Check", False, f"Server not responding: {error}")
        return False
    
    if response.status_code == 200:
        log_test("Server Health Check", True)
        return True
    else:
        log_test("Server Health Check", False, f"Status: {response.status_code}")
        return False

def test_analytics_summary():
    """Test analytics summary endpoint"""
    print("\n📊 Testing Analytics Summary...")
    
    # Test without date range
    response, error = make_request("GET", f"{API_BASE}/analytics/summary")
    if error:
        log_test("Analytics Summary (no dates)", False, error)
        return False
    
    if response.status_code == 200:
        data = response.json()
        required_fields = ["total_orders", "total_revenue", "total_customers", "total_messages"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            log_test("Analytics Summary (no dates)", False, f"Missing fields: {missing_fields}")
        else:
            log_test("Analytics Summary (no dates)", True)
            print(f"   📈 Total Orders: {data.get('total_orders', 0)}")
            print(f"   💰 Total Revenue: {data.get('total_revenue', 0)}")
            print(f"   👥 Total Customers: {data.get('total_customers', 0)}")
            print(f"   💬 Total Messages: {data.get('total_messages', 0)}")
    else:
        log_test("Analytics Summary (no dates)", False, f"Status: {response.status_code}")
        return False
    
    # Test with date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }
    
    response, error = make_request("GET", f"{API_BASE}/analytics/summary", params=params)
    if error:
        log_test("Analytics Summary (with dates)", False, error)
    else:
        if response.status_code == 200:
            log_test("Analytics Summary (with dates)", True)
        else:
            log_test("Analytics Summary (with dates)", False, f"Status: {response.status_code}")

def test_product_analytics_search():
    """Test product analytics search"""
    print("\n🔍 Testing Product Analytics Search...")
    
    # Test search with empty query (should return all products)
    response, error = make_request("GET", f"{API_BASE}/analytics/products/search", params={"q": ""})
    if error:
        log_test("Product Search (empty query)", False, error)
        return False
    
    if response.status_code == 200:
        data = response.json()
        if "products" in data and "total_found" in data:
            log_test("Product Search (empty query)", True)
            print(f"   📦 Found {data['total_found']} products")
            
            if data["products"]:
                product = data["products"][0]
                print(f"   🏷️  Sample Product: {product.get('name', 'N/A')}")
                print(f"   💰 Revenue: {product.get('total_revenue', 0)}")
                print(f"   📊 Sold: {product.get('total_sold', 0)}")
        else:
            log_test("Product Search (empty query)", False, "Invalid response format")
    else:
        log_test("Product Search (empty query)", False, f"Status: {response.status_code}")
        return False
    
    # Test search with specific query
    response, error = make_request("GET", f"{API_BASE}/analytics/products/search", params={"q": "شلوار"})
    if error:
        log_test("Product Search (specific query)", False, error)
    else:
        if response.status_code == 200:
            data = response.json()
            log_test("Product Search (specific query)", True)
            print(f"   🔍 Found {data.get('total_found', 0)} products matching 'شلوار'")
        else:
            log_test("Product Search (specific query)", False, f"Status: {response.status_code}")

def test_product_analytics_details():
    """Test product analytics details"""
    print("\n📋 Testing Product Analytics Details...")
    
    # First get a product ID from search
    response, error = make_request("GET", f"{API_BASE}/analytics/products/search", params={"q": ""})
    if error or response.status_code != 200:
        log_test("Product Details (get product ID)", False, "Could not get product list")
        return False
    
    data = response.json()
    if not data.get("products"):
        log_test("Product Details (no products)", False, "No products available for testing")
        return False
    
    product_id = data["products"][0]["id"]
    
    # Test product details
    response, error = make_request("GET", f"{API_BASE}/analytics/products/{product_id}/details")
    if error:
        log_test("Product Details", False, error)
        return False
    
    if response.status_code == 200:
        data = response.json()
        required_fields = ["product", "analytics", "daily_sales", "recent_orders"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            log_test("Product Details", False, f"Missing fields: {missing_fields}")
        else:
            log_test("Product Details", True)
            print(f"   📦 Product: {data['product']['name']}")
            print(f"   💰 Total Revenue: {data['analytics']['total_revenue']}")
            print(f"   📊 Total Sold: {data['analytics']['total_sold']}")
            print(f"   📅 Daily Sales Records: {len(data['daily_sales'])}")
            print(f"   🛒 Recent Orders: {len(data['recent_orders'])}")
    else:
        log_test("Product Details", False, f"Status: {response.status_code}")

def test_orders_api():
    """Test orders API"""
    print("\n🛒 Testing Orders API...")
    
    # Test get orders
    response, error = make_request("GET", f"{API_BASE}/orders/")
    if error:
        log_test("Get Orders", False, error)
        return False
    
    if response.status_code == 200:
        data = response.json()
        log_test("Get Orders", True)
        print(f"   📋 Found {len(data)} orders")
        
        if data:
            order = data[0]
            print(f"   🏷️  Sample Order: #{order.get('order_number', 'N/A')}")
            print(f"   👤 Customer: {order.get('customer_name', 'N/A')}")
            print(f"   💰 Amount: {order.get('final_amount', 0)}")
    else:
        log_test("Get Orders", False, f"Status: {response.status_code}")

def test_products_api():
    """Test products API"""
    print("\n📦 Testing Products API...")
    
    # Test get products
    response, error = make_request("GET", f"{API_BASE}/products/")
    if error:
        log_test("Get Products", False, error)
        return False
    
    if response.status_code == 200:
        data = response.json()
        log_test("Get Products", True)
        print(f"   📦 Found {len(data)} products")
        
        if data:
            product = data[0]
            print(f"   🏷️  Sample Product: {product.get('name', 'N/A')}")
            print(f"   💰 Price: {product.get('price', 0)}")
            print(f"   📊 Stock: {product.get('stock', 0)}")
    else:
        log_test("Get Products", False, f"Status: {response.status_code}")

def test_categories_api():
    """Test categories API"""
    print("\n🏷️  Testing Categories API...")
    
    # Test get categories
    response, error = make_request("GET", f"{API_BASE}/categories/")
    if error:
        log_test("Get Categories", False, error)
        return False
    
    if response.status_code == 200:
        data = response.json()
        log_test("Get Categories", True)
        print(f"   🏷️  Found {len(data)} categories")
        
        if data:
            category = data[0]
            print(f"   📂 Sample Category: {category.get('name', 'N/A')}")
    else:
        log_test("Get Categories", False, f"Status: {response.status_code}")

def test_conversations_api():
    """Test conversations API"""
    print("\n💬 Testing Conversations API...")
    
    # Test get conversations
    response, error = make_request("GET", f"{API_BASE}/conversations/")
    if error:
        log_test("Get Conversations", False, error)
        return False
    
    if response.status_code == 200:
        data = response.json()
        log_test("Get Conversations", True)
        print(f"   💬 Found {data.get('total', 0)} conversations")
    else:
        log_test("Get Conversations", False, f"Status: {response.status_code}")
    
    # Test get users
    response, error = make_request("GET", f"{API_BASE}/conversations/users")
    if error:
        log_test("Get Users", False, error)
    else:
        if response.status_code == 200:
            data = response.json()
            log_test("Get Users", True)
            print(f"   👥 Found {data.get('total', 0)} users")
        else:
            log_test("Get Users", False, f"Status: {response.status_code}")

def test_support_api():
    """Test support API"""
    print("\n🎧 Testing Support API...")
    
    # Test get support requests
    response, error = make_request("GET", f"{API_BASE}/support/requests")
    if error:
        log_test("Get Support Requests", False, error)
        return False
    
    if response.status_code == 200:
        data = response.json()
        log_test("Get Support Requests", True)
        print(f"   🎧 Found {len(data)} support requests")
    else:
        log_test("Get Support Requests", False, f"Status: {response.status_code}")

def test_crm_api():
    """Test CRM API"""
    print("\n👥 Testing CRM API...")
    
    # Test get customers
    response, error = make_request("GET", f"{API_BASE}/crm/customers")
    if error:
        log_test("Get CRM Customers", False, error)
        return False
    
    if response.status_code == 200:
        data = response.json()
        log_test("Get CRM Customers", True)
        print(f"   👥 Found {len(data)} CRM customers")
    else:
        log_test("Get CRM Customers", False, f"Status: {response.status_code}")

def test_chat_api():
    """Test chat API"""
    print("\n🤖 Testing Chat API...")
    
    # First test the ping endpoint
    response, error = make_request("GET", f"{API_BASE}/chat/ping")
    if error:
        log_test("Chat Ping", False, error)
    else:
        if response.status_code == 200:
            log_test("Chat Ping", True)
        else:
            log_test("Chat Ping", False, f"Status: {response.status_code}")
    
    # Test the test endpoint (no AI processing)
    chat_data = {
        "message": "test",
        "conversation_id": "test_conversation"
    }
    
    response, error = make_request("POST", f"{API_BASE}/chat/test", 
                                 json=chat_data, 
                                 headers={"Content-Type": "application/json"})
    if error:
        log_test("Chat Test Endpoint", False, error)
    else:
        if response.status_code == 200:
            log_test("Chat Test Endpoint", True)
        else:
            log_test("Chat Test Endpoint", False, f"Status: {response.status_code}")
    
    # Test main chat endpoint with a simple message
    chat_data = {
        "message": "سلام",
        "conversation_id": "test_conversation"
    }
    
    response, error = make_request("POST", f"{API_BASE}/chat", 
                                 json=chat_data, 
                                 headers={"Content-Type": "application/json"})
    if error:
        log_test("Chat Main Endpoint", False, error)
        return False
    
    if response.status_code == 200:
        data = response.json()
        log_test("Chat Main Endpoint", True)
        print(f"   🤖 Chat response received")
        if "reply" in data:
            print(f"   💬 Response: {data['reply'][:100]}...")
    else:
        log_test("Chat Main Endpoint", False, f"Status: {response.status_code}")

def test_frontend_endpoints():
    """Test frontend-specific endpoints"""
    print("\n🌐 Testing Frontend Endpoints...")
    
    # Test analytics summary for frontend
    response, error = make_request("GET", f"{API_BASE}/analytics/summary")
    if error:
        log_test("Frontend Analytics", False, error)
    else:
        if response.status_code == 200:
            log_test("Frontend Analytics", True)
        else:
            log_test("Frontend Analytics", False, f"Status: {response.status_code}")

def run_comprehensive_test():
    """Run all tests"""
    print("🚀 Starting Comprehensive Smoke Test for Shop Automation System")
    print("=" * 70)
    
    # Check if server is running first
    if not test_server_health():
        print("\n❌ Server is not running. Please start the server first.")
        return False
    
    # Run all test suites
    test_analytics_summary()
    test_product_analytics_search()
    test_product_analytics_details()
    test_orders_api()
    test_products_api()
    test_categories_api()
    test_conversations_api()
    test_support_api()
    test_crm_api()
    test_chat_api()
    test_frontend_endpoints()
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"📈 Success Rate: {(test_results['passed'] / (test_results['passed'] + test_results['failed']) * 100):.1f}%")
    
    if test_results['errors']:
        print("\n❌ ERRORS:")
        for error in test_results['errors']:
            print(f"   • {error}")
    
    print("\n🎯 Test completed!")
    return test_results['failed'] == 0

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
