"""AI model for Maya AI Content Optimization"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum
from database.connection import Base


class JobStatus(str, Enum):
    """AI processing job status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AIModel(Base):
    """AI model configuration"""
    __tablename__ = "ai_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    model_type = Column(String(100), nullable=False)  # openai, huggingface, etc.
    model_version = Column(String(100), nullable=True)
    
    # Configuration
    is_active = Column(Boolean, default=True)
    config = Column(JSON, nullable=True)  # Model-specific configuration
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<AIModel(id={self.id}, name='{self.name}', type='{self.model_type}')>"
    
    def to_dict(self):
        """Convert AI model to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "model_type": self.model_type,
            "model_version": self.model_version,
            "is_active": self.is_active,
            "config": self.config,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AIProcessingJob(Base):
    """AI processing job tracking"""
    __tablename__ = "ai_processing_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String(100), nullable=False)  # content_analysis, generation, etc.
    status = Column(String(50), default=JobStatus.PENDING)
    
    # Input/Output data
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=True)
    ai_model_id = Column(Integer, ForeignKey("ai_models.id"), nullable=True)
    
    user = relationship("User")
    content = relationship("Content")
    ai_model = relationship("AIModel")
    
    # Processing metadata
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    processing_time_seconds = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<AIProcessingJob(id={self.id}, type='{self.job_type}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert processing job to dictionary"""
        return {
            "id": self.id,
            "job_type": self.job_type,
            "status": self.status,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "user_id": self.user_id,
            "content_id": self.content_id,
            "ai_model_id": self.ai_model_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "processing_time_seconds": self.processing_time_seconds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }