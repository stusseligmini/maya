#!/usr/bin/env python3
"""
Maya - AI Content Optimization for Social Platforms
Main application entry point
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import get_settings
from app.api import api_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

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
    
    # Add CORS middleware with production-ready settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
    
    # Add security headers middleware for production
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        if not settings.DEBUG:
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response
    
    # Include API routes
    app.include_router(api_router)
    
    # Enhanced health check endpoint for Render
    @app.get("/health")
    async def health_check():
        """Health check endpoint optimized for Render monitoring"""
        try:
            # Check database connectivity
            from database.connection import check_db_health
            db_healthy = check_db_health()
            
            status = "healthy" if db_healthy else "unhealthy"
            return {
                "status": status,
                "service": "maya-ai-content",
                "version": "1.0.0",
                "timestamp": "2024-01-01T00:00:00Z",
                "environment": getattr(settings, 'ENVIRONMENT', 'development'),
                "database": "healthy" if db_healthy else "unhealthy"
            }
        except Exception as e:
            logger.error("Health check failed", exc_info=e)
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "service": "maya-ai-content",
                    "error": "Service unavailable"
                }
            )
    
    # Root endpoint with enhanced information
    @app.get("/")
    async def root():
        """Root endpoint with service information"""
        return {
            "service": "Maya - AI Content Optimization",
            "version": "1.0.0",
            "status": "running",
            "environment": getattr(settings, 'ENVIRONMENT', 'development'),
            "docs": "/docs" if settings.DEBUG else "disabled",
            "health_check": "/health",
            "api_base": "/api/v1",
            "features": {
                "webhooks": "/api/v1/webhooks",
                "publishing": "/api/v1/publishing",
                "system_monitoring": "/api/v1/system",
                "ai_processing": "/api/v1/ai",
                "content_management": "/api/v1/content"
            }
        }
    
    # Enhanced global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error("Unhandled exception", exc_info=exc, path=str(request.url))
        
        # Don't expose internal errors in production
        if settings.DEBUG:
            detail = str(exc)
        else:
            detail = "Internal server error"
            
        return JSONResponse(
            status_code=500,
            content={"detail": detail}
        )
    
    # Startup event for initialization
    @app.on_event("startup")
    async def startup_event():
        logger.info("Maya AI Content Optimization service starting up")
        
        # Initialize database if needed
        try:
            from database.connection import init_db
            init_db()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error("Database initialization failed", exc_info=e)
    
    # Shutdown event for cleanup
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Maya AI Content Optimization service shutting down")
        
        try:
            from database.connection import close_db
            close_db()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error("Error during shutdown", exc_info=e)
    
    logger.info("FastAPI application created successfully")
    return app

app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    
    # Use PORT environment variable for Render deployment
    port = int(os.getenv("PORT", settings.PORT))
    
    logger.info(
        "Starting Maya AI Content Optimization service",
        host=settings.HOST,
        port=port,
        debug=settings.DEBUG,
        environment=getattr(settings, 'ENVIRONMENT', 'development')
    )
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=port,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
        access_log=settings.DEBUG,
        workers=1 if settings.DEBUG else 4
    )