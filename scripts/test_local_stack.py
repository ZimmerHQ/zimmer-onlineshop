# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Local E2E Test Harness for Full Stack Testing
Tests: Health → Seed Data → Chat → Order → Approval → Stock Decrement → Analytics
"""

import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import time

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 10

class TestResult:
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.passed = False
        self.status_code = None
        self.response_text = ""
        self.error = None
    
    def success(self, status_code: int, response_text: str = ""):
        self.passed = True
        self.status_code = status_code
        self.response_text = response_text
    
    def failure(self, status_code: Optional[int], error: str, response_text: str = ""):
        self.passed = False
        self.status_code = status_code
        self.response_text = response_text
        self.error = error

def make_request(method: str, endpoint: str, data: Optional[Dict] = None, **kwargs) -> requests.Response:
    """Make HTTP request with error handling"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=TIMEOUT, **kwargs)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=TIMEOUT, **kwargs)
        elif method.upper() == "PATCH":
            response = requests.patch(url, json=data, timeout=TIMEOUT, **kwargs)
        else:
            raise ValueError(f"Unsupported method: {method}")
        return response
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {e}")

def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get nested dictionary value"""
    keys = key.split('.')
    current = data
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return default
    return current

def today_iso() -> str:
    """Get today's date in ISO format"""
    return datetime.now().strftime("%Y-%m-%d")

def print_result(result: TestResult):
    """Print test result in a formatted way"""
    if result.passed:
        print(f"[PASS] {result.test_name} {result.status_code}")
    else:
        print(f"[FAIL] {result.test_name} {result.status_code or 'ERROR'}")
        if result.error:
            print(f"       Error: {result.error}")
        if result.response_text:
            print(f"       Response: {result.response_text[:200]}...")

def test_health_checks() -> list[TestResult]:
    """Test health endpoints"""
    results = []
    
    # Test basic health
    result = TestResult("GET /api/health")
    try:
        response = make_request("GET", "/api/health")
        if response.status_code == 200:
            result.success(200, response.text)
        else:
            result.failure(response.status_code, f"Expected 200, got {response.status_code}", response.text)
    except Exception as e:
        result.failure(None, str(e))
    results.append(result)
    
    # Test detailed health
    result = TestResult("GET /api/health/details")
    try:
        response = make_request("GET", "/api/health/details")
        if response.status_code == 200:
            result.success(200, response.text)
        else:
            result.failure(response.status_code, f"Expected 200, got {response.status_code}", response.text)
    except Exception as e:
        result.failure(None, str(e))
    results.append(result)
    
    return results

def test_categories() -> list[TestResult]:
    """Test and ensure categories exist"""
    results = []
    
    # Check if categories exist
    result = TestResult("GET /api/categories/exists")
    try:
        response = make_request("GET", "/api/categories/exists")
        if response.status_code == 200:
            data = response.json()
            if data.get("exists", False):
                result.success(200, "Categories exist")
            else:
                # Create test category
                result = TestResult("POST /api/categories/ (create test category)")
                category_data = {
                    "name": "Test Category",
                    "description": "Test category for E2E testing"
                }
                response = make_request("POST", "/api/categories/", category_data)
                if response.status_code in [200, 201]:
                    result.success(response.status_code, "Test category created")
                else:
                    result.failure(response.status_code, "Failed to create test category", response.text)
        else:
            result.failure(response.status_code, f"Expected 200, got {response.status_code}", response.text)
    except Exception as e:
        result.failure(None, str(e))
    results.append(result)
    
    return results

