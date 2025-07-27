#!/usr/bin/env python3
"""
Maya AI Content Optimization System - Main Application
"""
import uvicorn
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio
from pathlib import Path
import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting Maya AI Content Optimization System")
    
    # Create directories
    directories = [
        "logs", "input/images_raw", "input/captions_raw", 
        "input/videos_raw", "storage", "temp", "static"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Initialize database (optional for now)
    try:
        logger.info("🗄️  Initializing database...")
        # We'll skip complex DB setup for now to get the API running
        logger.info("✅ Database setup deferred")
    except Exception as e:
        logger.warning(f"⚠️  Database setup skipped: {str(e)}")
    
    logger.info("🎉 Maya AI system fully initialized")
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down Maya AI system...")
    logger.info("👋 Maya AI system shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Maya AI Content Optimization System",
    description="""
    ## 🚀 Maya AI Content Optimization System

    A comprehensive AI-powered content optimization platform that automates:
    
    - **🖼️ Image Generation** with Fooocus integration
    - **📝 Caption Generation** using OpenAI GPT models  
    - **🔍 Content Moderation** with NSFW detection
    - **📊 Performance Analytics** and insights
    - **📱 Multi-Platform Publishing** (Instagram, TikTok, Twitter, etc.)
    - **🤖 Telegram Review Workflow** for content approval
    - **🔄 Background Processing** with Celery workers
    - **📈 Real-time Monitoring** and metrics

    ### 🏗️ Architecture Features:
    - Microservices architecture with Docker
    - Async processing with Redis queues
    - PostgreSQL database with comprehensive models
    - AI model integration (OpenAI, Hugging Face)
    - Automated content workflow
    - Security and rate limiting
    - Health monitoring and alerting

    ### 🔗 Quick Start:
    1. Upload content via `/api/content/upload`
    2. Monitor processing via `/api/queue/status`
    3. Review via Telegram bot integration
    4. Publish to platforms via `/api/content/{id}/publish`

    ### 📊 Monitoring:
    - Flower UI: http://localhost:5555 (Celery monitoring)
    - Health checks: `/health`
    - Metrics: `/metrics`
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
try:
    from api.routes import router as api_router
    app.include_router(api_router, prefix="/api", tags=["Maya AI API"])
    logger.info("✅ API routes loaded successfully")
except Exception as e:
    logger.warning(f"⚠️  Could not load API router: {str(e)}")

# Static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    # Directory doesn't exist, create it
    Path("static").mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "Maya AI Content Optimization System"
    }

# Metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    return {
        "system": {
            "status": "running",
            "version": "1.0.0"
        }
    }

# Root endpoint - redirect to dashboard
@app.get("/")
async def root():
    """Root endpoint - serve the modern dashboard"""
    from fastapi.responses import FileResponse
    return FileResponse('static/index.html')

# Upload page
@app.get("/upload")
async def upload_page():
    """Upload page for content"""
    from fastapi.responses import FileResponse
    return FileResponse('static/upload.html')

# Analytics page
@app.get("/analytics")
async def analytics_page():
    """Real-time analytics page"""
    from fastapi.responses import FileResponse
    return FileResponse('static/analytics.html')

# Mobile App endpoint - PWA for iOS/Android
@app.get("/app")
async def mobile_app():
    """Serve the mobile PWA application"""
    from fastapi.responses import FileResponse
    return FileResponse('static/mobile-app.html')

# API info endpoint
@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "message": "🚀 Maya AI Content Optimization System API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
        "dashboard": "/",
        "features": [
            "🖼️ AI Image Generation",
            "📝 Smart Caption Generation", 
            "🔍 Content Moderation",
            "📱 Multi-Platform Publishing",
            "🤖 Telegram Integration",
            "📊 Performance Analytics",
            "🔄 Background Processing",
            "📈 Real-time Monitoring"
        ],
        "architecture": {
            "api": "FastAPI + Uvicorn",
            "database": "PostgreSQL",
            "cache": "Redis", 
            "queue": "Celery",
            "ai": "OpenAI + Hugging Face",
            "containerization": "Docker + Docker Compose"
        }
    }

if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
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
    
    # Health check endpoint
    @app.get("/health")
    def health_check():
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
            "docs": "/docs"
        }

if __name__ == "__main__":
    # Render deployment - use PORT environment variable or default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload for production
        log_level="info"
    )