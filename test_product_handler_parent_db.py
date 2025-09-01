#!/usr/bin/env python3
"""
Test product handler with the updated database in the parent directory.
"""
import os
import sys

# Add the parent directory to the path so we can import the models
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_product_handler():
    """Test the product handler with the updated database."""
    try:
        print("🔍 Testing product handler with updated database...")
        
        # Test importing models
        from models import Product, Category
        print("✅ Models imported successfully")
        
        # Test importing database
        from database import get_db
        print("✅ Database imported successfully")
        
        # Test basic query
        db = next(get_db())
        print("📦 Testing basic product query...")
        
        try:
            products = db.query(Product).all()
            print(f"✅ Basic query successful: {len(products)} products")
            
            if products:
                for product in products:
                    print(f"  - {product.id}: {product.name} (Stock: {product.stock}, Low stock threshold: {getattr(product, 'low_stock_threshold', 'N/A')})")
        except Exception as e:
            print(f"❌ Basic query failed: {e}")
            return
        
        # Test with category join
        print("\n📦 Testing category join query...")
        try:
            from sqlalchemy.orm import joinedload
            join_query = db.query(Product).options(joinedload(Product.category)).all()
            print(f"✅ Join query successful: {len(join_query)} products")
        except Exception as e:
            print(f"❌ Join query failed: {e}")
            return
        
        db.close()
        print("🎉 All product queries successful!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_product_handler() 