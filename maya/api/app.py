"""FastAPI application for Maya AI Content System."""

from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from contextlib import asynccontextmanager
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from maya.config.settings import get_settings
from maya.core.logging import configure_logging, get_logger
from maya.monitoring.metrics import (
    prometheus_metrics, 
    performance_tracker, 
    health_monitor, 
    update_system_metrics_task,
    MonitoringMiddleware,
    configure_sentry
)
from maya.security.auth import (
    get_current_user, 
    require_scopes, 
    TokenData,
    SecurityHeaders,
    rate_limiter
)
from maya.content.processor import ContentProcessor, ContentItem, ContentType, Platform
from maya.social.platforms import social_manager
from maya.ai.models import ai_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger = get_logger("Application")
    
    # Startup
    logger.info("Starting Maya AI Content System")
    
    # Start background tasks
    metrics_task = asyncio.create_task(update_system_metrics_task())
    
    try:
        yield
    finally:
        # Shutdown
        logger.info("Shutting down Maya AI Content System")
        metrics_task.cancel()
        try:
            await metrics_task
        except asyncio.CancelledError:
            pass


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    # Configure logging
    configure_logging(
        level=settings.monitoring.log_level,
        json_logs=settings.monitoring.json_logs
    )
    
    # Configure Sentry
    configure_sentry()
    
    app = FastAPI(
        title="Maya AI Content System",
        description="AI-powered content optimization for social media platforms",
        version="0.1.0",
        lifespan=lifespan
    )
    
    # Add security headers middleware
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        for header, value in SecurityHeaders.get_security_headers().items():
            response.headers[header] = value
        return response
    
    # Add monitoring middleware
    monitoring_middleware = MonitoringMiddleware(prometheus_metrics, performance_tracker)
    app.middleware("http")(monitoring_middleware)
    
    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app


app = create_app()
content_processor = ContentProcessor()
logger = get_logger("API")


# Health and monitoring endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    health_status = await health_monitor.run_all_health_checks()
    overall_health = health_monitor.get_overall_health()
    
    status_code = 200 if overall_health == "healthy" else 503
    
    return {
        "status": overall_health,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {name: {
            "status": check.status,
            "details": check.details,
            "response_time_ms": check.response_time_ms
        } for name, check in health_status.items()}
    }


@app.get("/metrics", response_class=PlainTextResponse)
async def get_metrics():
    """Prometheus metrics endpoint."""
    return prometheus_metrics.get_metrics()


@app.get("/performance")
async def get_performance_stats(current_user: TokenData = Depends(require_scopes(["admin"]))):
    """Get performance statistics."""
    return performance_tracker.get_all_stats()


# Authentication endpoints
@app.post("/auth/token")
async def create_token(username: str, password: str):
    """Create access token (simplified for demo)."""
    # In a real implementation, verify credentials against database
    if username == "demo" and password == "demo123":
        from maya.security.auth import jwt_manager
        
        token = jwt_manager.create_access_token(
            user_id="demo_user",
            username=username,
            email="demo@maya-ai.com",
            scopes=["read", "write", "admin"]
        )
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": jwt_manager.access_token_expire_minutes * 60
        }
    
    raise HTTPException(status_code=401, detail="Invalid credentials")


