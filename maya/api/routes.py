"""
API routes module for Maya system.

This module provides API routes for content processing, AI services,
authentication, and platform optimization.
"""

import structlog
from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from maya.core.exceptions import ServiceError, AuthenticationError
from maya.core.config import get_settings

from maya.security.auth import get_current_user
from app.models.user import User
from maya.services.services import ai_service, content_service, platform_service
from maya.worker.worker import worker_manager
from maya.api.integrations import n8n_router

logger = structlog.get_logger()
settings = get_settings()

# Create router
router = APIRouter()


# Include integration routers
router.include_router(
    n8n_router,
    prefix="/integrations",
    tags=["integrations"]
)

# Root endpoint
@router.get("/")
async def root():
    return {"message": "Maya API is running. See /docs for documentation."}




# --- Simple login endpoint ---
from fastapi import Request
from maya.security.auth import password_manager, jwt_manager
from sqlalchemy.orm import Session
from database.connection import get_db
from app.models.user import User as DBUser

from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/auth/login", tags=["auth"])
async def login(
    login_req: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(DBUser).filter(DBUser.username == login_req.username).first()
    if not user or not password_manager.verify_password(login_req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = jwt_manager.create_access_token(
        user_id=str(user.id),
        username=user.username,
        email=user.email,
        scopes=["user"]
    )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/auth/me", tags=["auth"])
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    return {
        "username": current_user.username,
        "email": current_user.email,
        "roles": current_user.roles
    }


# AI routes
@router.post("/ai/generate", tags=["ai"])
async def generate_content(
    prompt: str = Body(...),
    model_type: str = Body("openai"),
    max_tokens: int = Body(150),
    temperature: float = Body(0.7),
    current_user: User = Depends(get_current_user)
):
    """Generate content using AI models."""
    try:
        result = await ai_service.generate_content(
            prompt,
            model_type=model_type,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return result
    except ServiceError as e:
        logger.error("Content generation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/ai/analyze", tags=["ai"])
async def analyze_content(
    content: str = Body(...),
    model_types: Optional[List[str]] = Body(None),
    current_user: User = Depends(get_current_user)
):
    """Analyze content using AI models."""
    try:
        result = await ai_service.analyze_content(content, model_types=model_types)
        return result
    except ServiceError as e:
        logger.error("Content analysis failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/ai/models", tags=["ai"])
async def list_ai_models(current_user: User = Depends(get_current_user)):
    """List available AI models."""
    try:
        from maya.ai.models import ai_manager
        available_models = ai_manager.list_available_models()
        return {"available_models": available_models}
    except Exception as e:
        logger.error("Failed to list AI models", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list AI models"
        )


# Content routes
@router.post("/content/process", tags=["content"])
async def process_content(
    content_data: Dict[str, Any] = Body(...),
    target_platforms: Optional[List[str]] = Body(None),
    analyze_with_ai: bool = Body(True),
    current_user: User = Depends(get_current_user)
):
    """Process content for optimization."""
    try:
        result = await content_service.process_content(
            content_data,
            target_platforms=target_platforms,
            analyze_with_ai=analyze_with_ai
        )
        return result
    except ServiceError as e:
        logger.error("Content processing failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/content/process/image", tags=["content"])
async def process_image(
    image_path: str = Body(...),
    target_platform: Optional[str] = Body(None),
    metadata: Optional[Dict[str, Any]] = Body(None),
    current_user: User = Depends(get_current_user)
):
    """Process image content for optimization."""
    try:
        result = await content_service.process_image(
            image_path,
            target_platform=target_platform,
            metadata=metadata
        )
        return result
    except ServiceError as e:
        logger.error("Image processing failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/content/process/video", tags=["content"])
async def process_video(
    video_path: str = Body(...),
    target_platform: Optional[str] = Body(None),
    metadata: Optional[Dict[str, Any]] = Body(None),
    current_user: User = Depends(get_current_user)
):
    """Process video content for optimization."""
    try:
        result = await content_service.process_video(
            video_path,
            target_platform=target_platform,
            metadata=metadata
        )
        return result
    except ServiceError as e:
        logger.error("Video processing failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Platform routes
@router.post("/platforms/{platform}/optimize", tags=["platforms"])
async def optimize_for_platform(
    platform: str,
    content_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user)
):
    """Optimize content for specific platform."""
    try:
        result = await platform_service.optimize_for_platform(
            content_data,
            platform=platform
        )
        return result
    except ServiceError as e:
        logger.error("Platform optimization failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/platforms", tags=["platforms"])
async def get_platforms(current_user: User = Depends(get_current_user)):
    """Get all supported platforms and their requirements."""
    try:
        result = platform_service.get_platform_requirements()
        return result
    except ServiceError as e:
        logger.error("Failed to get platforms", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/platforms/{platform}", tags=["platforms"])
async def get_platform_requirements(
    platform: str,
    current_user: User = Depends(get_current_user)
):
    """Get platform-specific requirements."""
    try:
        result = platform_service.get_platform_requirements(platform=platform)
        return result
    except ServiceError as e:
        logger.error("Failed to get platform requirements", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Task routes
@router.post("/tasks", tags=["tasks"])
async def submit_task(
    task_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user)
):
    """Submit a task for background processing."""
    try:
        # Add task metadata
        if "id" not in task_data:
            import uuid
            task_data["id"] = str(uuid.uuid4())
        
        task_data["submitted_by"] = current_user.username
        task_data["submitted_at"] = datetime.utcnow().isoformat()
        
        # Submit task
        # In a real implementation, this would be added to a queue
        # For now, process directly
        result = await worker_manager.process_task(task_data)
        
        return {
            "task_id": task_data["id"],
            "status": "submitted" if result["status"] == "completed" else "failed",
            "result": result
        }
    except Exception as e:
        logger.error("Task submission failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task submission failed: {str(e)}"
        )
