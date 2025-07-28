"""
Configuration management for Maya AI Content Optimization system
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application settings
    APP_NAME: str = "Maya AI Content Optimization"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./maya.db"
    DATABASE_ECHO: bool = False
    
    # Redis settings (for caching and task queue)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI Model settings
    OPENAI_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    RUNWAY_API_KEY: Optional[str] = None
    
    # Social Media API settings
    INSTAGRAM_CLIENT_ID: Optional[str] = None
    INSTAGRAM_CLIENT_SECRET: Optional[str] = None
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    TWITTER_BEARER_TOKEN: Optional[str] = None
    TWITTER_ACCESS_TOKEN: Optional[str] = None
    TWITTER_ACCESS_TOKEN_SECRET: Optional[str] = None
    TIKTOK_CLIENT_ID: Optional[str] = None
    TIKTOK_CLIENT_SECRET: Optional[str] = None
    
    # Content processing settings
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_MEDIA_TYPES: List[str] = ["image/jpeg", "image/png", "video/mp4", "video/mov"]
    
    # Monitoring and logging
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: Optional[str] = None
    
    # Feature flags
    ENABLE_AI_ENHANCEMENT: bool = True
    ENABLE_CONTENT_MODERATION: bool = True
    ENABLE_ANALYTICS: bool = True
    
    # Rate limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


class DevelopmentSettings(Settings):
    """Development environment settings"""
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./maya.db"
    DATABASE_ECHO: bool = True
    LOG_LEVEL: str = "DEBUG"


class ProductionSettings(Settings):
    """Production environment settings"""
    DEBUG: bool = False
    DATABASE_ECHO: bool = False
    LOG_LEVEL: str = "WARNING"
    ALLOWED_HOSTS: List[str] = ["your-domain.com"]


class TestSettings(Settings):
    """Test environment settings"""
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///test.db"
    DATABASE_ECHO: bool = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get settings instance based on environment
    Cached to avoid recreating settings object
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "test":
        return TestSettings()
    else:
        return DevelopmentSettings()


# Export commonly used settings
settings = get_settings()