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
            "docs": "/docs" if settings.DEBUG else "disabled",
            "features": [
                "AI Content Processing",
                "Sentiment Analysis", 
                "Content Generation",
                "Platform Optimization",
                "Telegram Bot Integration"
            ]
        }
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        # Send alert via Telegram bot if configured
        try:
            from app.services.telegram_bot import get_telegram_bot
            bot = get_telegram_bot()
            if bot.is_running:
                await bot.send_alert(
                    "System Error",
                    f"Unhandled exception in API: {str(exc)[:100]}...",
                    "error"
                )
        except Exception as bot_error:
            logger.error(f"Failed to send Telegram alert: {bot_error}")
        
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    # Startup event
    @app.on_event("startup")
    async def startup_event():
        """Initialize services on startup"""
        logger.info("Maya AI Content Optimization starting up...")
        
        # Initialize Telegram bot
        try:
            from app.services.telegram_bot import start_telegram_bot
            telegram_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
            await start_telegram_bot(telegram_token)
            logger.info("Telegram bot initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Telegram bot: {e}")
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown"""
        logger.info("Maya AI Content Optimization shutting down...")
        
        # Stop Telegram bot
        try:
            from app.services.telegram_bot import stop_telegram_bot
            await stop_telegram_bot()
            logger.info("Telegram bot stopped")
        except Exception as e:
            logger.warning(f"Error stopping Telegram bot: {e}")
    
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