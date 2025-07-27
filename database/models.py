"""
Comprehensive database models for Maya AI Content Optimization System
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
import uuid

Base = declarative_base()

class ContentType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"
    MIXED = "mixed"

class ContentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"
    FAILED = "failed"

class Platform(str, Enum):
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FANVUE = "fanvue"
    SNAPCHAT = "snapchat"

class ModerationResult(str, Enum):
    SAFE = "safe"
    NSFW = "nsfw"
    QUESTIONABLE = "questionable"
    BLOCKED = "blocked"

# Core Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    content_items = relationship("ContentItem", back_populates="creator")
    api_keys = relationship("APIKey", back_populates="user")

class ContentItem(Base):
    __tablename__ = "content_items"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    content_type = Column(SQLEnum(ContentType), nullable=False)
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.PENDING)
    file_path = Column(String(500))
    thumbnail_path = Column(String(500))
    caption = Column(Text)
    target_keywords = Column(Text)
    meta_description = Column(String(500))
    target_platforms = Column(JSON)  # List of platforms
    creator_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime)
    published_at = Column(DateTime)
    
    # Relationships
    creator = relationship("User", back_populates="content_items")
    moderation_results = relationship("ModerationResult", back_populates="content_item")
    ai_analysis = relationship("AIAnalysis", back_populates="content_item", uselist=False)
    publishing_records = relationship("PublishingRecord", back_populates="content_item")

class ModerationResult(Base):
    __tablename__ = "moderation_results"
    
    id = Column(Integer, primary_key=True, index=True)
    content_item_id = Column(Integer, ForeignKey("content_items.id"))
    result = Column(SQLEnum(ModerationResult), nullable=False)
    nsfw_score = Column(Float, default=0.0)
    emotion_scores = Column(JSON)  # Dict of emotion: score
    flagged_content = Column(JSON)  # List of flagged items
    moderator_notes = Column(Text)
    auto_moderated = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    content_item = relationship("ContentItem", back_populates="moderation_results")

class AIAnalysis(Base):
    __tablename__ = "ai_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    content_item_id = Column(Integer, ForeignKey("content_items.id"))
    generated_caption = Column(Text)
    seo_keywords = Column(JSON)  # List of keywords
    sentiment_score = Column(Float)
    engagement_prediction = Column(Float)
    platform_recommendations = Column(JSON)  # Platform-specific recommendations
    optimization_suggestions = Column(JSON)
    model_version = Column(String(50))
    processing_time = Column(Float)  # seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    content_item = relationship("ContentItem", back_populates="ai_analysis")

class PublishingRecord(Base):
    __tablename__ = "publishing_records"
    
    id = Column(Integer, primary_key=True, index=True)
    content_item_id = Column(Integer, ForeignKey("content_items.id"))
    platform = Column(SQLEnum(Platform), nullable=False)
    platform_post_id = Column(String(255))
    post_url = Column(String(500))
    status = Column(String(50))  # success, failed, pending
    scheduled_for = Column(DateTime)
    published_at = Column(DateTime)
    error_message = Column(Text)
    engagement_metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    content_item = relationship("ContentItem", back_populates="publishing_records")

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    key_name = Column(String(100), nullable=False)
    key_value = Column(String(255), nullable=False)
    platform = Column(String(50))
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")

class ProcessingQueue(Base):
    __tablename__ = "processing_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    content_item_id = Column(Integer, ForeignKey("content_items.id"))
    task_type = Column(String(50), nullable=False)  # moderation, ai_analysis, publishing
    priority = Column(Integer, default=5)
    status = Column(String(50), default="pending")
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemMetrics(Base):
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_type = Column(String(50))  # counter, gauge, histogram
    tags = Column(JSON)  # Additional metadata
    timestamp = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String(50))
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow)

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    content_item_id = Column(Integer, ForeignKey("content_items.id"))
    feedback_type = Column(String(50))  # user_rating, engagement_data, error_report
    rating = Column(Integer)  # 1-5 scale
    comment = Column(Text)
    engagement_data = Column(JSON)
    source = Column(String(50))  # user, system, external_api
    created_at = Column(DateTime, default=datetime.utcnow)
