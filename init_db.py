#!/usr/bin/env python3
"""
Simple database initialization script.
"""

import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database import engine
    print("✅ Database engine imported successfully")
    
    from models import Base
    print("✅ Models Base imported successfully")
    
    # Check what models are available
    print(f"📋 Available models: {[name for name in dir(Base.metadata) if not name.startswith('_')]}")
    
    # Check tables
    print(f"📋 Tables in metadata: {list(Base.metadata.tables.keys())}")
    
    print("📋 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
    
    # Verify tables were created
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"📋 Tables in database: {tables}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
