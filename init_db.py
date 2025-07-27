#!/usr/bin/env python3
"""
Database initialization script for Maya AI Content Optimization
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import init_db, engine, SessionLocal
from app.models.social_platform import SocialPlatform
from app.models.ai_model import AIModel, AIProvider
import structlog

logger = structlog.get_logger()


def create_sample_data():
    """Create sample data for development"""
    db = SessionLocal()
    
    try:
        # Create sample social platforms
        platforms = [
            {
                "name": "instagram",
                "display_name": "Instagram",
                "max_image_size": 8 * 1024 * 1024,  # 8MB
                "max_video_size": 100 * 1024 * 1024,  # 100MB
                "max_video_duration": 60,
                "supported_formats": ["jpg", "jpeg", "png", "mp4", "mov"],
                "image_dimensions": {"min": {"width": 320, "height": 320}, "max": {"width": 1080, "height": 1080}},
                "supports_carousel": True,
                "supports_stories": True,
                "supports_reels": True,
                "api_base_url": "https://graph.instagram.com"
            },
            {
                "name": "tiktok",
                "display_name": "TikTok",
                "max_video_size": 72 * 1024 * 1024,  # 72MB
                "max_video_duration": 180,
                "supported_formats": ["mp4", "mov"],
                "supports_reels": True,
                "api_base_url": "https://open-api.tiktok.com"
            },
            {
                "name": "twitter",
                "display_name": "Twitter/X",
                "max_image_size": 5 * 1024 * 1024,  # 5MB
                "max_video_size": 512 * 1024 * 1024,  # 512MB
                "max_video_duration": 140,
                "supported_formats": ["jpg", "jpeg", "png", "gif", "mp4", "mov"],
                "image_dimensions": {"max": {"width": 1200, "height": 675}},
                "api_base_url": "https://api.twitter.com"
            }
        ]
        
        for platform_data in platforms:
            existing = db.query(SocialPlatform).filter(SocialPlatform.name == platform_data["name"]).first()
            if not existing:
                platform = SocialPlatform(**platform_data)
                db.add(platform)
                logger.info("Created platform", name=platform_data["name"])
        
        # Create sample AI models
        models = [
            {
                "name": "gpt-4-vision",
                "display_name": "GPT-4 Vision",
                "description": "OpenAI's multimodal model for image and text processing",
                "provider": AIProvider.OPENAI,
                "model_id": "gpt-4-vision-preview",
                "supports_images": True,
                "supports_text": True,
                "default_params": {"max_tokens": 1000, "temperature": 0.7},
                "is_premium": True
            },
            {
                "name": "runway-gen2",
                "display_name": "Runway Gen-2",
                "description": "Runway's video generation model",
                "provider": AIProvider.RUNWAY,
                "model_id": "gen2",
                "supports_videos": True,
                "supports_images": True,
                "is_premium": True
            },
            {
                "name": "huggingface-clip",
                "display_name": "CLIP Image Analysis",
                "description": "HuggingFace CLIP model for image understanding",
                "provider": AIProvider.HUGGINGFACE,
                "model_id": "openai/clip-vit-base-patch32",
                "supports_images": True,
                "supports_text": True
            }
        ]
        
        for model_data in models:
            existing = db.query(AIModel).filter(AIModel.name == model_data["name"]).first()
            if not existing:
                model = AIModel(**model_data)
                db.add(model)
                logger.info("Created AI model", name=model_data["name"])
        
        db.commit()
        logger.info("Sample data created successfully")
        
    except Exception as e:
        logger.error("Error creating sample data", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Initialize database and create sample data"""
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully")
        
        logger.info("Creating sample data...")
        create_sample_data()
        logger.info("Database setup completed successfully")
        
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()