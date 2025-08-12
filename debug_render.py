#!/usr/bin/env python3
"""
Debug script to check frontend build status on Render
"""
import os
import sys

def check_frontend_build():
    print("🔍 Checking frontend build status...")
    
    # Check if frontend directory exists
    frontend_dir = "frontend"
    if not os.path.exists(frontend_dir):
        print("❌ Frontend directory not found!")
        return False
    
    print(f"✅ Frontend directory exists: {frontend_dir}")
    
    # Check if .next directory exists
    next_dir = os.path.join(frontend_dir, ".next")
    if not os.path.exists(next_dir):
        print("❌ .next directory not found!")
        print("💡 This means the frontend wasn't built properly")
        return False
    
    print(f"✅ .next directory exists: {next_dir}")
    
    # Check .next contents
    try:
        next_contents = os.listdir(next_dir)
        print(f"📁 .next contents: {next_contents}")
    except Exception as e:
        print(f"❌ Error reading .next directory: {e}")
        return False
    
    # Check server directory
    server_dir = os.path.join(next_dir, "server")
    if not os.path.exists(server_dir):
        print("❌ .next/server directory not found!")
        return False
    
    print(f"✅ .next/server directory exists: {server_dir}")
    
    # Check app directory
    app_dir = os.path.join(server_dir, "app")
    if not os.path.exists(app_dir):
        print("❌ .next/server/app directory not found!")
        return False
    
    print(f"✅ .next/server/app directory exists: {app_dir}")
    
    # Check for index.html
    index_file = os.path.join(app_dir, "index.html")
    if not os.path.exists(index_file):
        print("❌ index.html not found!")
        print("💡 This is why the frontend isn't serving")
        return False
    
    print(f"✅ index.html exists: {index_file}")
    
    # Check file size
    try:
        size = os.path.getsize(index_file)
        print(f"📏 index.html size: {size} bytes")
    except Exception as e:
        print(f"❌ Error getting file size: {e}")
    
    # List some files in app directory
    try:
        app_files = os.listdir(app_dir)
        html_files = [f for f in app_files if f.endswith('.html')]
        print(f"📄 HTML files found: {html_files}")
    except Exception as e:
        print(f"❌ Error listing app directory: {e}")
    
    return True

def check_static_files():
    print("\n🔍 Checking static files...")
    
    static_dir = os.path.join("frontend", ".next", "static")
    if not os.path.exists(static_dir):
        print("❌ .next/static directory not found!")
        return False
    
    print(f"✅ .next/static directory exists: {static_dir}")
    
    try:
        static_contents = os.listdir(static_dir)
        print(f"📁 Static contents: {static_contents}")
    except Exception as e:
        print(f"❌ Error reading static directory: {e}")
    
    return True

def main():
    print("🚀 Render Frontend Debug Script")
    print("=" * 50)
    
    # Check current working directory
    print(f"📂 Current working directory: {os.getcwd()}")
    
    # Check if we're in the right place
    if not os.path.exists("main.py"):
        print("❌ main.py not found! Are we in the right directory?")
        return
    
    print("✅ main.py found - we're in the right directory")
    
    # Check frontend build
    frontend_ok = check_frontend_build()
    
    # Check static files
    static_ok = check_static_files()
    
    print("\n" + "=" * 50)
    if frontend_ok and static_ok:
        print("✅ Frontend build looks good!")
        print("💡 The issue might be in the main.py serving logic")
    else:
        print("❌ Frontend build has issues!")
        print("💡 Check the build process in render.yaml")

if __name__ == "__main__":
    main() 