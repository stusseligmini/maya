"""
Content model for managing user content and media
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base
import enum


class ContentType(str, enum.Enum):
    """Content type enumeration"""
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"


class ContentStatus(str, enum.Enum):
    """Content processing status enumeration"""
    DRAFT = "draft"
    PROCESSING = "processing"
    READY = "ready"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"


class Content(Base):
    """Content model for managing user content and media"""
    
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Content metadata
    content_type = Column(Enum(ContentType), nullable=False)
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT)
    
    # File information
    original_file_path = Column(String(512), nullable=True)
    processed_file_path = Column(String(512), nullable=True)
    thumbnail_path = Column(String(512), nullable=True)
    file_size = Column(Integer, nullable=True)  # in bytes
    mime_type = Column(String(100), nullable=True)
    
    # AI enhancement
    ai_enhanced = Column(Boolean, default=False)
    optimization_score = Column(Integer, nullable=True)  # 0-100
    ai_suggestions = Column(JSON, nullable=True)
    
    # Social media optimization
    tags = Column(JSON, nullable=True)  # List of hashtags and keywords
    target_platforms = Column(JSON, nullable=True)  # List of target platforms
    captions = Column(JSON, nullable=True)  # Platform-specific captions
    
    # Analytics
    view_count = Column(Integer, default=0)
    engagement_score = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="content")
    ai_jobs = relationship("AIProcessingJob", back_populates="content", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Content(id={self.id}, title='{self.title}', type='{self.content_type}', status='{self.status}')>"