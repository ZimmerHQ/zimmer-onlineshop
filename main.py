# main.py
import logging
import os

# Load configuration first
from config import CORS_ORIGINS, IS_PRODUCTION, print_config_summary

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Print configuration summary
print_config_summary()

# Validate OpenAI API key in production
if IS_PRODUCTION:
    try:
        from env import assert_openai_key
        assert_openai_key()
        logger.info("✅ OpenAI API key validated")
    except Exception as e:
        logger.error(f"❌ OpenAI API key validation failed: {e}")
        raise

# Create database tables
from database import engine, Base
logger.info("📋 Creating database tables...")
Base.metadata.create_all(bind=engine)
logger.info("✅ Database tables created successfully")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Create FastAPI app instance
app = FastAPI(
    title="Zimmer Backend API",
    description="Backend API for Zimmer e-commerce platform",
    version="1.0.0"
)

# Add CORS middleware with dynamic origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import uuid
from fastapi.responses import JSONResponse

@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    request.headers.__dict__["_list"].append((b"x-request-id", request_id.encode()))
    
    logging.info(f"⬅️ [{request_id}] {request.method} {request.url}")
    try:
        response = await call_next(request)
        logging.info(f"➡️ [{request_id}] Response status: {response.status_code}")
        return response
    except Exception as e:
        logging.error(f"🔥 [{request_id}] Error while handling {request.url}: {repr(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "internal_error", "request_id": request_id}
        )

# Import your routers AFTER creating the app
from routers.chat import router as chat_router
app.include_router(chat_router)

# Add other routers as needed
from routers.products import router as products_router
app.include_router(products_router, prefix="/api/products", tags=["products"])

from routers.orders import router as orders_router
app.include_router(orders_router, prefix="/api/orders", tags=["orders"])

# Remove duplicate product_handler router since we're using routers.products
# from product_handler import router as product_router
# app.include_router(product_router, prefix="/api/products")

# Remove duplicate order_handler router since we're using routers.orders
# from order_handler import router as order_router
# app.include_router(order_router)

from upload_handler import router as upload_router
app.include_router(upload_router)

from conversations_handler import router as conversations_router
app.include_router(conversations_router)

from routers.imports import router as imports_router
app.include_router(imports_router, prefix="/api/imports")

from routers.categories import router as categories_router
app.include_router(categories_router, prefix="/api/categories")

# Add health router
from routers.health import router as health_router
app.include_router(health_router, prefix="/api")

# Add Telegram router
from routers.telegram import router as telegram_router
app.include_router(telegram_router, prefix="/api/telegram", tags=["telegram"])

# Add Analytics router
from routers.analytics import router as analytics_router
app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])

# Add Integrations router
from routers.integrations import router as integrations_router
app.include_router(integrations_router, prefix="/api/integrations", tags=["integrations"])



# Add Conversations router
from routers.conversations import router as conversations_router_new
app.include_router(conversations_router_new, prefix="/api/conversations", tags=["conversations"])

# Add FAQ router
from routers.faq import router as faq_router
app.include_router(faq_router, prefix="/api/faq", tags=["faq"])

# Add static files serving
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add Next.js static files serving
# app.mount("/_next", StaticFiles(directory="frontend/.next"), name="next_static")

# Add webhook management router
from webhook_manager import router as webhook_router
app.include_router(webhook_router)

# Add telegram webhook router
from telegram_webhook import app as telegram_app
app.mount("/telegram", telegram_app)

# Add direct webhook endpoint for easier access
@app.post("/api/telegram/webhook")
async def telegram_webhook_direct(request: Request):
    """Direct Telegram webhook endpoint."""
    from telegram_webhook import telegram_webhook
    from database import get_db
    db = next(get_db())
    return await telegram_webhook(request, db)

# Setup APScheduler for automated reports
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from services.reports_service import ReportsService
    from database import get_db
    
    scheduler = BackgroundScheduler()
    
    def generate_weekly_report():
        """Generate weekly report every Monday at 00:10"""
        try:
            db = next(get_db())
            reports_service = ReportsService(db)
            reports_service.generate_report("weekly")
            logging.info("✅ Weekly report generated successfully")
        except Exception as e:
            logging.error(f"❌ Error generating weekly report: {e}")
    
    def generate_monthly_report():
        """Generate monthly report on 1st day at 00:15"""
        try:
            db = next(get_db())
            reports_service = ReportsService(db)
            reports_service.generate_report("monthly")
            logging.info("✅ Monthly report generated successfully")
        except Exception as e:
            logging.error(f"❌ Error generating monthly report: {e}")
    
    # Schedule jobs
    scheduler.add_job(
        generate_weekly_report,
        CronTrigger(day_of_week='mon', hour=0, minute=10),
        id='weekly_report',
        name='Generate Weekly Sales Report'
    )
    
    scheduler.add_job(
        generate_monthly_report,
        CronTrigger(day=1, hour=0, minute=15),
        id='monthly_report',
        name='Generate Monthly Sales Report'
    )
    
    # Start scheduler
    scheduler.start()
    logging.info("🚀 APScheduler started for automated reports")
    
except ImportError:
    logging.warning("⚠️ APScheduler not available. Automated reports disabled.")
except Exception as e:
    logging.error(f"❌ Error setting up scheduler: {e}")

# Fallback route for SPA routing (must be last)
# Temporarily commented out to fix API routing issues
# @app.get("/{full_path:path}")
# async def serve_frontend(full_path: str):
#     # Don't handle API routes - let them pass through to their respective routers
#     if full_path.startswith("api/"):
#         raise HTTPException(status_code=404, detail="API endpoint not found")
#     
#     # For now, just return a simple message
#     return {"status": "error", "message": "Frontend not built. Please run 'npm run build' in the frontend directory."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)