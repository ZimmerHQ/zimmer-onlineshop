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
    print("⚠️  OpenAI API key not found. Some features may not work.")

# Create database tables
from database import engine
from models import Base
from models.category import Category
from models.product import Product

print("📋 Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Database tables created successfully")

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Create FastAPI app instance
app = FastAPI(
    title="Online Shop API",
    description="FastAPI + SQLAlchemy online shop backend with categories, products, and import functionality",
    version="2.0.0"
)

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

# Import new routers
from routers.categories import router as categories_router
from routers.products import router as products_router
from routers.imports import router as imports_router

# Include new routers
app.include_router(categories_router, prefix="/api")
app.include_router(products_router, prefix="/api")
app.include_router(imports_router, prefix="/api")

# Import existing routers AFTER creating the app
from chat_handler import router as chat_router
app.include_router(chat_router)

# Add other existing routers as needed
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

# Add Next.js static files serving
app.mount("/_next", StaticFiles(directory="frontend/.next"), name="next_static")

# Add webhook management router
from webhook_manager import router as webhook_router
app.include_router(webhook_router)

# Add telegram webhook router
from telegram_webhook import app as telegram_app
app.mount("/telegram", telegram_app)

@app.get("/api/health")
def health():
    try:
        # Test database connection
        from database import get_db
        from sqlalchemy.orm import Session
        from sqlalchemy import text
        
        db = next(get_db())
        result = db.execute(text("SELECT 1"))
        db.close()
        
        return {
            "status": "healthy", 
            "message": "Backend API is running",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "message": f"Server error: {str(e)}",
            "database": "error"
        }

# Note: Removed fallback route to prevent interference with API routes
# The frontend should be served by a separate server (Next.js dev server)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 