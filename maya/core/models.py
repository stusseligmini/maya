"""
Core Models for Maya AI Content Optimization System

This file contains all database models used throughout the system.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
import uuid
from typing import Optional, List, Dict, Any

# Base declarative model
Base = declarative_base()

# ===========================
# ENUM DEFINITIONS
# ===========================

class ContentType(str, Enum):
    """Type of content being processed"""
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"
    MIXED = "mixed"
    BLOG_POST = "blog_post"
    ARTICLE = "article"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    LANDING_PAGE = "landing_page"
    PRODUCT_DESCRIPTION = "product_description"

class ContentStatus(str, Enum):
    """Status of content in the processing pipeline"""
    DRAFT = "draft"
    PENDING = "pending"
    PROCESSING = "processing"
    OPTIMIZED = "optimized"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"

class Platform(str, Enum):
    """Social media platforms for publishing"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    YOUTUBE = "youtube"

class ModerationResult(str, Enum):
    """Result of content moderation checks"""
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"

class AIModelType(str, Enum):
    """Types of AI models used in the system"""
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    STABLE_DIFFUSION = "stable_diffusion"
    FOOOCUS = "fooocus"
    CUSTOM = "custom"

# ===========================
# USER MODELS
# ===========================

class User(Base):
    """User model for authentication and permissions"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    api_key = Column(String, nullable=True, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    contents = relationship("Content", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"

class APIKey(Base):
    """API key for programmatic access"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")

# ===========================
# CONTENT MODELS
# ===========================

class Content(Base):
    """Main content model for all types of content"""
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, default=lambda: str(uuid.uuid4()), unique=True)
    title = Column(String(255), nullable=False)
    content_type = Column(SQLEnum(ContentType), nullable=False)
    original_content = Column(Text, nullable=False)
    optimized_content = Column(Text, nullable=True)
    target_keywords = Column(Text, nullable=True)  # JSON string of keywords
    meta_description = Column(String(255), nullable=True)
    caption = Column(Text, nullable=True)
    hashtags = Column(Text, nullable=True)
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.DRAFT)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metrics
    seo_score = Column(Integer, nullable=True)
    readability_score = Column(Integer, nullable=True)
    engagement_prediction = Column(Float, nullable=True)
    
    # File paths for media content
    file_path = Column(String, nullable=True)
    thumbnail_path = Column(String, nullable=True)
    
    # Platform targeting
    target_platforms = Column(Text, nullable=True)  # JSON list of platforms
    
    # Relationships
    user = relationship("User", back_populates="contents")
    moderation_results = relationship("ModerationResult", back_populates="content")
    ai_analyses = relationship("AIAnalysis", back_populates="content")
    publishing_records = relationship("PublishingRecord", back_populates="content")
    
    def __repr__(self):
        return f"<Content {self.id}: {self.title[:30]}...>"

class ModerationResultModel(Base):
    """Content moderation results"""
    __tablename__ = "moderation_results"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.id"))
    result = Column(SQLEnum(ModerationResult))
    reason = Column(Text, nullable=True)
    nsfw_score = Column(Float, nullable=True)
    violence_score = Column(Float, nullable=True)
    hate_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    content = relationship("Content", back_populates="moderation_results")

class AIAnalysis(Base):
    """AI analysis of content"""
    __tablename__ = "ai_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.id"))
    model_type = Column(SQLEnum(AIModelType))
    model_name = Column(String)
    analysis_data = Column(JSON)  # Stores sentiment, keywords, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    content = relationship("Content", back_populates="ai_analyses")

class PublishingRecord(Base):
    """Record of content publication to platforms"""
    __tablename__ = "publishing_records"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.id"))
    platform = Column(SQLEnum(Platform))
    status = Column(String)  # success, failed, pending
    external_url = Column(String, nullable=True)  # URL on the platform
    response_data = Column(JSON, nullable=True)  # Platform API response
    scheduled_time = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    
    # Metrics
    likes = Column(Integer, nullable=True)
    shares = Column(Integer, nullable=True)
    comments = Column(Integer, nullable=True)
    reach = Column(Integer, nullable=True)
    
    # Relationship
    content = relationship("Content", back_populates="publishing_records")

class ProcessingQueue(Base):
    """Background processing queue"""
    __tablename__ = "processing_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.id"))
    task_type = Column(String)  # generation, optimization, moderation, etc.
    status = Column(String)  # pending, processing, completed, failed
    priority = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Worker info
    worker_id = Column(String, nullable=True)
    celery_task_id = Column(String, nullable=True)
    
    # Relationships
    content = relationship("Content")
