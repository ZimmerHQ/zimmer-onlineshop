#!/usr/bin/env python3
"""
Clear all data from the shop automation database
"""

import sqlite3
import os
from datetime import datetime

def clear_database():
    """Clear all data from the database"""
    db_path = "app.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return
    
    print(f"🗑️ Clearing all data from database: {db_path}")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get list of all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📋 Found tables: {', '.join(tables)}")
        
        # Count records before deletion
        total_records = 0
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            total_records += count
            print(f"  📊 {table}: {count} records")
        
        print(f"\n📈 Total records to delete: {total_records}")
        
        if total_records == 0:
            print("✅ Database is already empty!")
            return
        
        # Ask for confirmation
        confirm = input(f"\n⚠️  Are you sure you want to delete ALL {total_records} records? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Operation cancelled.")
            return
        
        # Disable foreign key constraints temporarily
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # Clear all tables
        deleted_records = 0
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
            deleted = cursor.rowcount
            deleted_records += deleted
            print(f"🗑️  Deleted {deleted} records from {table}")
        
        # Reset auto-increment counters
        for table in tables:
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
        
        # Re-enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Commit changes
        conn.commit()
        
        print(f"\n✅ Successfully deleted {deleted_records} records!")
        print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Verify database is empty
        print("\n🔍 Verifying database is empty...")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  📊 {table}: {count} records")
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    clear_database()
