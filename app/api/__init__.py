"""
Main API router configuration
"""

from fastapi import APIRouter
from app.api import auth, content, ai

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include all route modules
api_router.include_router(auth.router)
api_router.include_router(content.router)
api_router.include_router(ai.router)