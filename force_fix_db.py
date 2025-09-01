#!/usr/bin/env python3
"""
Forcefully fix database schema by recreating the products table.
"""
import sqlite3
import os

def force_fix_database():
    """Forcefully fix database schema."""
    db_path = "app.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return
    
    print(f"🔧 Forcefully fixing database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check current schema
        cursor.execute("PRAGMA table_info(products)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 Current products table columns: {columns}")
        
        # Backup existing data
        cursor.execute("SELECT * FROM products")
        products_data = cursor.fetchall()
        print(f"📦 Backing up {len(products_data)} products...")
        
        # Drop and recreate the table
        print("🗑️ Dropping products table...")
        cursor.execute("DROP TABLE products")
        
        # Create new table with correct schema
        print("🏗️ Creating new products table...")
        cursor.execute("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR NOT NULL,
                description TEXT,
                price FLOAT NOT NULL,
                stock INTEGER DEFAULT 0,
                low_stock_threshold INTEGER NOT NULL DEFAULT 5,
                code VARCHAR NOT NULL UNIQUE,
                category_id INTEGER NOT NULL,
                image_url VARCHAR,
                thumbnail_url VARCHAR,
                sizes TEXT,
                tags VARCHAR,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        """)
        
        # Reinsert data if any existed
        if products_data:
            print("📥 Reinserting products data...")
            for product in products_data:
                # Handle the old schema (without low_stock_threshold, thumbnail_url, sizes)
                if len(product) == 13:  # Old schema
                    cursor.execute("""
                        INSERT INTO products (id, name, description, price, stock, code, category_id, 
                                           image_url, tags, is_active, created_at, updated_at, low_stock_threshold)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 5)
                    """, product + (5,))
                else:
                    # New schema or different length
                    cursor.execute("""
                        INSERT INTO products (id, name, description, price, stock, low_stock_threshold, 
                                           code, category_id, image_url, thumbnail_url, sizes, tags, 
                                           is_active, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, product)
        
        conn.commit()
        print("✅ Database schema fixed successfully!")
        
        # Verify the new schema
        cursor.execute("PRAGMA table_info(products)")
        new_columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 New products table columns: {new_columns}")
        
        # Check if data was preserved
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        print(f"📦 Products count after fix: {product_count}")
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    force_fix_database() 