"""
Secret configuration - NEVER commit this file to Git!
"""
import os
from typing import Optional

# Database secrets
DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL", "postgresql://maya:maya_secret@postgres:5432/maya_db")
REDIS_URL: Optional[str] = os.getenv("REDIS_URL", "redis://redis:6379/0")

# API Keys for external services
OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_API_KEY: Optional[str] = os.getenv("HUGGINGFACE_API_KEY")
RUNWAY_API_KEY: Optional[str] = os.getenv("RUNWAY_API_KEY")

# Social Media API Keys
INSTAGRAM_ACCESS_TOKEN: Optional[str] = os.getenv("INSTAGRAM_ACCESS_TOKEN")
TIKTOK_ACCESS_TOKEN: Optional[str] = os.getenv("TIKTOK_ACCESS_TOKEN")
TWITTER_API_KEY: Optional[str] = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET: Optional[str] = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN: Optional[str] = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET: Optional[str] = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Telegram Bot
TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID: Optional[str] = os.getenv("TELEGRAM_CHAT_ID")

# Storage & Security
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-this-in-production")
ENCRYPTION_KEY: Optional[str] = os.getenv("ENCRYPTION_KEY")
PROTON_USERNAME: Optional[str] = os.getenv("PROTON_USERNAME")
PROTON_PASSWORD: Optional[str] = os.getenv("PROTON_PASSWORD")

# AI Model Settings
FOOOCUS_API_URL: str = os.getenv("FOOOCUS_API_URL", "http://ai-service:8080")
MODEL_CACHE_SIZE: int = int(os.getenv("MODEL_CACHE_SIZE", "1000"))