def test_products() -> list[TestResult]:
    """Test and ensure test product exists"""
    results = []
    
    # Check if test product exists
    result = TestResult("GET /api/products/ (check test product)")
    try:
        response = make_request("GET", "/api/products/?page=1&page_size=100")
        if response.status_code == 200:
            data = response.json()
            # Products API returns list directly, not wrapped in object
            products = data if isinstance(data, list) else data.get("items", [])
            
            # Look for test product
            test_product = None
            for product in products:
                if product.get("name") == "شلوار نایک":
                    test_product = product
                    break
            
            if test_product:
                result.success(200, f"Test product found: {test_product.get('id')}")
            else:
                # Create test product
                result = TestResult("POST /api/products/ (create test product)")
                product_data = {
                    "name": "شلوار نایک",
                    "description": "مشکی",
                    "price": 123000,
                    "stock": 23,
                    "category_id": 1,  # Assuming first category
                    "sizes": ["S", "M", "L", "XL"],
                    "image_url": "",
                    "thumbnail_url": ""
                }
                response = make_request("POST", "/api/products/", product_data)
                if response.status_code in [200, 201]:
                    result.success(response.status_code, "Test product created")
                else:
                    result.failure(response.status_code, "Failed to create test product", response.text)
        else:
            result.failure(response.status_code, f"Expected 200, got {response.status_code}", response.text)
    except Exception as e:
        result.failure(None, str(e))
    results.append(result)
    
    return results

def test_chat_flow() -> list[TestResult]:
    """Test chat flow and order creation"""
    results = []
    
    # Test initial chat
    result = TestResult("POST /api/chat (initial question)")
    try:
        chat_data = {"conversation_id": "test-conv-001", "message": "شلوار داری؟"}
        response = make_request("POST", "/api/chat", chat_data)
        if response.status_code == 200:
            result.success(200, "Initial chat successful")
        else:
            result.failure(response.status_code, f"Expected 200, got {response.status_code}", response.text)
    except Exception as e:
        result.failure(None, str(e))
    results.append(result)
    
    # Test order request
    result = TestResult("POST /api/chat (order request)")
    try:
        chat_data = {"conversation_id": "test-conv-001", "message": "۱ عدد سایز M رنگ مشکی از شلوار نایک می‌خوام"}
        response = make_request("POST", "/api/chat", chat_data)
        if response.status_code == 200:
            result.success(200, "Order request successful")
        else:
            result.failure(response.status_code, f"Expected 200, got {response.status_code}", response.text)
    except Exception as e:
        result.failure(None, str(e))
    results.append(result)
    
    # Test order confirmation
    result = TestResult("POST /api/chat (order confirmation)")
    try:
        chat_data = {"conversation_id": "test-conv-001", "message": "تایید"}
        response = make_request("POST", "/api/chat", chat_data)
        if response.status_code == 200:
            result.success(200, "Order confirmation successful")
        else:
            result.failure(response.status_code, f"Expected 200, got {response.status_code}", response.text)
    except Exception as e:
        result.failure(None, str(e))
    results.append(result)
    
    return results

def get_latest_order() -> Optional[int]:
    """Get the latest order ID"""
    try:
        response = make_request("GET", "/api/orders/")
        if response.status_code == 200:
            data = response.json()
            orders = data.get("items", [])
            if orders:
                return orders[0].get("id")
    except Exception:
        pass
    return None

def test_order_approval(order_id: Optional[int]) -> list[TestResult]:
    """Test order approval and sale"""
    results = []
    
    if not order_id:
        result = TestResult("Order approval (no order found)")
        result.failure(None, "No order ID available for testing")
        results.append(result)
        return results
    
    # Test order approval
    result = TestResult(f"PATCH /api/orders/{order_id}/status (approve)")
    try:
        status_data = {"status": "approved"}
        response = make_request("PATCH", f"/api/orders/{order_id}/status", status_data)
        if response.status_code == 200:
            result.success(200, "Order approved")
        else:
            result.failure(response.status_code, f"Expected 200, got {response.status_code}", response.text)
    except Exception as e:
        result.failure(None, str(e))
    results.append(result)
    
    # Test marking as sold
    result = TestResult(f"PATCH /api/orders/{order_id}/status (sold)")
    try:
        status_data = {"status": "sold"}
        response = make_request("PATCH", f"/api/orders/{order_id}/status", status_data)
        if response.status_code == 200:
            result.success(200, "Order marked as sold")
        else:
            result.failure(response.status_code, f"Expected 200, got {response.status_code}", response.text)
    except Exception as e:
        result.failure(None, str(e))
    results.append(result)
    
    return results

