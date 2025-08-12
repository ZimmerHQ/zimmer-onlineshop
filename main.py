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
    
    # Check for production build first
    frontend_file = os.path.join("frontend/out", full_path)
    if os.path.exists(frontend_file) and os.path.isfile(frontend_file):
        return FileResponse(frontend_file)
    
    # Check for Next.js build output
    next_build_file = os.path.join("frontend/.next/server/pages", full_path)
    if os.path.exists(next_build_file) and os.path.isfile(next_build_file):
        return FileResponse(next_build_file)
    
    # Serve index.html for SPA routing
    index_path = os.path.join("frontend/out", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    # Fallback to Next.js index
    next_index_path = os.path.join("frontend/.next/server/pages", "index.html")
    if os.path.exists(next_index_path):
        return FileResponse(next_index_path)
    
    # If no frontend build exists, return a helpful message
    return {"status": "error", "message": "Frontend not built. Please run 'npm run build' in the frontend directory."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)