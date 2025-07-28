"""
Main API router configuration
"""

from fastapi import APIRouter

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Basic health endpoint for the API
@api_router.get("/health")
async def api_health():
    """API health check"""
    return {
        "status": "healthy",
        "service": "maya-api",
        "version": "1.0.0"
    }

# Placeholder endpoints - will be expanded
@api_router.get("/models")
async def list_models():
    """List available AI models"""
    return {
        "models": [
            {
                "id": "openai-gpt-4",
                "name": "GPT-4",
                "provider": "OpenAI",
                "status": "available"
            },
            {
                "id": "openai-gpt-3.5-turbo", 
                "name": "GPT-3.5 Turbo",
                "provider": "OpenAI",
                "status": "available"
            }
        ]
    }

@api_router.get("/platforms")
async def list_platforms():
    """List supported social media platforms"""
    return {
        "platforms": [
            {
                "id": "twitter",
                "name": "Twitter/X",
                "status": "coming_soon"
            },
            {
                "id": "instagram", 
                "name": "Instagram",
                "status": "coming_soon"
            },
            {
                "id": "tiktok",
                "name": "TikTok", 
                "status": "coming_soon"
            },
            {
                "id": "linkedin",
                "name": "LinkedIn",
                "status": "coming_soon"
            }
        ]
    }

# Include route modules when they become available
# This will be uncommented as we implement each module
# try:
#     from app.api import auth, content, ai
#     api_router.include_router(auth.router)
#     api_router.include_router(content.router)
#     api_router.include_router(ai.router)
# except ImportError:
#     pass