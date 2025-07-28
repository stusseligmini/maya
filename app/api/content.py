"""
Content management API routes
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
import structlog

from database.connection import get_db
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.models.content import Content, ContentType, ContentStatus

logger = structlog.get_logger()
router = APIRouter(prefix="/content", tags=["content"])


class ContentCreate(BaseModel):
    """Content creation schema"""
    title: str
    description: Optional[str] = None
    content_type: ContentType
    target_platforms: Optional[List[str]] = None


class ContentResponse(BaseModel):
    """Content response schema"""
    id: int
    title: str
    description: Optional[str]
    content_type: str
    status: str
    original_text: Optional[str]
    optimized_text: Optional[str]
    media_urls: Optional[List[str]]
    hashtags: Optional[List[str]]
    mentions: Optional[List[str]]
    target_platforms: Optional[List[str]]
    analysis_data: Optional[Dict[str, Any]]
    recommendations: Optional[List[str]]
    user_id: int
    created_at: Optional[str]
    updated_at: Optional[str]
    published_at: Optional[str]
    
    class Config:
        from_attributes = True


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_content(
    content_data: ContentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new content"""
    content = Content(
        title=content_data.title,
        description=content_data.description,
        content_type=content_data.content_type,
        target_platforms=content_data.target_platforms,
        user_id=current_user.id
    )
    
    db.add(content)
    db.commit()
    db.refresh(content)
    
    logger.info("Content created", content_id=content.id, user_id=current_user.id)
    # Convert to dict to handle datetime serialization
    content_dict = content.to_dict()
    return content_dict


@router.get("/")
async def list_content(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List user's content"""
    content = db.query(Content).filter(
        Content.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return [item.to_dict() for item in content]


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific content by ID"""
    content = db.query(Content).filter(
        Content.id == content_id,
        Content.owner_id == current_user.id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    return ContentResponse.model_validate(content)


@router.post("/{content_id}/upload")
async def upload_content_file(
    content_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload file for content"""
    # Verify content ownership
    content = db.query(Content).filter(
        Content.id == content_id,
        Content.owner_id == current_user.id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Validate file type and size (basic validation)
    if file.size > 100 * 1024 * 1024:  # 100MB limit
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large"
        )
    
    # In a real implementation, you would:
    # 1. Save the file to storage (S3, local filesystem, etc.)
    # 2. Update the content record with file path
    # 3. Potentially trigger AI processing
    
    logger.info("File upload initiated", content_id=content_id, filename=file.filename)
    
    return {
        "message": "File upload initiated",
        "content_id": content_id,
        "filename": file.filename,
        "size": file.size
    }