"""
AI processing API routes
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import structlog

from database.connection import get_db
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.models.ai_model import AIModel, AIProcessingJob, JobStatus

logger = structlog.get_logger()
router = APIRouter(prefix="/ai", tags=["ai-processing"])


class AIModelResponse(BaseModel):
    """AI Model response schema"""
    id: int
    name: str
    display_name: str
    description: Optional[str]
    provider: str
    supports_images: bool
    supports_videos: bool
    supports_text: bool
    is_active: bool
    is_premium: bool
    
    class Config:
        from_attributes = True


class ProcessingJobCreate(BaseModel):
    """Processing job creation schema"""
    content_id: int
    model_id: int
    job_type: str
    input_params: Optional[dict] = None


class ProcessingJobResponse(BaseModel):
    """Processing job response schema"""
    id: int
    content_id: int
    model_id: int
    job_type: str
    status: JobStatus
    progress_percentage: int
    error_message: Optional[str]
    processing_time_seconds: Optional[float]
    quality_score: Optional[int]
    created_at: str
    
    class Config:
        from_attributes = True


@router.get("/models", response_model=List[AIModelResponse])
async def list_ai_models(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List available AI models"""
    models = db.query(AIModel).filter(AIModel.is_active == True).all()
    return [AIModelResponse.model_validate(model) for model in models]


@router.post("/process", response_model=ProcessingJobResponse, status_code=status.HTTP_201_CREATED)
async def create_processing_job(
    job_data: ProcessingJobCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new AI processing job"""
    # Verify content ownership
    from app.models.content import Content
    content = db.query(Content).filter(
        Content.id == job_data.content_id,
        Content.owner_id == current_user.id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Verify AI model exists
    model = db.query(AIModel).filter(AIModel.id == job_data.model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI model not found"
        )
    
    # Create processing job
    job = AIProcessingJob(
        content_id=job_data.content_id,
        model_id=job_data.model_id,
        job_type=job_data.job_type,
        input_params=job_data.input_params,
        status=JobStatus.PENDING
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    logger.info("AI processing job created", job_id=job.id, content_id=job_data.content_id)
    
    # In a real implementation, you would trigger the actual AI processing here
    # This could involve sending the job to a queue (Celery) or calling an external API
    
    return ProcessingJobResponse.from_orm(job)


@router.get("/jobs", response_model=List[ProcessingJobResponse])
async def list_processing_jobs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List user's AI processing jobs"""
    from app.models.content import Content
    
    jobs = db.query(AIProcessingJob).join(Content).filter(
        Content.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return [ProcessingJobResponse.model_validate(job) for job in jobs]


@router.get("/jobs/{job_id}", response_model=ProcessingJobResponse)
async def get_processing_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific processing job status"""
    from app.models.content import Content
    
    job = db.query(AIProcessingJob).join(Content).filter(
        AIProcessingJob.id == job_id,
        Content.owner_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processing job not found"
        )
    
    return ProcessingJobResponse.from_orm(job)