#!/usr/bin/env python3
"""
Unified server script for Render deployment
Starts both backend and frontend in a single process
"""

import os
import sys
import subprocess
import threading
import time
import signal
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting backend server...")
    try:
        # Use uvicorn to start the backend
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend failed to start: {e}")
        sys.exit(1)

def start_frontend():
    """Start the Next.js frontend server"""
    print("🎨 Starting frontend server...")
    
    # Change to frontend directory
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    try:
        # Check if frontend is already built
        if not (frontend_dir / ".next").exists():
            print("📦 Installing frontend dependencies...")
            subprocess.run(["npm", "install"], check=True)
            
            print("🔨 Building frontend for production...")
            subprocess.run(["npm", "run", "build"], check=True)
        
        # Start the production server
        print("🌐 Starting frontend production server...")
        subprocess.run(["npm", "start"], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend failed to start: {e}")
        sys.exit(1)

def main():
    """Main function to start both servers"""
    print("🎯 Starting unified server for Render deployment...")
    
    # Set environment variables for production
    os.environ.setdefault("ENVIRONMENT", "production")
    os.environ.setdefault("PORT", "8000")
    
    # Check if we're in development or production mode
    if os.environ.get("ENVIRONMENT") == "production":
        print("🏭 Production mode detected")
        # In production, we'll serve the frontend through the backend
        # The backend will handle both API and static files
        start_backend()
    else:
        print("🔧 Development mode detected")
        # In development, start both servers
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        frontend_thread = threading.Thread(target=start_frontend, daemon=True)
        
        backend_thread.start()
        time.sleep(2)  # Give backend time to start
        frontend_thread.start()
        
        # Wait for both threads
        backend_thread.join()
        frontend_thread.join()

if __name__ == "__main__":
    main() 