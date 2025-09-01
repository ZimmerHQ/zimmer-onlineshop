#!/usr/bin/env python3
"""
Test database connection and check products.
"""
from database import get_db
from models.product import Product
from models.category import Category

def test_database():
    """Test database connection and check data."""
    try:
        # Get database session
        db = next(get_db())
        
        print("🔍 Testing database connection...")
        
        # Check categories
        categories = db.query(Category).all()
        print(f"✅ Found {len(categories)} categories:")
        for cat in categories:
            print(f"  - {cat.id}: {cat.name} ({cat.prefix})")
        
        # Check products
        products = db.query(Product).all()
        print(f"✅ Found {len(products)} products:")
        for prod in products:
            print(f"  - {prod.id}: {prod.name} (Category: {prod.category_id})")
        
        # Test a simple query
        print("\n🔍 Testing simple product query...")
        try:
            simple_query = db.query(Product).limit(5).all()
            print(f"✅ Simple query successful: {len(simple_query)} products")
        except Exception as e:
            print(f"❌ Simple query failed: {e}")
        
        # Test with category join
        print("\n🔍 Testing category join query...")
        try:
            from sqlalchemy.orm import joinedload
            join_query = db.query(Product).options(joinedload(Product.category)).limit(5).all()
            print(f"✅ Join query successful: {len(join_query)} products")
        except Exception as e:
            print(f"❌ Join query failed: {e}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database() 