#!/usr/bin/env python3
"""
Maya - AI Content Optimization for Social Platforms
Main application entry point
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os
import logging

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import get_settings

# Use standard logging for now, will upgrade to structlog later
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    settings = get_settings()
    
    app = FastAPI(
        title="Maya - AI Content Optimization",
        description="AI-powered content optimization for social media platforms",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    try:
        from app.api import api_router
        app.include_router(api_router)
        logger.info("API router loaded successfully")
    except ImportError as e:
        logger.warning(f"Could not import API router: {e}")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "maya-ai-content"}
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with service information"""
        return {
            "service": "Maya - AI Content Optimization",
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs" if settings.DEBUG else "disabled"
        }
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    logger.info("FastAPI application created successfully")
    return app

app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    
    logger.info(
        f"Starting Maya AI Content Optimization service on {settings.HOST}:{settings.PORT}"
    )
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )