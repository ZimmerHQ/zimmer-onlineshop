#!/usr/bin/env python3
"""
Test script for the new API functionality.

This script tests:
1. Category creation and listing
2. Product creation with auto-generated codes
3. Product search functionality
4. Import preview and commit
"""

import requests
import json
import csv
import io
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000/api"


def test_health():
    """Test the health endpoint."""
    print("🏥 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_categories():
    """Test category creation and listing."""
    print("📂 Testing categories...")
    
    # Create categories
    categories_data = [
        {"name": "Jeans"},
        {"name": "Shirts"},
        {"name": "Shoes"}
    ]
    
    created_categories = []
    for cat_data in categories_data:
        response = requests.post(f"{BASE_URL}/categories/", json=cat_data)
        print(f"Create category '{cat_data['name']}': {response.status_code}")
        if response.status_code == 201:
            created_categories.append(response.json())
            print(f"  -> Prefix: {response.json()['prefix']}")
    
    # List categories
    response = requests.get(f"{BASE_URL}/categories/")
    print(f"List categories: {response.status_code}")
    if response.status_code == 200:
        categories = response.json()
        print(f"  -> Found {len(categories)} categories")
        for cat in categories:
            print(f"    {cat['prefix']}: {cat['name']}")
    
    print()
    return created_categories


def test_products(categories):
    """Test product creation and search."""
    print("📦 Testing products...")
    
    if not categories:
        print("❌ No categories available for testing")
        return
    
    # Create products
    products_data = [
        {
            "name": "شلوار جین آبی",
            "description": "کلاسیک روزمره",
            "price": 450000.0,
            "stock": 10,
            "category_id": categories[0]["id"],  # Jeans
            "image_url": "https://example.com/jeans1.jpg",
            "tags": "jeans,blue,classic",
            "is_active": True
        },
        {
            "name": "پیراهن سفید",
            "description": "پیراهن رسمی",
            "price": 350000.0,
            "stock": 15,
            "category_id": categories[1]["id"],  # Shirts
            "image_url": "https://example.com/shirt1.jpg",
            "tags": "shirt,white,formal",
            "is_active": True
        }
    ]
    
    created_products = []
    for prod_data in products_data:
        response = requests.post(f"{BASE_URL}/products/", json=prod_data)
        print(f"Create product '{prod_data['name']}': {response.status_code}")
        if response.status_code == 201:
            created_products.append(response.json())
            print(f"  -> Code: {response.json()['code']}")
            print(f"  -> Category: {response.json()['category_name']}")
    
    # Test search
    print("\n🔍 Testing search...")
    
    # Search by name
    response = requests.get(f"{BASE_URL}/products/?q=جین")
    print(f"Search 'جین': {response.status_code}")
    if response.status_code == 200:
        results = response.json()
        print(f"  -> Found {len(results)} products")
    
    # Search by category
    response = requests.get(f"{BASE_URL}/products/?q=Jeans")
    print(f"Search 'Jeans': {response.status_code}")
    if response.status_code == 200:
        results = response.json()
        print(f"  -> Found {len(results)} products")
    
    # Filter by category
    response = requests.get(f"{BASE_URL}/products/?category_id={categories[0]['id']}")
    print(f"Filter by category {categories[0]['id']}: {response.status_code}")
    if response.status_code == 200:
        results = response.json()
        print(f"  -> Found {len(results)} products")
    
    print()
    return created_products


def test_import():
    """Test import functionality."""
    print("📥 Testing import functionality...")
    
    # Create CSV data
    csv_data = [
        ["name", "price", "stock", "category_name", "description", "image_url", "tags", "is_active"],
        ["کفش ورزشی", "250000", "8", "Shoes", "کفش ورزشی راحت", "https://example.com/shoes1.jpg", "sports,comfortable", "true"],
        ["شلوار جین مشکی", "380000", "12", "Jeans", "شلوار جین مشکی", "https://example.com/jeans2.jpg", "jeans,black", "true"],
        ["پیراهن آبی", "280000", "6", "Shirts", "پیراهن آبی رسمی", "https://example.com/shirt2.jpg", "shirt,blue,formal", "true"]
    ]
    
    # Create CSV file
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerows(csv_data)
    csv_content = csv_buffer.getvalue()
    
    # Test preview
    print("📋 Testing import preview...")
    files = {"file": ("products.csv", csv_content, "text/csv")}
    response = requests.post(f"{BASE_URL}/imports/products/preview", files=files)
    print(f"Preview: {response.status_code}")
    if response.status_code == 200:
        preview = response.json()
        print(f"  -> Total rows: {preview['total_rows']}")
        print(f"  -> Valid rows: {preview['valid_rows']}")
        print(f"  -> Invalid rows: {preview['invalid_rows']}")
    
    # Test commit
    print("\n💾 Testing import commit...")
    files = {"file": ("products.csv", csv_content, "text/csv")}
    response = requests.post(f"{BASE_URL}/imports/products/commit", files=files)
    print(f"Commit: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"  -> Inserted: {result['inserted']}")
        print(f"  -> Skipped: {result['skipped']}")
        print(f"  -> Errors: {len(result['errors'])}")
    
    # Test template download
    print("\n📄 Testing template download...")
    response = requests.get(f"{BASE_URL}/imports/products/template.csv")
    print(f"Template: {response.status_code}")
    if response.status_code == 200:
        print(f"  -> Template size: {len(response.content)} bytes")
    
    print()


def main():
    """Run all tests."""
    print("🧪 Starting API tests...")
    print("=" * 60)
    
    try:
        # Test health
        test_health()
        
        # Test categories
        categories = test_categories()
        
        # Test products
        products = test_products(categories)
        
        # Test import
        test_import()
        
        print("=" * 60)
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    main() 