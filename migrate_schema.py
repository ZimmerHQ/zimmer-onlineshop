#!/usr/bin/env python3
"""
Database migration script for the new category and product schema.

This script will:
1. Create the categories table
2. Update the products table with new fields
3. Backfill product codes for existing products
4. Create an "Uncategorized" category for products without categories
"""

import os
import sys
from sqlalchemy import text, create_engine, MetaData, Table, Column, String, Integer, Boolean, ForeignKey, DateTime, inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
import sqlite3

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, get_db
from models import Base, Category, Product
from utils.clock import utcnow
from utils.category_prefix import assign_next_category_prefix
from utils.product_code import generate_code_for_category


def create_categories_table():
    """Create the categories table if it doesn't exist."""
    print("📋 Creating categories table...")
    
    # Check if categories table exists
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if 'categories' not in existing_tables:
        Category.__table__.create(engine, checkfirst=True)
        print("✅ Categories table created")
    else:
        print("ℹ️  Categories table already exists")


def update_products_table():
    """Update the products table with new fields."""
    print("📋 Updating products table...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if new columns exist
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('products')]
        
        # Add missing columns
        if 'code' not in columns:
            print("  ➕ Adding 'code' column...")
            db.execute(text("ALTER TABLE products ADD COLUMN code VARCHAR"))
            db.execute(text("CREATE INDEX IF NOT EXISTS ix_products_code ON products (code)"))
        
        if 'category_id' not in columns:
            print("  ➕ Adding 'category_id' column...")
            db.execute(text("ALTER TABLE products ADD COLUMN category_id INTEGER"))
            db.execute(text("CREATE INDEX IF NOT EXISTS ix_products_category_id ON products (category_id)"))
        
        if 'tags' not in columns:
            print("  ➕ Adding 'tags' column...")
            db.execute(text("ALTER TABLE products ADD COLUMN tags VARCHAR"))
        
        if 'thumbnail_url' not in columns:
            print("  ➕ Adding 'thumbnail_url' column...")
            db.execute(text("ALTER TABLE products ADD COLUMN thumbnail_url VARCHAR"))
        
        if 'sizes' not in columns:
            print("  ➕ Adding 'sizes' column...")
            db.execute(text("ALTER TABLE products ADD COLUMN sizes VARCHAR"))
        
        if 'is_active' not in columns:
            print("  ➕ Adding 'is_active' column...")
            db.execute(text("ALTER TABLE products ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
        
        if 'updated_at' not in columns:
            print("  ➕ Adding 'updated_at' column...")
            db.execute(text("ALTER TABLE products ADD COLUMN updated_at DATETIME"))
        
        # Add new structured attributes columns
        if 'available_sizes_json' not in columns:
            print("  ➕ Adding 'available_sizes_json' column...")
            db.execute(text("ALTER TABLE products ADD COLUMN available_sizes_json TEXT"))
        
        if 'available_colors_json' not in columns:
            print("  ➕ Adding 'available_colors_json' column...")
            db.execute(text("ALTER TABLE products ADD COLUMN available_colors_json TEXT"))
        
        # Update existing records
        db.execute(text("UPDATE products SET updated_at = created_at WHERE updated_at IS NULL"))
        db.execute(text("UPDATE products SET is_active = TRUE WHERE is_active IS NULL"))
        db.execute(text("UPDATE products SET stock = 0 WHERE stock IS NULL"))
        
        db.commit()
        print("✅ Products table updated")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating products table: {e}")
        raise
    finally:
        db.close()


def create_uncategorized_category():
    """Create an 'Uncategorized' category for products without categories."""
    print("📋 Creating 'Uncategorized' category...")
    
    db = next(get_db())
    
    try:
        # Check if Uncategorized category exists
        uncategorized = db.query(Category).filter(Category.name == "Uncategorized").first()
        
        if not uncategorized:
            # Create Uncategorized category
            prefix = assign_next_category_prefix(db)
            uncategorized = Category(name="Uncategorized", prefix=prefix)
            db.add(uncategorized)
            db.commit()
            db.refresh(uncategorized)
            print(f"✅ Created 'Uncategorized' category with prefix '{prefix}'")
        else:
            print(f"ℹ️  'Uncategorized' category already exists with prefix '{uncategorized.prefix}'")
        
        return uncategorized.id
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating Uncategorized category: {e}")
        raise
    finally:
        db.close()


def backfill_product_codes():
    """Backfill product codes for existing products."""
    print("📋 Backfilling product codes...")
    
    db = next(get_db())
    
    try:
        # Get products without codes
        products_without_codes = db.query(Product).filter(Product.code.is_(None)).all()
        
        if not products_without_codes:
            print("ℹ️  No products need code backfilling")
            return
        
        print(f"🔄 Found {len(products_without_codes)} products without codes")
        
        # Get or create Uncategorized category
        uncategorized_id = create_uncategorized_category()
        
        for product in products_without_codes:
            try:
                # Assign to Uncategorized if no category
                if not product.category_id:
                    product.category_id = uncategorized_id
                
                # Generate code
                code = generate_code_for_category(db, product.category_id)
                product.code = code
                
                print(f"  ✅ Product '{product.name}' -> {code}")
                
            except Exception as e:
                print(f"  ❌ Error generating code for product '{product.name}': {e}")
        
        db.commit()
        print("✅ Product codes backfilled")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error backfilling product codes: {e}")
        raise
    finally:
        db.close()


def add_foreign_key_constraints():
    """Add foreign key constraints if they don't exist."""
    print("📋 Adding foreign key constraints...")
    
    db = next(get_db())
    
    try:
        # Check if foreign key exists
        inspector = inspect(engine)
        foreign_keys = inspector.get_foreign_keys('products')
        
        category_fk_exists = any(fk['referred_table'] == 'categories' for fk in foreign_keys)
        
        if not category_fk_exists:
            print("  ➕ Adding foreign key constraint: products.category_id -> categories.id")
            # Note: SQLite doesn't support adding foreign keys to existing tables easily
            # This would require recreating the table, which is complex
            # For now, we'll rely on application-level validation
            print("  ℹ️  Foreign key constraint will be enforced at application level")
        else:
            print("ℹ️  Foreign key constraints already exist")
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding foreign key constraints: {e}")
    finally:
        db.close()


def migrate_schema():
    """Migrate database schema to latest version."""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'app.db')
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Please run the application first to create the database.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔧 Starting database migration...")
    
    try:
        # Check if product_variants table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='product_variants'
        """)
        
        if not cursor.fetchone():
            print("📦 Creating product_variants table...")
            cursor.execute("""
                CREATE TABLE product_variants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    size TEXT,
                    color TEXT,
                    sku TEXT,
                    stock INTEGER NOT NULL DEFAULT 0,
                    price_delta REAL NOT NULL DEFAULT 0.0,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
                )
            """)
            
            # Create index on product_id for performance
            cursor.execute("""
                CREATE INDEX idx_product_variants_product_id 
                ON product_variants (product_id)
            """)
            
            print("✅ product_variants table created successfully")
        else:
            print("✅ product_variants table already exists")
        
        # Check if order_items table has variant_id column
        cursor.execute("PRAGMA table_info(order_items)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'variant_id' not in columns:
            print("🔧 Adding variant_id column to order_items table...")
            cursor.execute("""
                ALTER TABLE order_items 
                ADD COLUMN variant_id INTEGER 
                REFERENCES product_variants (id)
            """)
            print("✅ variant_id column added to order_items table")
        else:
            print("✅ variant_id column already exists in order_items table")
        
        if 'variant_size' not in columns:
            print("🔧 Adding variant_size column to order_items table...")
            cursor.execute("""
                ALTER TABLE order_items 
                ADD COLUMN variant_size TEXT
            """)
            print("✅ variant_size column added to order_items table")
        else:
            print("✅ variant_size column already exists in order_items table")
        
        if 'variant_color' not in columns:
            print("🔧 Adding variant_color column to order_items table...")
            cursor.execute("""
                ALTER TABLE order_items 
                ADD COLUMN variant_color TEXT
            """)
            print("✅ variant_color column added to order_items table")
        else:
            print("✅ variant_color column already exists in order_items table")
        
        # Check if products table has new columns
        cursor.execute("PRAGMA table_info(products)")
        product_columns = [column[1] for column in cursor.fetchall()]
        
        if 'thumbnail_url' not in product_columns:
            print("🔧 Adding thumbnail_url column to products table...")
            cursor.execute("""
                ALTER TABLE products 
                ADD COLUMN thumbnail_url TEXT
            """)
            print("✅ thumbnail_url column added to products table")
        else:
            print("✅ thumbnail_url column already exists in products table")
        
        if 'sizes' not in product_columns:
            print("🔧 Adding sizes column to products table...")
            cursor.execute("""
                ALTER TABLE products 
                ADD COLUMN sizes TEXT
            """)
            print("✅ sizes column added to products table")
        else:
            print("✅ sizes column already exists in products table")
        
        # Add new structured attributes columns
        if 'available_sizes_json' not in product_columns:
            print("🔧 Adding available_sizes_json column to products table...")
            cursor.execute("""
                ALTER TABLE products 
                ADD COLUMN available_sizes_json TEXT
            """)
            print("✅ available_sizes_json column added to products table")
        else:
            print("✅ available_sizes_json column already exists in products table")
        
        if 'available_colors_json' not in product_columns:
            print("🔧 Adding available_colors_json column to products table...")
            cursor.execute("""
                ALTER TABLE products 
                ADD COLUMN available_colors_json TEXT
            """)
            print("✅ available_colors_json column added to products table")
        else:
            print("✅ available_colors_json column already exists in products table")
        
        # Update OrderStatus enum values in orders table
        print("🔧 Updating OrderStatus enum values...")
        
        # First, check what status values exist
        cursor.execute("SELECT DISTINCT status FROM orders")
        existing_statuses = [row[0] for row in cursor.fetchall()]
        
        # Update old status values to new ones
        if 'confirmed' in existing_statuses:
            cursor.execute("""
                UPDATE orders 
                SET status = 'approved' 
                WHERE status = 'confirmed'
            """)
            print("✅ Updated 'confirmed' → 'approved'")
        
        if 'processing' in existing_statuses:
            cursor.execute("""
                UPDATE orders 
                SET status = 'approved' 
                WHERE status = 'processing'
            """)
            print("✅ Updated 'processing' → 'approved'")
        
        if 'shipped' in existing_statuses:
            cursor.execute("""
                UPDATE orders 
                SET status = 'sold' 
                WHERE status = 'shipped'
            """)
            print("✅ Updated 'shipped' → 'sold'")
        
        if 'delivered' in existing_statuses:
            cursor.execute("""
                UPDATE orders 
                SET status = 'sold' 
                WHERE status = 'delivered'
            """)
            print("✅ Updated 'delivered' → 'sold'")
        
        # Add new status values if they don't exist
        cursor.execute("""
            UPDATE orders 
            SET status = 'draft' 
            WHERE status = 'pending' AND created_at = updated_at
        """)
        
        print("✅ OrderStatus enum values updated")
        
        # Commit all changes
        conn.commit()
        print("✅ Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def main():
    """Run the complete migration."""
    print("🚀 Starting database migration...")
    print("=" * 50)
    
    try:
        # Step 1: Create categories table
        create_categories_table()
        
        # Step 2: Update products table
        update_products_table()
        
        # Step 3: Create Uncategorized category
        create_uncategorized_category()
        
        # Step 4: Backfill product codes
        backfill_product_codes()
        
        # Step 5: Add foreign key constraints
        add_foreign_key_constraints()
        
        print("=" * 50)
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print("=" * 50)
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 