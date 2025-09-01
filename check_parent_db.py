#!/usr/bin/env python3
"""
Check the database in the parent directory.
"""
import sqlite3
import os

def check_parent_db():
    """Check the database in the parent directory."""
    db_path = "../app.db"
    
    print(f"🔍 Checking database: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if tables:
            print(f"📋 Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("❌ No tables found!")
        
        # Check products table schema
        if ('products',) in tables:
            cursor.execute("PRAGMA table_info(products)")
            columns = cursor.fetchall()
            print(f"\n📋 Products table columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]}) - nullable: {col[3]}, default: {col[4]}")
        else:
            print("\n❌ Products table not found!")
        
        # Check categories table schema
        if ('categories',) in tables:
            cursor.execute("PRAGMA table_info(categories)")
            columns = cursor.fetchall()
            print(f"\n📋 Categories table columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]}) - nullable: {col[3]}, default: {col[4]}")
        else:
            print("\n❌ Categories table not found!")
        
        # Check if there are any products
        if ('products',) in tables:
            cursor.execute("SELECT COUNT(*) FROM products")
            product_count = cursor.fetchone()[0]
            print(f"\n📦 Products count: {product_count}")
            
            if product_count > 0:
                cursor.execute("SELECT * FROM products LIMIT 1")
                sample = cursor.fetchone()
                print(f"🔍 Sample product: {sample}")
        
        # Check if there are any categories
        if ('categories',) in tables:
            cursor.execute("SELECT COUNT(*) FROM categories")
            cat_count = cursor.fetchone()[0]
            print(f"\n📦 Categories count: {cat_count}")
            
            if cat_count > 0:
                cursor.execute("SELECT * FROM categories LIMIT 1")
                sample = cursor.fetchone()
                print(f"🔍 Sample category: {sample}")
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    check_parent_db() 