"""
Publishing API endpoints for social media content publishing and scheduling
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
import structlog
import uuid

from database.connection import get_db
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.models.content import Content, ContentStatus
from app.models.social_platform import SocialPlatform, PlatformCredentials, PlatformType
from config.settings import get_settings

logger = structlog.get_logger()
router = APIRouter(prefix="/publishing", tags=["publishing"])
settings = get_settings()


class PublishRequest(BaseModel):
    """Content publishing request schema"""
    content_id: int
    platforms: List[str] = Field(..., description="List of platform names to publish to")
    captions: Optional[Dict[str, str]] = Field(None, description="Platform-specific captions")
    tags: Optional[List[str]] = Field(None, description="Hashtags and keywords")
    scheduled_time: Optional[datetime] = Field(None, description="Schedule for later publishing")
    
    @validator('platforms')
    def validate_platforms(cls, v):
        valid_platforms = [platform.value for platform in PlatformType]
        for platform in v:
            if platform not in valid_platforms:
                raise ValueError(f"Invalid platform: {platform}")
        return v


class BatchPublishRequest(BaseModel):
    """Batch publishing request for multiple content items"""
    content_ids: List[int] = Field(..., description="List of content IDs to publish")
    platforms: List[str] = Field(..., description="List of platform names to publish to")
    scheduled_time: Optional[datetime] = Field(None, description="Schedule for later publishing")
    stagger_minutes: Optional[int] = Field(None, description="Minutes between each publish")


class PublishResponse(BaseModel):
    """Publishing response schema"""
    publish_id: str
    content_id: int
    platforms: List[str]
    status: str  # "scheduled", "publishing", "completed", "failed"
    scheduled_time: Optional[datetime]
    created_at: datetime
    estimated_completion: Optional[datetime]
    
    class Config:
        from_attributes = True


class PublishStatusResponse(BaseModel):
    """Publishing status response schema"""
    publish_id: str
    content_id: int
    overall_status: str
    platform_statuses: Dict[str, Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    completion_percentage: int
    
    class Config:
        from_attributes = True


# In-memory store for publish jobs (in production, use Redis or database)
publish_jobs = {}


async def publish_to_platform(content_id: int, platform: str, caption: str, user_id: int, db: Session):
    """
    Async function to publish content to a specific platform
    In production, this would integrate with actual platform APIs
    """
    try:
        # Simulate API call delay
        import asyncio
        await asyncio.sleep(2)
        
        # Check platform credentials
        user = db.query(User).filter(User.id == user_id).first()
        platform_obj = db.query(SocialPlatform).filter(SocialPlatform.name == platform).first()
        
        if not platform_obj:
            return {"status": "failed", "error": f"Platform {platform} not found"}
        
        credentials = db.query(PlatformCredentials).filter(
            PlatformCredentials.user_id == user_id,
            PlatformCredentials.platform_id == platform_obj.id,
            PlatformCredentials.is_active == True
        ).first()
        
        if not credentials:
            return {"status": "failed", "error": f"No active credentials for {platform}"}
        
        # Simulate successful publishing
        platform_post_id = f"{platform}_{uuid.uuid4().hex[:8]}"
        published_url = f"https://{platform}.com/post/{platform_post_id}"
        
        return {
            "status": "success",
            "platform_post_id": platform_post_id,
            "published_url": published_url,
            "published_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Publishing to {platform} failed", exc_info=e)
        return {"status": "failed", "error": str(e)}


@router.post("/immediate", response_model=PublishResponse)
async def publish_immediately(
    request: PublishRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Publish content immediately to specified platforms
    """
    # Verify content ownership
    content = db.query(Content).filter(
        Content.id == request.content_id,
        Content.owner_id == current_user.id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    if content.status != ContentStatus.READY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content is not ready for publishing"
        )
    
    # Create publish job
    publish_id = str(uuid.uuid4())
    job_data = {
        "publish_id": publish_id,
        "content_id": request.content_id,
        "platforms": request.platforms,
        "status": "publishing",
        "scheduled_time": None,
        "created_at": datetime.utcnow(),
        "estimated_completion": datetime.utcnow() + timedelta(minutes=5),
        "platform_statuses": {platform: {"status": "pending"} for platform in request.platforms},
        "user_id": current_user.id
    }
    
    publish_jobs[publish_id] = job_data
    
    # Start publishing process in background
    for platform in request.platforms:
        caption = request.captions.get(platform, content.description) if request.captions else content.description
        background_tasks.add_task(
            publish_to_platform_background,
            publish_id,
            content.id,
            platform,
            caption,
            current_user.id,
            db
        )
    
    # Update content status
    content.status = ContentStatus.PROCESSING
    db.commit()
    
    logger.info(
        "Immediate publishing started",
        publish_id=publish_id,
        content_id=request.content_id,
        platforms=request.platforms,
        user_id=current_user.id
    )
    
    return PublishResponse(**job_data)


