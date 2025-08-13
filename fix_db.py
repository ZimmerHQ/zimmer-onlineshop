import sqlite3

def fix_database():
    try:
        # Connect to the database
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        
        # Check if thumbnail_url column exists
        cursor.execute("PRAGMA table_info(products)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'thumbnail_url' not in columns:
            print("Adding thumbnail_url column to products table...")
            cursor.execute("ALTER TABLE products ADD COLUMN thumbnail_url TEXT")
            conn.commit()
            print("✅ thumbnail_url column added successfully!")
        else:
            print("✅ thumbnail_url column already exists!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")

if __name__ == "__main__":
    fix_database() 