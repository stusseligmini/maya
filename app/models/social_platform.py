"""
Social platform models for managing platform credentials and configurations
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base
import enum


class PlatformType(str, enum.Enum):
    """Social media platform enumeration"""
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    YOUTUBE = "youtube"
    PINTEREST = "pinterest"


class SocialPlatform(Base):
    """Social media platform configuration"""
    
    __tablename__ = "social_platforms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum(PlatformType), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Platform capabilities
    supports_images = Column(Boolean, default=True)
    supports_videos = Column(Boolean, default=True)
    supports_carousel = Column(Boolean, default=False)
    supports_stories = Column(Boolean, default=False)
    supports_scheduling = Column(Boolean, default=False)
    
    # API configuration
    api_base_url = Column(String(512), nullable=True)
    api_version = Column(String(50), nullable=True)
    requires_approval = Column(Boolean, default=False)
    
    # Content limitations
    max_image_size = Column(Integer, nullable=True)  # in bytes
    max_video_size = Column(Integer, nullable=True)  # in bytes
    max_video_duration = Column(Integer, nullable=True)  # in seconds
    max_caption_length = Column(Integer, nullable=True)  # in characters
    supported_formats = Column(JSON, nullable=True)  # List of supported file formats
    
    # Platform status
    is_active = Column(Boolean, default=True)
    is_beta = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    credentials = relationship("PlatformCredentials", back_populates="platform")
    
    def __repr__(self):
        return f"<SocialPlatform(id={self.id}, name='{self.name}')>"


class PlatformCredentials(Base):
    """User's social media platform credentials"""
    
    __tablename__ = "platform_credentials"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # OAuth tokens (encrypted)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional credentials
    app_id = Column(String(255), nullable=True)
    app_secret = Column(String(255), nullable=True)  # encrypted
    
    # Account information
    platform_user_id = Column(String(255), nullable=True)
    platform_username = Column(String(255), nullable=True)
    account_name = Column(String(255), nullable=True)
    
    # Status and permissions
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    permissions = Column(JSON, nullable=True)  # List of granted permissions
    
    # Usage tracking
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    total_posts = Column(Integer, default=0)
    monthly_posts = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform_id = Column(Integer, ForeignKey("social_platforms.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="platform_credentials")
    platform = relationship("SocialPlatform", back_populates="credentials")
    
    def __repr__(self):
        return f"<PlatformCredentials(id={self.id}, user_id={self.user_id}, platform_id={self.platform_id})>"