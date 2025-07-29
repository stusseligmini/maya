"""
Unified Configuration System for Maya AI

This module provides a centralized configuration system, supporting different environments
and secure secret management.
"""
import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
env_path = Path('.env')
if env_path.exists():
    load_dotenv(dotenv_path=str(env_path))

class AppSettings(BaseSettings):
    """
    Application settings with environment variable support
    """
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    
    # Application basics
    APP_NAME: str = "Maya AI Content Optimization"
    VERSION: str = "1.0.0"
    
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
    SECRET_KEY: str = Field(
        default="insecure-secret-key-change-me-in-production",
        description="Secret key for tokens and cryptographic signing"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External API Integrations
    OPENAI_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    RUNWAY_API_KEY: Optional[str] = None
    
    # Social Media API Credentials
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = None
    TIKTOK_ACCESS_TOKEN: Optional[str] = None
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    TWITTER_ACCESS_TOKEN: Optional[str] = None
    TWITTER_ACCESS_TOKEN_SECRET: Optional[str] = None
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    
    # Storage configuration
    STORAGE_PATH: str = "./storage"
    TEMP_PATH: str = "./temp"
    
    # Worker configuration
    WORKER_CONCURRENCY: int = 4
    WORKER_LOGLEVEL: str = "info"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # n8n Integration
    N8N_WEBHOOK_URL: Optional[str] = None
    N8N_AUTH_TOKEN: Optional[str] = None
    
    # Monitoring
    PROMETHEUS_METRICS: bool = False
    SENTRY_DSN: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        allowed = ["development", "testing", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT == "testing"


class DevelopmentSettings(AppSettings):
    """Development environment specific settings"""
    DEBUG: bool = True
    DATABASE_ECHO: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    # Override with development-specific values
    class Config:
        env_prefix = "DEV_"


class ProductionSettings(AppSettings):
    """Production environment specific settings"""
    DEBUG: bool = False
    ALLOWED_HOSTS: List[str] = ["api.mayaai.com"]
    
    # Production requires proper configuration
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if v == "insecure-secret-key-change-me-in-production":
            raise ValueError("You must set a secure SECRET_KEY in production")
        return v
    
    @validator("OPENAI_API_KEY", "DATABASE_URL")
    def validate_required_fields(cls, v, values, **kwargs):
        if not v:
            raise ValueError(f"{kwargs['field'].name} is required in production")
        return v

    class Config:
        env_prefix = "PROD_"


class TestingSettings(AppSettings):
    """Testing environment specific settings"""
    TESTING: bool = True
    DATABASE_URL: str = "sqlite:///./test.db"
    
    class Config:
        env_prefix = "TEST_"


@lru_cache()
def get_settings() -> AppSettings:
    """
    Get the appropriate settings based on the current environment.
    Uses environment caching for performance.
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# Export the settings instance for easy import
settings = get_settings()