# Content processing endpoints
@app.post("/content/process")
async def process_content(
    text: str,
    content_type: str = "text",
    target_platforms: List[str] = None,
    analyze_with_ai: bool = True,
    current_user: TokenData = Depends(require_scopes(["write"]))
):
    """Process content for optimization."""
    
    # Rate limiting
    if not rate_limiter.is_allowed(current_user.user_id, max_requests=50):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    try:
        # Create content item
        content_item = ContentItem(
            id=None,  # Will be auto-generated
            content_type=ContentType(content_type),
            text=text
        )
        
        # Parse target platforms
        if target_platforms is None:
            target_platforms = ["twitter", "instagram"]
        
        platforms = [Platform(p) for p in target_platforms]
        
        # Process content
        result = await content_processor.process_content(
            content_item, 
            platforms, 
            analyze_with_ai
        )
        
        logger.info("Content processed successfully", 
                   content_id=content_item.id, 
                   user_id=current_user.user_id)
        
        return result.to_dict()
        
    except Exception as e:
        logger.error("Content processing failed", 
                    user_id=current_user.user_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Content processing failed: {str(e)}")


@app.post("/content/publish")
async def publish_content(
    content_id: str,
    text: str,
    platforms: List[str],
    current_user: TokenData = Depends(require_scopes(["write"]))
):
    """Publish content to social platforms."""
    
    # Rate limiting
    if not rate_limiter.is_allowed(current_user.user_id, max_requests=20):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    try:
        # Create content item
        content_item = ContentItem(
            id=content_id,
            content_type=ContentType.TEXT,
            text=text
        )
        
        # Parse platforms
        platform_enums = [Platform(p) for p in platforms]
        
        # Publish to platforms
        results = await social_manager.publish_to_platforms(content_item, platform_enums)
        
        # Convert results to serializable format
        response = {}
        for platform, result in results.items():
            response[platform.value] = {
                "post_id": result.post_id,
                "url": result.url,
                "status": result.status,
                "metadata": result.metadata
            }
        
        logger.info("Content published successfully", 
                   content_id=content_id, 
                   platforms=platforms,
                   user_id=current_user.user_id)
        
        return response
        
    except Exception as e:
        logger.error("Content publishing failed", 
                    content_id=content_id, 
                    user_id=current_user.user_id, 
                    error=str(e))
        raise HTTPException(status_code=500, detail=f"Content publishing failed: {str(e)}")


@app.post("/content/schedule")
async def schedule_content(
    content_id: str,
    text: str,
    platforms: List[str],
    publish_time: str,  # ISO format datetime
    current_user: TokenData = Depends(require_scopes(["write"]))
):
    """Schedule content for future publishing."""
    
    try:
        # Parse publish time
        publish_datetime = datetime.fromisoformat(publish_time.replace('Z', '+00:00'))
        
        # Create content item
        content_item = ContentItem(
            id=content_id,
            content_type=ContentType.TEXT,
            text=text
        )
        
        # Parse platforms
        platform_enums = [Platform(p) for p in platforms]
        
        # Schedule content
        results = await social_manager.schedule_for_platforms(
            content_item, 
            platform_enums, 
            publish_datetime
        )
        
        # Convert results to serializable format
        response = {}
        for platform, result in results.items():
            response[platform.value] = {
                "post_id": result.post_id,
                "scheduled_time": result.scheduled_time.isoformat() if result.scheduled_time else None,
                "status": result.status,
                "metadata": result.metadata
            }
        
        logger.info("Content scheduled successfully", 
                   content_id=content_id, 
                   platforms=platforms,
                   publish_time=publish_time,
                   user_id=current_user.user_id)
        
        return response
        
    except Exception as e:
        logger.error("Content scheduling failed", 
                    content_id=content_id, 
                    user_id=current_user.user_id, 
                    error=str(e))
        raise HTTPException(status_code=500, detail=f"Content scheduling failed: {str(e)}")


@app.delete("/content/{post_id}")
async def unpublish_content(
    post_id: str,
    platform: str,
    current_user: TokenData = Depends(require_scopes(["write"]))
):
    """Unpublish content from a platform."""
    
    try:
        platform_enum = Platform(platform)
        platform_integration = social_manager.get_platform(platform_enum)
        
        success = await platform_integration.unpublish_content(post_id)
        
        logger.info("Content unpublished", 
                   post_id=post_id, 
                   platform=platform,
                   user_id=current_user.user_id,
                   success=success)
        
        return {"success": success, "post_id": post_id, "platform": platform}
        
    except Exception as e:
        logger.error("Content unpublishing failed", 
                    post_id=post_id, 
                    platform=platform,
                    user_id=current_user.user_id, 
                    error=str(e))
        raise HTTPException(status_code=500, detail=f"Content unpublishing failed: {str(e)}")


# AI model endpoints
@app.get("/ai/models")
async def list_ai_models(current_user: TokenData = Depends(require_scopes(["read"]))):
    """List available AI models."""
    models = ai_manager.list_available_models()
    return {"available_models": models}


@app.post("/ai/analyze")
async def analyze_content_ai(
    text: str,
    model_type: str = "huggingface",
    current_user: TokenData = Depends(require_scopes(["read"]))
):
    """Analyze content using AI models."""
    
    try:
        model = ai_manager.get_model(model_type)
        analysis = await model.analyze_content(text)
        
        logger.info("AI content analysis completed", 
                   model_type=model_type,
                   user_id=current_user.user_id)
        
        return analysis
        
    except Exception as e:
        logger.error("AI content analysis failed", 
                    model_type=model_type,
                    user_id=current_user.user_id, 
                    error=str(e))
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")


@app.post("/ai/generate")
async def generate_content_ai(
    prompt: str,
    model_type: str = "openai",
    max_tokens: int = 150,
    current_user: TokenData = Depends(require_scopes(["write"]))
):
    """Generate content using AI models."""
    
    # Rate limiting for AI generation
    if not rate_limiter.is_allowed(f"{current_user.user_id}_ai_generate", max_requests=10):
        raise HTTPException(status_code=429, detail="AI generation rate limit exceeded")
    
    try:
        model = ai_manager.get_model(model_type)
        content = await model.generate_content(prompt, max_tokens=max_tokens)
        
        logger.info("AI content generation completed", 
                   model_type=model_type,
                   user_id=current_user.user_id)
        
        return {"generated_content": content, "model_type": model_type}
        
    except Exception as e:
        logger.error("AI content generation failed", 
                    model_type=model_type,
                    user_id=current_user.user_id, 
                    error=str(e))
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


# Social platform endpoints
@app.get("/social/platforms")
async def list_platforms(current_user: TokenData = Depends(require_scopes(["read"]))):
    """List supported social platforms."""
    platforms = social_manager.list_supported_platforms()
    return {"supported_platforms": [p.value for p in platforms]}


@app.get("/social/scheduled")
async def get_scheduled_posts(
    platform: Optional[str] = None,
    current_user: TokenData = Depends(require_scopes(["read"]))
):
    """Get scheduled posts."""
    
    platform_enum = Platform(platform) if platform else None
    scheduled_posts = social_manager.get_scheduled_posts(platform_enum)
    
    response = []
    for post in scheduled_posts:
        response.append({
            "id": post.id,
            "platform": post.platform.value,
            "scheduled_time": post.scheduled_time.isoformat(),
            "status": post.status,
            "content": {
                "id": post.content.id,
                "text": post.content.text,
                "content_type": post.content.content_type.value
            }
        })
    
    return {"scheduled_posts": response}


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    
    uvicorn.run(
        "maya.api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )