#!/usr/bin/env python3
"""
Database initialization script
Creates all tables and adds some sample data
"""

import os
import sys
from pathlib import Path

# Set environment variables
os.environ.setdefault("ENV", "development")

print("🔧 Initializing database...")

try:
    # Import database components
    from database import engine, Base
    from models import *  # Import all models
    
    print("📋 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    
    # Test database connection
    from database import get_db
    db = next(get_db())
    
    # Check if tables exist
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"📊 Tables created: {', '.join(tables)}")
    
    # Add some sample data if tables are empty
    from models import Category, Product
    
    # Check if categories exist
    category_count = db.query(Category).count()
    if category_count == 0:
        print("🌱 Adding sample categories...")
        
        # Create sample categories
        categories = [
            Category(name="پوشاک مردانه", prefix="A"),
            Category(name="پوشاک زنانه", prefix="B"),
            Category(name="کفش", prefix="C"),
            Category(name="اکسسوری", prefix="D")
        ]
        
        for category in categories:
            db.add(category)
        
        db.commit()
        print(f"✅ Added {len(categories)} sample categories")
    else:
        print(f"📁 Found {category_count} existing categories")
    
    # Check if products exist
    product_count = db.query(Product).count()
    if product_count == 0:
        print("🛍️ Adding sample products...")
        
        # Get the first category
        first_category = db.query(Category).first()
        if first_category:
            # Create sample products
            products = [
                Product(
                    name="شلوار جین مردانه",
                    description="شلوار جین با کیفیت بالا",
                    price=150000.0,
                    stock=50,
                    category_id=first_category.id,
                    code="A0001",
                    is_active=True
                ),
                Product(
                    name="پیراهن رسمی مردانه",
                    description="پیراهن رسمی مناسب محل کار",
                    price=120000.0,
                    stock=30,
                    category_id=first_category.id,
                    code="A0002",
                    is_active=True
                )
            ]
            
            for product in products:
                db.add(product)
            
            db.commit()
            print(f"✅ Added {len(products)} sample products")
        else:
            print("⚠️ No categories found, skipping product creation")
    else:
        print(f"🛍️ Found {product_count} existing products")
    
    db.close()
    print("🎉 Database initialization completed successfully!")
    
except Exception as e:
    print(f"❌ Error initializing database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
