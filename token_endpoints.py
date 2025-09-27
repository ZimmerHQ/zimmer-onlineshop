
# Add these endpoints to your main.py or create a new router

from fastapi import APIRouter
from token_tracker import get_token_dashboard, get_session_token_info, tracker
from token_calculator import calculator

# Create token tracking router
token_router = APIRouter(prefix="/api/tokens", tags=["tokens"])

@token_router.get("/dashboard")
async def get_token_dashboard_endpoint():
    """Get comprehensive token usage dashboard"""
    return get_token_dashboard()

@token_router.get("/session/{session_id}")
async def get_session_tokens(session_id: str):
    """Get token usage for a specific session"""
    return get_session_token_info(session_id)

@token_router.get("/optimization")
async def get_optimization_recommendations():
    """Get optimization recommendations"""
    return tracker.get_optimization_dashboard()

@token_router.get("/export")
async def export_token_data():
    """Export all token usage data"""
    filename = calculator.export_data()
    return {"filename": filename, "message": "Data exported successfully"}

# Include this router in your main app
# app.include_router(token_router)