def test_stock_decrement() -> list[TestResult]:
    """Test that product stock decreased after sale"""
    results = []
    
    result = TestResult("GET /api/products/ (verify stock decrement)")
    try:
        response = make_request("GET", "/api/products/?page=1&page_size=100")
        if response.status_code == 200:
            data = response.json()
            # Products API returns list directly, not wrapped in object
            products = data if isinstance(data, list) else data.get("items", [])
            
            # Find test product
            test_product = None
            for product in products:
                if product.get("name") == "شلوار نایک":
                    test_product = product
                    break
            
            if test_product:
                current_stock = test_product.get("stock", 0)
                if current_stock == 22:  # Should be 23 - 1
                    result.success(200, f"Stock correctly decremented to {current_stock}")
                else:
                    result.failure(200, f"Stock not decremented. Expected 22, got {current_stock}")
            else:
                result.failure(200, "Test product not found")
        else:
            result.failure(response.status_code, f"Expected 200, got {response.status_code}", response.text)
    except Exception as e:
        result.failure(None, str(e))
    results.append(result)
    
    return results

def test_analytics() -> list[TestResult]:
    """Test analytics with today's date range"""
    results = []
    
    today = today_iso()
    result = TestResult(f"GET /api/analytics/summary?start_date={today}&end_date={today}")
    try:
        response = make_request("GET", f"/api/analytics/summary?start_date={today}&end_date={today}")
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            required_fields = ["total_orders", "total_messages", "msg_order_ratio"]
            missing_fields = []
            
            for field in required_fields:
                if field not in data:
                    missing_fields.append(field)
            
            if missing_fields:
                result.failure(200, f"Missing required fields: {missing_fields}")
            else:
                result.success(200, f"Analytics data: orders={data.get('total_orders')}, messages={data.get('total_messages')}, ratio={data.get('msg_order_ratio')}")
        else:
            result.failure(response.status_code, f"Expected 200, got {response.status_code}", response.text)
    except Exception as e:
        result.failure(None, str(e))
    results.append(result)
    
    return results

def main():
    """Main test execution"""
    print("🧪 Starting Local E2E Test Harness")
    print("=" * 50)
    
    all_results = []
    
    # Test health checks
    print("\n1️⃣ Testing Health Endpoints...")
    all_results.extend(test_health_checks())
    
    # Test categories
    print("\n2️⃣ Testing Categories...")
    all_results.extend(test_categories())
    
    # Test products
    print("\n3️⃣ Testing Products...")
    all_results.extend(test_products())
    
    # Test chat flow
    print("\n4️⃣ Testing Chat Flow...")
    all_results.extend(test_chat_flow())
    
    # Get latest order
    print("\n5️⃣ Getting Latest Order...")
    order_id = get_latest_order()
    if order_id:
        print(f"   Found order ID: {order_id}")
    else:
        print("   No order found, will skip approval tests")
    
    # Test order approval
    print("\n6️⃣ Testing Order Approval...")
    all_results.extend(test_order_approval(order_id))
    
    # Test stock decrement
    print("\n7️⃣ Testing Stock Decrement...")
    all_results.extend(test_stock_decrement())
    
    # Test analytics
    print("\n8️⃣ Testing Analytics...")
    all_results.extend(test_analytics())
    
    # Print results summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for result in all_results:
        print_result(result)
        if result.passed:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"✅ PASSED: {passed}")
    print(f"❌ FAILED: {failed}")
    print(f"📈 SUCCESS RATE: {(passed / (passed + failed) * 100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Local stack is working correctly.")
        sys.exit(0)
    else:
        print(f"\n💥 {failed} test(s) failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 