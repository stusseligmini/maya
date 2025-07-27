"""Configuration management for Maya system."""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional, List
import os


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    url: str = Field(default="postgresql://maya:maya@localhost:5432/maya", env="DATABASE_URL")
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    
    class Config:
        env_prefix = "DB_"


class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    
    url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    max_connections: int = Field(default=10, env="REDIS_MAX_CONNECTIONS")
    
    class Config:
        env_prefix = "REDIS_"


class AISettings(BaseSettings):
    """AI model configuration settings."""
    
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    huggingface_token: Optional[str] = Field(default=None, env="HUGGINGFACE_TOKEN")
    model_cache_dir: str = Field(default="./models/cache", env="MODEL_CACHE_DIR")
    
    class Config:
        env_prefix = "AI_"


class SecuritySettings(BaseSettings):
    """Security configuration settings."""
    
    secret_key: str = Field(default="dev-secret-key-change-in-production-at-least-32-chars", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    allowed_hosts: List[str] = Field(default=["*"], env="ALLOWED_HOSTS")
    
    class Config:
        env_prefix = "SECURITY_"
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('Secret key must be at least 32 characters long')
        return v


class SocialPlatformSettings(BaseSettings):
    """Social platform API configuration."""
    
    twitter_api_key: Optional[str] = Field(default=None, env="TWITTER_API_KEY")
    twitter_api_secret: Optional[str] = Field(default=None, env="TWITTER_API_SECRET")
    instagram_access_token: Optional[str] = Field(default=None, env="INSTAGRAM_ACCESS_TOKEN")
    
    class Config:
        env_prefix = "SOCIAL_"


class MonitoringSettings(BaseSettings):
    """Monitoring and observability settings."""
    
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    prometheus_port: int = Field(default=8090, env="PROMETHEUS_PORT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    json_logs: bool = Field(default=True, env="JSON_LOGS")
    
    class Config:
        env_prefix = "MONITORING_"


class Settings(BaseSettings):
    """Main application settings."""
    
    # Application
    app_name: str = Field(default="Maya AI Content System", env="APP_NAME")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # API
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    
    # Sub-configurations
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    ai: AISettings = AISettings()
    security: SecuritySettings = SecuritySettings()
    social: SocialPlatformSettings = SocialPlatformSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Get application settings singleton."""
    return Settings()