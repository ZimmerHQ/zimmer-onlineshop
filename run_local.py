#!/usr/bin/env python3
"""
Local development startup script
Bypasses Render-specific configurations for local development
"""

import os
import sys
import uvicorn

# Set environment for local development
os.environ["ENV"] = "development"
os.environ["PORT"] = "8006"

print("🚀 Starting local development server...")
print("📍 Port: 8006")
print("🌍 Environment: development")

try:
    # Import and start the app
    from main import app
    
    print("✅ App imported successfully")
    print("🚀 Starting server on http://localhost:8006")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8006,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )
    
except Exception as e:
    print(f"❌ Error starting server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
