#!/usr/bin/env python3
"""
Seed script to populate the products table with test data
"""

import sys
import os
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Product, Base

# Test products data
TEST_PRODUCTS = [
    {
        "name": "Black Cotton T‑Shirt",
        "description": "Super soft, 100% cotton tag‑free tee",
        "price": 12.0,
        "sizes": ["S", "M", "L", "XL"],
        "stock": 50
    },
    {
        "name": "\"Think Big\" Logo T‑Shirt",
        "description": "Crew‑neck tee with BigCommerce logo",
        "price": 15.0,
        "sizes": ["M", "L", "XL"],
        "stock": 30
    },
    {
        "name": "BigCommerce Logo Hoodie",
        "description": "Heavyweight fleece, ribbed cuffs",
        "price": 25.0,
        "sizes": ["M", "L"],
        "stock": 20
    },
    {
        "name": "Women's Performance Girlfriend Jeans",
        "description": "Stretch denim & antimicrobial treatment, mid‑rise fit",
        "price": 78.0,
        "sizes": ["25", "27", "29"],
        "stock": 40
    },
    {
        "name": "Classic Skinny Blue Jeans",
        "description": "Curvy fit, stretchy denim",
        "price": 78.0,
        "sizes": ["5", "7", "9", "11", "13", "15"],
        "stock": 35
    },
    {
        "name": "Cropped Flare Medium Blue Jeans",
        "description": "Stretch denim, floral embroidered hem",
        "price": 86.8,
        "sizes": ["26", "28", "30"],
        "stock": 25
    }
]

def create_tables():
    """Create all tables if they don't exist"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified successfully")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)

def seed_products():
    """Seed the products table with test data"""
    db = SessionLocal()
    
    try:
        # Check if products already exist
        existing_count = db.query(Product).count()
        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing products in database")
            response = input("Do you want to add more products? (y/N): ").strip().lower()
            if response != 'y':
                print("❌ Seeding cancelled")
                return
        
        # Prepare products for insertion
        products_to_add = []
        for product_data in TEST_PRODUCTS:
            # Convert sizes list to comma-separated string
            sizes_str = ",".join(product_data["sizes"])
            
            # Create Product object
            product = Product(
                name=product_data["name"],
                description=product_data["description"],
                price=product_data["price"],
                sizes=sizes_str,
                stock=product_data["stock"],
                image_url=None  # No image URL for test products
            )
            products_to_add.append(product)
        
        # Add all products to database
        db.add_all(products_to_add)
        db.commit()
        
        print(f"✅ Successfully added {len(products_to_add)} products to database")
        
        # Display added products
        print("\n📦 Added Products:")
        print("=" * 60)
        for i, product in enumerate(products_to_add, 1):
            sizes_list = product.sizes.split(",") if product.sizes else []
            print(f"{i}. {product.name}")
            print(f"   Price: ${product.price:.2f}")
            print(f"   Sizes: {', '.join(sizes_list)}")
            print(f"   Stock: {product.stock}")
            print(f"   Description: {product.description[:50]}...")
            print()
        
    except Exception as e:
        print(f"❌ Error seeding products: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

def verify_seeding():
    """Verify that products were added correctly"""
    db = SessionLocal()
    
    try:
        total_products = db.query(Product).count()
        print(f"\n🔍 Verification: {total_products} total products in database")
        
        if total_products > 0:
            print("\n📋 Sample products in database:")
            print("-" * 40)
            sample_products = db.query(Product).limit(3).all()
            
            for product in sample_products:
                sizes_list = product.sizes.split(",") if product.sizes else []
                print(f"• {product.name}")
                print(f"  Price: ${product.price:.2f}")
                print(f"  Sizes: {', '.join(sizes_list)}")
                print(f"  Stock: {product.stock}")
                print()
        
    except Exception as e:
        print(f"❌ Error verifying products: {e}")
    finally:
        db.close()

def main():
    """Main function to run the seeding process"""
    print("🌱 Product Database Seeding Script")
    print("=" * 50)
    
    # Create tables if they don't exist
    print("\n1️⃣ Creating database tables...")
    create_tables()
    
    # Seed products
    print("\n2️⃣ Seeding products...")
    seed_products()
    
    # Verify seeding
    print("\n3️⃣ Verifying seeding...")
    verify_seeding()
    
    print("\n✅ Product seeding completed successfully!")
    print("\nYou can now test the product search functionality with:")
    print("python test_product_search.py")

if __name__ == "__main__":
    main() 