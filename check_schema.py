#!/usr/bin/env python3
"""
Check database schema and add missing columns.
"""
import sqlite3
import os

def check_and_fix_schema():
    """Check database schema and add missing columns."""
    db_path = "app.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return
    
    print(f"🔍 Checking database schema: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check products table schema
        cursor.execute("PRAGMA table_info(products)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 Products table columns: {columns}")
        
        # Check if required columns exist
        required_columns = ['low_stock_threshold', 'thumbnail_url', 'sizes']
        missing_columns = []
        
        for col in required_columns:
            if col not in columns:
                missing_columns.append(col)
        
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            
            # Add missing columns
            for col in missing_columns:
                if col == 'low_stock_threshold':
                    print(f"➕ Adding {col} column...")
                    cursor.execute("ALTER TABLE products ADD COLUMN low_stock_threshold INTEGER NOT NULL DEFAULT 5")
                elif col == 'thumbnail_url':
                    print(f"➕ Adding {col} column...")
                    cursor.execute("ALTER TABLE products ADD COLUMN thumbnail_url TEXT")
                elif col == 'sizes':
                    print(f"➕ Adding {col} column...")
                    cursor.execute("ALTER TABLE products ADD COLUMN sizes TEXT")
            
            conn.commit()
            print("✅ Added missing columns")
            
            # Verify the changes
            cursor.execute("PRAGMA table_info(products)")
            new_columns = [col[1] for col in cursor.fetchall()]
            print(f"📋 Updated products table columns: {new_columns}")
        else:
            print("✅ All required columns exist")
        
        # Check if there are any products
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        print(f"📦 Found {product_count} products in database")
        
        if product_count > 0:
            # Check a sample product
            cursor.execute("SELECT * FROM products LIMIT 1")
            sample = cursor.fetchone()
            print(f"🔍 Sample product: {sample}")
        
    except Exception as e:
        print(f"❌ Error checking schema: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    check_and_fix_schema() 