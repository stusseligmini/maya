"""
AI model and processing job models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base
import enum


class JobStatus(str, enum.Enum):
    """AI processing job status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AIModel(Base):
    """AI model configuration and metadata"""
    
    __tablename__ = "ai_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # e.g., "gpt-4-vision"
    display_name = Column(String(255), nullable=False)  # Human-readable name
    description = Column(Text, nullable=True)
    provider = Column(String(100), nullable=False)  # e.g., "openai", "huggingface"
    
    # Capabilities
    supports_images = Column(Boolean, default=False)
    supports_videos = Column(Boolean, default=False)
    supports_text = Column(Boolean, default=True)
    supports_audio = Column(Boolean, default=False)
    
    # Model configuration
    max_input_size = Column(Integer, nullable=True)  # Max input size in tokens/pixels
    max_output_size = Column(Integer, nullable=True)  # Max output size
    cost_per_request = Column(Float, nullable=True)  # Cost in credits/USD
    avg_processing_time = Column(Float, nullable=True)  # Average time in seconds
    
    # Status and availability
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    
    # Configuration
    api_endpoint = Column(String(512), nullable=True)
    model_version = Column(String(100), nullable=True)
    parameters = Column(JSON, nullable=True)  # Model-specific parameters
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    processing_jobs = relationship("AIProcessingJob", back_populates="model")
    
    def __repr__(self):
        return f"<AIModel(id={self.id}, name='{self.name}', provider='{self.provider}')>"


class AIProcessingJob(Base):
    """AI processing job tracking"""
    
    __tablename__ = "ai_processing_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String(100), nullable=False)  # e.g., "enhancement", "caption_generation"
    
    # Job configuration
    input_params = Column(JSON, nullable=True)  # Job-specific input parameters
    output_data = Column(JSON, nullable=True)  # Job results
    
    # Status and progress
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    progress_percentage = Column(Integer, default=0)  # 0-100
    
    # Results and metadata
    quality_score = Column(Integer, nullable=True)  # 0-100
    confidence_score = Column(Float, nullable=True)  # 0.0-1.0
    error_message = Column(Text, nullable=True)
    
    # Performance metrics
    processing_time_seconds = Column(Float, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    cost_credits = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    model_id = Column(Integer, ForeignKey("ai_models.id"), nullable=False)
    
    # Relationships
    content = relationship("Content", back_populates="ai_jobs")
    model = relationship("AIModel", back_populates="processing_jobs")
    
    class Config:
        protected_namespaces = ()
    
    def __repr__(self):
        return f"<AIProcessingJob(id={self.id}, type='{self.job_type}', status='{self.status}')>"