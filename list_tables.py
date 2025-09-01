#!/usr/bin/env python3
"""
List all tables in the database.
"""
import sqlite3

def list_tables():
    """List all tables in the database."""
    db_path = "app.db"
    
    print(f"🔍 Listing tables in: {db_path}")
    
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
        
        # Check if database file exists and has content
        import os
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            print(f"\n📁 Database file size: {size} bytes")
        else:
            print("\n❌ Database file not found!")
        
    except Exception as e:
        print(f"❌ Error listing tables: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    list_tables() 