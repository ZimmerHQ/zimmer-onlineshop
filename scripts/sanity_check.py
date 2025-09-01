# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Sanity check script for the FastAPI backend.
Tests full round-trip: Create Category → Create Product → Verify → Cleanup
"""

import os
import sys
import time
import requests
from typing import Dict, Any, Optional

# Add scripts directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))
from _cli_utils import (
    get_base_url, print_pass, print_fail, print_info, 
    print_header, print_summary, OK, FAIL
)


class SanityCheck:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.created_category: Optional[Dict[str, Any]] = None
        self.created_product: Optional[Dict[str, Any]] = None
        self.test_results: list = []
        
    def run_all_tests(self) -> None:
        """Run all sanity tests in sequence."""
        print_header("SANITY CHECK - FULL ROUND-TRIP TEST")
        
        try:
            # Test 1: Create category
            self.test_create_category()
            
            # Test 2: Create product
            self.test_create_product()
            
            # Test 3: Verify product via search
            self.test_product_search()
            
            # Test 4: Verify category summary
            self.test_category_summary()
            
            # Test 5: Cleanup
            self.test_cleanup()
            
        except Exception as e:
            print_fail("Unexpected error", str(e))
            self.test_results.append(False)
        finally:
            # Always try to cleanup
            self.ensure_cleanup()
    
    def test_create_category(self) -> None:
        """Test category creation."""
        try:
            timestamp = int(time.time())
            category_name = f"Sanity-{timestamp}"
            
            print_info("Creating category", category_name)
            
            response = requests.post(
                f"{self.base_url}/api/categories/",
                json={"name": category_name},
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                self.created_category = data
                print_pass("Creating category", f"id={data['id']}, prefix={data['prefix']}")
                self.test_results.append(True)
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print_fail("Creating category", error_msg)
                self.test_results.append(False)
                
        except requests.exceptions.RequestException as e:
            print_fail("Creating category", f"Request failed: {e}")
            self.test_results.append(False)
    
    def test_create_product(self) -> None:
        """Test product creation."""
        if not self.created_category:
            print_fail("Creating product", "No category available")
            self.test_results.append(False)
            return
            
        try:
            product_data = {
                "name": f"Sanity Product {int(time.time())}",
                "description": "Test product for sanity check",
                "price": 99.99,
                "stock": 10,
                "category_id": self.created_category["id"],
                "image_url": "https://example.com/test.jpg",
                "tags": "test,sanity,automation"
            }
            
            print_info("Creating product", product_data["name"])
            
            response = requests.post(
                f"{self.base_url}/api/products/",
                json=product_data,
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                self.created_product = data
                print_pass("Creating product", f"id={data['id']}, code={data['code']}")
                self.test_results.append(True)
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print_fail("Creating product", error_msg)
                self.test_results.append(False)
                
        except requests.exceptions.RequestException as e:
            print_fail("Creating product", f"Request failed: {e}")
            self.test_results.append(False)
    
    def test_product_search(self) -> None:
        """Test product search functionality."""
        if not self.created_product:
            print_fail("Searching product", "No product available")
            self.test_results.append(False)
        return
            
        try:
            search_query = self.created_product["name"].split()[0]  # First word of product name
            
            print_info("Searching product", f"query='{search_query}'")
            
            response = requests.get(
                f"{self.base_url}/api/products/",
                params={"q": search_query},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                found = any(p["id"] == self.created_product["id"] for p in data)
                
                if found:
                    print_pass("Searching product", f"Found product in {len(data)} results")
                    self.test_results.append(True)
                else:
                    print_fail("Searching product", "Product not found in search results")
                    self.test_results.append(False)
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print_fail("Searching product", error_msg)
                self.test_results.append(False)
                
        except requests.exceptions.RequestException as e:
            print_fail("Searching product", f"Request failed: {e}")
            self.test_results.append(False)
    
    def test_category_summary(self) -> None:
        """Test category summary with product count."""
        if not self.created_category:
            print_fail("Summary count", "No category available")
            self.test_results.append(False)
            return
            
        try:
            print_info("Summary count", "Checking category product count")
            
            response = requests.get(
                f"{self.base_url}/api/categories/summary",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                category_summary = next(
                    (cat for cat in data if cat["id"] == self.created_category["id"]), 
                    None
                )
                
                if category_summary and category_summary["product_count"] >= 1:
                    print_pass("Summary count", f"Category has {category_summary['product_count']} products")
                    self.test_results.append(True)
                else:
                    print_fail("Summary count", "Category product count not updated")
                    self.test_results.append(False)
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print_fail("Summary count", error_msg)
                self.test_results.append(False)
                
        except requests.exceptions.RequestException as e:
            print_fail("Summary count", f"Request failed: {e}")
            self.test_results.append(False)
    
    def test_cleanup(self) -> None:
        """Test cleanup functionality."""
        print_info("Cleanup", "Testing cleanup operations")
        
        cleanup_success = True
        
        # Try to delete product first
        if self.created_product:
            try:
                response = requests.delete(
                    f"{self.base_url}/api/products/{self.created_product['id']}",
                    timeout=10
                )
                
                if response.status_code in [200, 204]:
                    print_pass("Cleanup", "Product deleted successfully")
                else:
                    print_fail("Cleanup", f"Product deletion failed: HTTP {response.status_code}")
                    cleanup_success = False
                    
            except requests.exceptions.RequestException as e:
                print_fail("Cleanup", f"Product deletion request failed: {e}")
                cleanup_success = False
        
        # Try to delete category
        if self.created_category:
            try:
                response = requests.delete(
                    f"{self.base_url}/api/categories/{self.created_category['id']}",
                    timeout=10
                )
                
                if response.status_code in [200, 204]:
                    print_pass("Cleanup", "Category deleted successfully")
                else:
                    print_fail("Cleanup", f"Category deletion failed: HTTP {response.status_code}")
                    cleanup_success = False
                    
            except requests.exceptions.RequestException as e:
                print_fail("Cleanup", f"Category deletion request failed: {e}")
                cleanup_success = False
        
        if cleanup_success:
            self.test_results.append(True)
        else:
            self.test_results.append(False)
    
    def ensure_cleanup(self) -> None:
        """Ensure cleanup happens even if tests fail."""
        if not self.created_product and not self.created_category:
            return
            
        print_info("Cleanup", "Ensuring cleanup of test data...")
        
        # Force cleanup attempts
        if self.created_product:
            try:
                requests.delete(
                    f"{self.base_url}/api/products/{self.created_product['id']}",
                    timeout=5
                )
            except:
                pass  # Ignore cleanup errors
        
        if self.created_category:
            try:
                requests.delete(
                    f"{self.base_url}/api/categories/{self.created_category['id']}",
                    timeout=5
                )
            except:
                pass  # Ignore cleanup errors
    
    def get_results(self) -> tuple:
        """Get test results summary."""
        passed = sum(self.test_results)
        total = len(self.test_results)
        return passed, total


def main():
    """Main function to run sanity tests."""
    try:
        base_url = get_base_url()
        print(f"Testing backend at: {base_url}")
        
        sanity_check = SanityCheck(base_url)
        sanity_check.run_all_tests()
        
        passed, total = sanity_check.get_results()
        print_summary(passed, total)
        
        # Exit with appropriate code
        sys.exit(0 if passed == total else 1)
        
    except KeyboardInterrupt:
        print(f"\n{FAIL} Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n{FAIL} Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
