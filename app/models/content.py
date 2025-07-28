"""Content model for Maya AI Content Optimization"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum
import enum
from database.connection import Base


class ContentType(str, Enum):
    """Content type enumeration"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    MIXED = "mixed"


class ContentStatus(str, Enum):
    """Content status enumeration"""
    DRAFT = "draft"
    PROCESSING = "processing"
    OPTIMIZED = "optimized"
    PUBLISHED = "published"
    FAILED = "failed"


class Content(Base):
    """Content model"""
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content_type = Column(String(50), nullable=False)
    status = Column(String(50), default=ContentStatus.DRAFT)
    
    # Content data
    original_text = Column(Text, nullable=True)
    optimized_text = Column(Text, nullable=True)
    media_urls = Column(JSON, nullable=True)  # Array of media URLs
    hashtags = Column(JSON, nullable=True)  # Array of hashtags
    mentions = Column(JSON, nullable=True)  # Array of mentions
    
    # Optimization data
    target_platforms = Column(JSON, nullable=True)  # Array of target platforms
    analysis_data = Column(JSON, nullable=True)  # AI analysis results
    recommendations = Column(JSON, nullable=True)  # Optimization recommendations
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="content")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Content(id={self.id}, title='{self.title}', type='{self.content_type}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert content to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "content_type": self.content_type,
            "status": self.status,
            "original_text": self.original_text,
            "optimized_text": self.optimized_text,
            "media_urls": self.media_urls,
            "hashtags": self.hashtags,
            "mentions": self.mentions,
            "target_platforms": self.target_platforms,
            "analysis_data": self.analysis_data,
            "recommendations": self.recommendations,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
        }