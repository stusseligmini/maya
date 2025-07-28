"""
Main API router configuration
"""

from fastapi import APIRouter
from app.api import auth, content, ai, webhooks, publishing, system, config

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include all route modules
api_router.include_router(auth.router)
api_router.include_router(content.router)
api_router.include_router(ai.router)
api_router.include_router(webhooks.router)
api_router.include_router(publishing.router)
api_router.include_router(system.router)
api_router.include_router(config.router)