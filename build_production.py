#!/usr/bin/env python3
"""
Production build script for Render deployment
Builds both backend and frontend for production
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a shell command and handle errors"""
    print(f"🔄 Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def main():
    """Main build function"""
    print("🏗️ Starting production build...")
    
    # Get the project root directory
    project_root = Path(__file__).parent
    frontend_dir = project_root / "frontend"
    
    # Step 1: Install Python dependencies
    print("📦 Installing Python dependencies...")
    run_command("pip install -r requirements.txt", cwd=project_root)
    
    # Step 2: Install Node.js dependencies
    print("📦 Installing Node.js dependencies...")
    run_command("npm install", cwd=frontend_dir)
    
    # Step 3: Build frontend
    print("🔨 Building frontend...")
    run_command("npm run build", cwd=frontend_dir)
    
    # Step 4: Create production directories
    print("📁 Creating production directories...")
    static_dir = project_root / "static"
    static_dir.mkdir(exist_ok=True)
    
    # Step 5: Copy frontend build to static directory
    print("📋 Copying frontend build...")
    out_dir = frontend_dir / "out"
    if out_dir.exists():
        # Copy the entire out directory to static
        if (static_dir / "frontend").exists():
            shutil.rmtree(static_dir / "frontend")
        shutil.copytree(out_dir, static_dir / "frontend")
        print("✅ Frontend build copied to static/frontend")
    else:
        print("⚠️ Frontend build not found in frontend/out")
    
    # Step 6: Create a simple start script
    print("📝 Creating start script...")
    start_script = project_root / "start_production.py"
    with open(start_script, 'w') as f:
        f.write('''#!/usr/bin/env python3
import os
import uvicorn
from main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
''')
    
    print("✅ Production build completed!")
    print("🚀 To start the production server, run:")
    print("   python start_production.py")

if __name__ == "__main__":
    main() 