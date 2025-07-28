from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ContentType(str, Enum):
    BLOG_POST = "blog_post"
    ARTICLE = "article"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    LANDING_PAGE = "landing_page"
    PRODUCT_DESCRIPTION = "product_description"

class ContentStatus(str, Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    OPTIMIZED = "optimized"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content_type = Column(SQLEnum(ContentType), nullable=False)
    original_content = Column(Text, nullable=False)
    optimized_content = Column(Text, nullable=True)
    target_keywords = Column(Text, nullable=True)  # JSON string of keywords
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.DRAFT)
    seo_score = Column(Integer, nullable=True)
    readability_score = Column(Integer, nullable=True)
    user_id = Column(Integer, nullable=True)  # Foreign key to users table
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)