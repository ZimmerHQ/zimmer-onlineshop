#!/usr/bin/env python3
"""
Test script to check if product lookup is working
"""

import requests
import json

def test_product_lookup():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing product lookup...")
    
    # Test 1: Check if product A0001 exists
    print("\n1️⃣ Looking up product A0001...")
    response = requests.get(f"{base_url}/api/products/code/A0001")
    
    if response.status_code == 200:
        product = response.json()
        print(f"✅ Product found: {product.get('name', 'Unknown')} (ID: {product.get('id', 'Unknown')})")
    else:
        print(f"❌ Product not found: {response.status_code}")
        print(f"Response: {response.text}")
    
    # Test 2: Check if product search works
    print("\n2️⃣ Searching for products with 'شلوار'...")
    response = requests.get(f"{base_url}/api/products/search?q=شلوار")
    
    if response.status_code == 200:
        products = response.json()
        print(f"✅ Found {len(products)} products:")
        for p in products[:3]:  # Show first 3
            print(f"  - {p.get('name', 'Unknown')} (کد: {p.get('code', 'Unknown')})")
    else:
        print(f"❌ Search failed: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_product_lookup() 