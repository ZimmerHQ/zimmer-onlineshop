#!/usr/bin/env python3
"""
Run Zimmer database migration.
Creates the Zimmer integration tables.
"""

import sqlite3
import os
from pathlib import Path

def run_migration():
    """Run the Zimmer database migration."""
    # Get database path
    db_path = "app.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    # Read migration SQL
    migration_file = Path("migrations/add_zimmer_tables.sql")
    if not migration_file.exists():
        print(f"❌ Migration file {migration_file} not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Read and execute migration
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Execute migration (SQLite supports multiple statements)
        cursor.executescript(migration_sql)
        
        # Commit changes
        conn.commit()
        
        print("✅ Zimmer database migration completed successfully!")
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%automation%' OR name LIKE '%usage%' OR name LIKE '%session%'")
        tables = cursor.fetchall()
        
        print("📋 Created tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)

