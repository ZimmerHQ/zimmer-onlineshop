#!/usr/bin/env python3
"""
Update the database in the parent directory with missing columns.
"""
import sqlite3
import os

def update_parent_db():
    """Update the database in the parent directory with missing columns."""
    db_path = "../app.db"
    
    print(f"🔧 Updating database: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check current products table schema
        cursor.execute("PRAGMA table_info(products)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 Current products table columns: {columns}")
        
        # Add missing columns
        missing_columns = []
        
        if 'low_stock_threshold' not in columns:
            missing_columns.append('low_stock_threshold')
        if 'thumbnail_url' not in columns:
            missing_columns.append('thumbnail_url')
        if 'sizes' not in columns:
            missing_columns.append('sizes')
        
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
        
        # Update existing products to have default values for new columns
        if 'low_stock_threshold' in columns:
            cursor.execute("UPDATE products SET low_stock_threshold = 5 WHERE low_stock_threshold IS NULL")
            print("✅ Updated existing products with default low_stock_threshold")
        
        if 'thumbnail_url' in columns:
            cursor.execute("UPDATE products SET thumbnail_url = image_url WHERE thumbnail_url IS NULL")
            print("✅ Updated existing products with thumbnail_url = image_url")
        
        if 'sizes' in columns:
            cursor.execute("UPDATE products SET sizes = 'S,M,L,XL' WHERE sizes IS NULL")
            print("✅ Updated existing products with default sizes")
        
        conn.commit()
        print("🎉 Database updated successfully!")
        
    except Exception as e:
        print(f"❌ Error updating database: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    update_parent_db() 