@router.post("/schedule", response_model=PublishResponse)
async def schedule_publishing(
    request: PublishRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Schedule content publishing for a future time
    """
    if not request.scheduled_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scheduled time is required for scheduling"
        )
    
    if request.scheduled_time <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scheduled time must be in the future"
        )
    
    # Verify content ownership
    content = db.query(Content).filter(
        Content.id == request.content_id,
        Content.owner_id == current_user.id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    if content.status != ContentStatus.READY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content is not ready for publishing"
        )
    
    # Create scheduled publish job
    publish_id = str(uuid.uuid4())
    job_data = {
        "publish_id": publish_id,
        "content_id": request.content_id,
        "platforms": request.platforms,
        "status": "scheduled",
        "scheduled_time": request.scheduled_time,
        "created_at": datetime.utcnow(),
        "estimated_completion": request.scheduled_time + timedelta(minutes=5),
        "platform_statuses": {platform: {"status": "scheduled"} for platform in request.platforms},
        "user_id": current_user.id,
        "captions": request.captions,
        "tags": request.tags
    }
    
    publish_jobs[publish_id] = job_data
    
    logger.info(
        "Publishing scheduled",
        publish_id=publish_id,
        content_id=request.content_id,
        platforms=request.platforms,
        scheduled_time=request.scheduled_time,
        user_id=current_user.id
    )
    
    return PublishResponse(**job_data)


@router.post("/batch", response_model=List[PublishResponse])
async def batch_publish(
    request: BatchPublishRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Batch publish multiple content items
    Optimized for N8n bulk operations
    """
    # Verify all content ownership
    content_items = db.query(Content).filter(
        Content.id.in_(request.content_ids),
        Content.owner_id == current_user.id,
        Content.status == ContentStatus.READY
    ).all()
    
    if len(content_items) != len(request.content_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more content items not found or not ready for publishing"
        )
    
    publish_responses = []
    current_time = request.scheduled_time or datetime.utcnow()
    
    for i, content in enumerate(content_items):
        # Calculate staggered time if specified
        publish_time = current_time
        if request.stagger_minutes and i > 0:
            publish_time = current_time + timedelta(minutes=request.stagger_minutes * i)
        
        publish_id = str(uuid.uuid4())
        job_data = {
            "publish_id": publish_id,
            "content_id": content.id,
            "platforms": request.platforms,
            "status": "scheduled" if request.scheduled_time else "publishing",
            "scheduled_time": publish_time if request.scheduled_time else None,
            "created_at": datetime.utcnow(),
            "estimated_completion": publish_time + timedelta(minutes=5),
            "platform_statuses": {platform: {"status": "pending"} for platform in request.platforms},
            "user_id": current_user.id
        }
        
        publish_jobs[publish_id] = job_data
        publish_responses.append(PublishResponse(**job_data))
        
        # Start immediate publishing if not scheduled
        if not request.scheduled_time:
            for platform in request.platforms:
                background_tasks.add_task(
                    publish_to_platform_background,
                    publish_id,
                    content.id,
                    platform,
                    content.description,
                    current_user.id,
                    db
                )
    
    logger.info(
        "Batch publishing initiated",
        content_count=len(request.content_ids),
        platforms=request.platforms,
        scheduled=bool(request.scheduled_time),
        user_id=current_user.id
    )
    
    return publish_responses


@router.get("/status/{publish_id}", response_model=PublishStatusResponse)
async def get_publish_status(
    publish_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get publishing status for a specific publish job
    """
    job = publish_jobs.get(publish_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publish job not found"
        )
    
    if job["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Calculate completion percentage
    total_platforms = len(job["platforms"])
    completed_platforms = sum(
        1 for status in job["platform_statuses"].values()
        if status["status"] in ["success", "failed"]
    )
    completion_percentage = int((completed_platforms / total_platforms) * 100) if total_platforms > 0 else 0
    
    return PublishStatusResponse(
        publish_id=publish_id,
        content_id=job["content_id"],
        overall_status=job["status"],
        platform_statuses=job["platform_statuses"],
        created_at=job["created_at"],
        updated_at=job.get("updated_at", job["created_at"]),
        completion_percentage=completion_percentage
    )


@router.delete("/cancel/{publish_id}")
async def cancel_publishing(
    publish_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Cancel a scheduled publishing job
    """
    job = publish_jobs.get(publish_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publish job not found"
        )
    
    if job["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if job["status"] not in ["scheduled", "pending"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel job that is already in progress or completed"
        )
    
    # Update job status
    job["status"] = "cancelled"
    job["updated_at"] = datetime.utcnow()
    
    logger.info(
        "Publishing job cancelled",
        publish_id=publish_id,
        content_id=job["content_id"],
        user_id=current_user.id
    )
    
    return {
        "status": "cancelled",
        "publish_id": publish_id,
        "message": "Publishing job cancelled successfully"
    }


@router.get("/history")
async def get_publish_history(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get publishing history for the current user
    """
    # Filter jobs for current user
    user_jobs = [
        job for job in publish_jobs.values()
        if job["user_id"] == current_user.id
    ]
    
    # Sort by creation time (newest first)
    user_jobs.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Apply pagination
    paginated_jobs = user_jobs[skip:skip + limit]
    
    return {
        "total": len(user_jobs),
        "jobs": paginated_jobs,
        "skip": skip,
        "limit": limit
    }


async def publish_to_platform_background(
    publish_id: str,
    content_id: int,
    platform: str,
    caption: str,
    user_id: int,
    db: Session
):
    """
    Background task to publish content to a platform and update job status
    """
    try:
        # Update platform status to "publishing"
        if publish_id in publish_jobs:
            publish_jobs[publish_id]["platform_statuses"][platform] = {"status": "publishing"}
        
        # Perform the actual publishing
        result = await publish_to_platform(content_id, platform, caption, user_id, db)
        
        # Update job status
        if publish_id in publish_jobs:
            publish_jobs[publish_id]["platform_statuses"][platform] = result
            publish_jobs[publish_id]["updated_at"] = datetime.utcnow()
            
            # Check if all platforms are done
            all_statuses = [
                status["status"] for status in publish_jobs[publish_id]["platform_statuses"].values()
            ]
            if all(status in ["success", "failed"] for status in all_statuses):
                if any(status == "success" for status in all_statuses):
                    publish_jobs[publish_id]["status"] = "completed"
                else:
                    publish_jobs[publish_id]["status"] = "failed"
        
        logger.info(
            "Platform publishing completed",
            publish_id=publish_id,
            content_id=content_id,
            platform=platform,
            result_status=result["status"]
        )
        
    except Exception as e:
        logger.error(
            "Platform publishing failed",
            publish_id=publish_id,
            content_id=content_id,
            platform=platform,
            exc_info=e
        )
        
        if publish_id in publish_jobs:
            publish_jobs[publish_id]["platform_statuses"][platform] = {
                "status": "failed",
                "error": str(e)
            }