#!/usr/bin/env python3
"""
Test product handler functions directly.
"""
from database import get_db
from models import Product, Category
from sqlalchemy.orm import joinedload

def test_product_query():
    """Test the product query logic directly."""
    try:
        print("🔍 Testing product query logic...")
        
        # Get database session
        db = next(get_db())
        
        # Test basic query
        print("📦 Testing basic product query...")
        try:
            basic_query = db.query(Product).all()
            print(f"✅ Basic query successful: {len(basic_query)} products")
        except Exception as e:
            print(f"❌ Basic query failed: {e}")
            return
        
        # Test with category join
        print("📦 Testing category join query...")
        try:
            join_query = db.query(Product).options(joinedload(Product.category)).all()
            print(f"✅ Join query successful: {len(join_query)} products")
        except Exception as e:
            print(f"❌ Join query failed: {e}")
            return
        
        # Test with search filter
        print("📦 Testing search filter query...")
        try:
            from sqlalchemy import or_
            search_query = db.query(Product).options(joinedload(Product.category))
            search_query = search_query.filter(
                or_(
                    Product.name.ilike("%test%"),
                    Product.code.ilike("%test%"),
                    Product.category.has(Category.name.ilike("%test%"))
                )
            )
            results = search_query.all()
            print(f"✅ Search query successful: {len(results)} products")
        except Exception as e:
            print(f"❌ Search query failed: {e}")
            return
        
        # Test pagination
        print("📦 Testing pagination query...")
        try:
            paginated_query = db.query(Product).options(joinedload(Product.category))
            paginated_query = paginated_query.order_by(Product.created_at.desc()).offset(0).limit(10)
            results = paginated_query.all()
            print(f"✅ Pagination query successful: {len(results)} products")
        except Exception as e:
            print(f"❌ Pagination query failed: {e}")
            return
        
        print("🎉 All product queries successful!")
        db.close()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_product_query() 