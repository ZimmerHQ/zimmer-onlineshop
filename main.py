# main.py
import logging
from env import assert_openai_key  # makes sure .env is loaded and key exists

logging.basicConfig(level=logging.INFO)

# Validate early (comment this if you want to run without key)
try:
    assert_openai_key()
except Exception as e:
    # Optional: don't crash here; just log. If you want hard fail, re-raise.
    logging.warning(f"Startup warning: {e}")

# Create database tables
from database import engine
from models import Base
print("📋 Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Database tables created successfully")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Create FastAPI app instance
app = FastAPI()

# Add CORS middleware to allow requests from any origin (for demo purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"⬅️ {request.method} {request.url}")
    try:
        response = await call_next(request)
    except Exception as e:
        logging.error(f"🔥 Error while handling {request.url}: {repr(e)}")
        raise
    logging.info(f"➡️ Response status: {response.status_code}")
    return response

# Import your routers AFTER creating the app
from chat_handler import router as chat_router
app.include_router(chat_router)

# Add other routers as needed
from product_handler import router as product_router
app.include_router(product_router, prefix="/api/products")

from order_handler import router as order_router
app.include_router(order_router)

from upload_handler import router as upload_router
app.include_router(upload_router)

from conversations_handler import router as conversations_router
app.include_router(conversations_router)

# Add static files serving
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add webhook management router
from webhook_manager import router as webhook_router
app.include_router(webhook_router)

# Add telegram webhook router
from telegram_webhook import app as telegram_app
app.mount("/telegram", telegram_app)

@app.get("/api/health")
def health():
    return {"status": "ok", "message": "Backend API is running"}

# Fallback route for SPA routing (must be last)
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # Don't handle API routes
    if full_path.startswith("api/"):
        return {"status": "error", "message": "API endpoint not found"}
    
    # Debug logging
    print(f"🔍 Serving frontend for path: '{full_path}'")
    
    # Check for Next.js static files first
    static_file = os.path.join("frontend/.next/static", full_path)
    if os.path.exists(static_file) and os.path.isfile(static_file):
        print(f"✅ Serving static file: {static_file}")
        return FileResponse(static_file)
    
    # Check for Next.js build output in app directory with .html extension
    next_build_file = os.path.join("frontend/.next/server/app", f"{full_path}.html")
    if os.path.exists(next_build_file) and os.path.isfile(next_build_file):
        print(f"✅ Serving HTML file: {next_build_file}")
        return FileResponse(next_build_file)
    
    # Check for Next.js build output in app directory without extension
    next_build_file_no_ext = os.path.join("frontend/.next/server/app", full_path)
    if os.path.exists(next_build_file_no_ext) and os.path.isfile(next_build_file_no_ext):
        print(f"✅ Serving file without extension: {next_build_file_no_ext}")
        return FileResponse(next_build_file_no_ext)
    
    # Check for pages directory (legacy)
    next_pages_file = os.path.join("frontend/.next/server/pages", full_path)
    if os.path.exists(next_pages_file) and os.path.isfile(next_pages_file):
        print(f"✅ Serving pages file: {next_pages_file}")
        return FileResponse(next_pages_file)
    
    # Serve index.html for root path
    if full_path == "" or full_path == "/":
        index_path = os.path.join("frontend/.next/server/app", "index.html")
        if os.path.exists(index_path):
            print(f"✅ Serving index.html: {index_path}")
            return FileResponse(index_path)
        else:
            print(f"❌ index.html not found at: {index_path}")
    
    # Fallback to pages index
    pages_index_path = os.path.join("frontend/.next/server/pages", "index.html")
    if os.path.exists(pages_index_path):
        print(f"✅ Serving pages index.html: {pages_index_path}")
        return FileResponse(pages_index_path)
    
    # Debug: List what we found
    print(f"❌ No frontend file found for path: '{full_path}'")
    print(f"📂 Checking if frontend/.next exists: {os.path.exists('frontend/.next')}")
    if os.path.exists('frontend/.next'):
        print(f"📂 Checking if frontend/.next/server exists: {os.path.exists('frontend/.next/server')}")
        if os.path.exists('frontend/.next/server'):
            print(f"📂 Checking if frontend/.next/server/app exists: {os.path.exists('frontend/.next/server/app')}")
            if os.path.exists('frontend/.next/server/app'):
                try:
                    app_files = os.listdir('frontend/.next/server/app')
                    print(f"📄 Files in app directory: {app_files}")
                except Exception as e:
                    print(f"❌ Error listing app directory: {e}")
    
    # If no frontend build exists, return a helpful message
    return {"status": "error", "message": "Frontend not built. Please run 'npm run build' in the frontend directory."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)