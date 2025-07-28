"""Configuration management for Maya system."""

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    # Fallback for environments without pydantic-settings
    PYDANTIC_AVAILABLE = False
    
from typing import Optional, List
import os


if PYDANTIC_AVAILABLE:

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
        
        secret_key: str = Field(default="your-super-secret-key-change-in-production", env="SECRET_KEY")
        jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
        access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
        allowed_hosts: List[str] = Field(default=["*"], env="ALLOWED_HOSTS")
        
        @validator('secret_key')
        def validate_secret_key(cls, v):
            if len(v) < 32:
                raise ValueError('Secret key must be at least 32 characters long')
            return v
        
        class Config:
            env_prefix = "SECURITY_"


    class SocialPlatformSettings(BaseSettings):
        """Social platform API configuration."""
        
        # Twitter
        twitter_api_key: Optional[str] = Field(default=None, env="TWITTER_API_KEY")
        twitter_api_secret: Optional[str] = Field(default=None, env="TWITTER_API_SECRET")
        
        # Instagram
        instagram_access_token: Optional[str] = Field(default=None, env="INSTAGRAM_ACCESS_TOKEN")
        
        # TikTok
        tiktok_access_token: Optional[str] = Field(default=None, env="TIKTOK_ACCESS_TOKEN")
        
        # Facebook
        facebook_access_token: Optional[str] = Field(default=None, env="FACEBOOK_ACCESS_TOKEN")
        
        # LinkedIn
        linkedin_access_token: Optional[str] = Field(default=None, env="LINKEDIN_ACCESS_TOKEN")
        
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


else:
    # Fallback implementation when pydantic-settings is not available
    import os
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # dotenv not available, use system environment only
    
    class FallbackSettings:
        """Fallback settings implementation using environment variables."""
        
        def __init__(self):
            # Application settings
            self.app_name = os.getenv("APP_NAME", "Maya AI Content System")
            self.debug = os.getenv("DEBUG", "false").lower() == "true"
            self.environment = os.getenv("ENVIRONMENT", "development")
            
            # API settings
            self.api_host = os.getenv("API_HOST", "0.0.0.0")
            self.api_port = int(os.getenv("API_PORT", "8000"))
            
            # Database settings
            self.database_url = os.getenv("DATABASE_URL", "postgresql://maya:maya@localhost:5432/maya")
            
            # Redis settings
            self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            
            # AI settings (create a simple namespace object)
            class AINamespace:
                def __init__(self):
                    self.openai_api_key = os.getenv("OPENAI_API_KEY")
                    self.huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
                    self.model_cache_dir = os.getenv("MODEL_CACHE_DIR", "./models/cache")
            
            self.ai = AINamespace()
            
            # Security settings
            self.secret_key = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
            self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
            self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
            
            # Social platform settings
            self.twitter_api_key = os.getenv("TWITTER_API_KEY")
            self.twitter_api_secret = os.getenv("TWITTER_API_SECRET")
            self.instagram_access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
            
            # Monitoring settings
            self.sentry_dsn = os.getenv("SENTRY_DSN")
            self.prometheus_port = int(os.getenv("PROMETHEUS_PORT", "8090"))
            self.log_level = os.getenv("LOG_LEVEL", "INFO")
            self.json_logs = os.getenv("JSON_LOGS", "true").lower() == "true"
    
    # Alias for backward compatibility
    Settings = FallbackSettings
    DatabaseSettings = FallbackSettings
    RedisSettings = FallbackSettings
    AISettings = FallbackSettings
    SecuritySettings = FallbackSettings
    SocialPlatformSettings = FallbackSettings
    MonitoringSettings = FallbackSettings
    
    def get_settings() -> FallbackSettings:
        """Get application settings singleton (fallback version)."""
        return FallbackSettings()