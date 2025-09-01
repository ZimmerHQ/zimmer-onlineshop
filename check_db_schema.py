#!/usr/bin/env python3
"""
Check the actual database schema.
"""
import sqlite3

def check_db_schema():
    """Check the actual database schema."""
    db_path = "app.db"
    
    print(f"🔍 Checking database schema: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check products table schema
        cursor.execute("PRAGMA table_info(products)")
        columns = cursor.fetchall()
        print(f"📋 Products table columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - nullable: {col[3]}, default: {col[4]}")
        
        # Check categories table schema
        cursor.execute("PRAGMA table_info(categories)")
        cat_columns = cursor.fetchall()
        print(f"\n📋 Categories table columns:")
        for col in cat_columns:
            print(f"  {col[1]} ({col[2]}) - nullable: {col[3]}, default: {col[4]}")
        
        # Check if there are any products
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        print(f"\n📦 Products count: {product_count}")
        
        if product_count > 0:
            cursor.execute("SELECT * FROM products LIMIT 1")
            sample = cursor.fetchone()
            print(f"🔍 Sample product: {sample}")
        
        # Check if there are any categories
        cursor.execute("SELECT COUNT(*) FROM categories")
        cat_count = cursor.fetchone()[0]
        print(f"\n📦 Categories count: {cat_count}")
        
        if cat_count > 0:
            cursor.execute("SELECT * FROM categories LIMIT 1")
            sample = cursor.fetchone()
            print(f"🔍 Sample category: {sample}")
        
    except Exception as e:
        print(f"❌ Error checking schema: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    check_db_schema() 