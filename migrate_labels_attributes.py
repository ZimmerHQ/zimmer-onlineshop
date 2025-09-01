#!/usr/bin/env python3
"""
Migration script to add labels_json and attributes_json columns to products table.
Run this script to update your database schema.
"""

import sqlite3
import os
from pathlib import Path

def migrate_database():
    """Add new columns to products table."""
    
    # Get database path
    db_path = Path("app.db")
    if not db_path.exists():
        print("❌ Database file 'app.db' not found!")
        print("   Make sure you're running this from the backend directory.")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Checking current database schema...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(products)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"   Current columns: {', '.join(columns)}")
        
        # Add labels_json column if it doesn't exist
        if 'labels_json' not in columns:
            print("➕ Adding labels_json column...")
            cursor.execute("ALTER TABLE products ADD COLUMN labels_json TEXT NULL")
            print("   ✅ labels_json column added")
        else:
            print("   ℹ️  labels_json column already exists")
        
        # Add attributes_json column if it doesn't exist
        if 'attributes_json' not in columns:
            print("➕ Adding attributes_json column...")
            cursor.execute("ALTER TABLE products ADD COLUMN attributes_json TEXT NULL")
            print("   ✅ attributes_json column added")
        else:
            print("   ℹ️  attributes_json column already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify the new schema
        cursor.execute("PRAGMA table_info(products)")
        new_columns = [col[1] for col in cursor.fetchall()]
        print(f"\n🔍 New schema: {', '.join(new_columns)}")
        
        # Check for any existing products to backfill
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        
        if product_count > 0:
            print(f"\n📊 Found {product_count} existing products")
            print("   💡 Consider backfilling labels and attributes for better search")
            
            # Example of how to backfill (optional)
            print("\n   Example backfill query:")
            print("   UPDATE products SET labels_json = '[]', attributes_json = '{}'")
            print("   WHERE labels_json IS NULL OR attributes_json IS NULL")
        
        print("\n✅ Migration completed successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def backfill_example_data():
    """Example of how to backfill some products with sample labels/attributes."""
    
    db_path = Path("app.db")
    if not db_path.exists():
        print("❌ Database file not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔄 Backfilling example data...")
        
        # Example: Update a product with sample labels and attributes
        sample_labels = '["jeans", "pants", "casual"]'
        sample_attributes = '{"color": ["black", "blue"], "size": ["M", "L", "XL"], "material": ["denim"]}'
        
        # Find a product to update (assuming you have some)
        cursor.execute("SELECT id, name FROM products LIMIT 1")
        product = cursor.fetchone()
        
        if product:
            product_id, product_name = product
            print(f"   📝 Updating product {product_id} ({product_name})")
            
            cursor.execute("""
                UPDATE products 
                SET labels_json = ?, attributes_json = ?
                WHERE id = ?
            """, (sample_labels, sample_attributes, product_id))
            
            conn.commit()
            print("   ✅ Sample data added")
            print(f"   📋 Labels: {sample_labels}")
            print(f"   🏷️  Attributes: {sample_attributes}")
        else:
            print("   ℹ️  No products found to backfill")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 Starting Labels & Attributes Migration")
    print("=" * 50)
    
    # Run migration
    if migrate_database():
        # Optionally backfill example data
        response = input("\n🤔 Would you like to add sample labels/attributes to a product? (y/N): ")
        if response.lower() in ['y', 'yes']:
            backfill_example_data()
    
    print("\n✨ Migration script completed!")
    print("\n📚 Next steps:")
    print("   1. Restart your backend server")
    print("   2. Test creating/updating products with labels and attributes")
    print("   3. Test the enhanced search functionality")
    print("   4. Update your frontend to include the new fields") 