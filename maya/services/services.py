"""
Unified services module for Maya system.

This module provides a consolidated approach to service management
by combining AI services, content processing services, and platform
optimization into a single, cohesive interface.
"""

import asyncio
import structlog
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from pathlib import Path

from maya.core.exceptions import ServiceError, AIModelError, ContentProcessingError
from maya.core.logging import LoggerMixin
from maya.core.config import get_settings
from maya.ai.models import ai_manager, BaseAIModel

# Import content processing components
from maya.content.processor import (
    ContentItem, 
    ContentType, 
    Platform, 
    ContentProcessor as ContentPipelineProcessor, 
    ProcessingResult
)

logger = structlog.get_logger()
settings = get_settings()


class AIService(LoggerMixin):
    """Unified AI service for content generation and analysis."""
    
    def __init__(self):
        self.available_models = ai_manager.list_available_models()
        self.logger.info("AI Service initialized", 
                        available_models=self.available_models)
    
    async def generate_content(
        self, 
        prompt: str, 
        model_type: str = "openai", 
        **kwargs
    ) -> Dict[str, Any]:
        """Generate content using specified AI model."""
        try:
            if model_type not in self.available_models:
                if len(self.available_models) > 0:
                    model_type = self.available_models[0]
                    self.logger.warning(f"Requested model {model_type} not available, using {model_type}")
                else:
                    raise ServiceError("No AI models available")
            
            model = ai_manager.get_model(model_type)
            content = await model.generate_content(prompt, **kwargs)
            
            result = {
                "content": content,
                "model": model_type,
                "prompt_length": len(prompt),
                "content_length": len(content),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.info("Content generated successfully", 
                           model=model_type, content_length=len(content))
            
            return result
            
        except Exception as e:
            self.logger.error("Content generation failed", 
                            model=model_type, error=str(e))
            raise ServiceError(f"Content generation failed: {str(e)}")
    
    async def analyze_content(
        self, 
        content: str, 
        model_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Analyze content using available AI models."""
        results = {}
        errors = []
        
        # If no specific models requested, use all available
        if not model_types:
            model_types = self.available_models
        
        for model_type in model_types:
            if model_type in self.available_models:
                try:
                    model = ai_manager.get_model(model_type)
                    analysis = await model.analyze_content(content)
                    results[model_type] = analysis
                except Exception as e:
                    error_msg = f"Analysis with {model_type} failed: {str(e)}"
                    errors.append(error_msg)
                    self.logger.error("Content analysis failed", 
                                    model=model_type, error=str(e))
        
        if not results and errors:
            raise ServiceError(f"All content analysis failed: {'; '.join(errors)}")
        
        return {
            "results": results, 
            "errors": errors,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of AI service and available models."""
        return {
            "status": "healthy" if self.available_models else "degraded",
            "available_models": self.available_models,
            "timestamp": datetime.utcnow().isoformat()
        }


class ContentService(LoggerMixin):
    """Unified content processing and optimization service."""
    
    def __init__(self):
        self.processor = ContentPipelineProcessor()
        self.logger.info("Content Service initialized")
    
    async def process_content(
        self,
        content_data: Dict[str, Any],
        target_platforms: List[str] = None,
        analyze_with_ai: bool = True
    ) -> Dict[str, Any]:
        """Process content for optimization across platforms."""
        try:
            # Convert input data to ContentItem
            content_item = self._create_content_item(content_data)
            
            # Convert platform strings to enum values
            platforms = []
            if target_platforms:
                for platform_str in target_platforms:
                    try:
                        platform = Platform[platform_str.upper()]
                        platforms.append(platform)
                    except (KeyError, ValueError):
                        self.logger.warning(f"Invalid platform: {platform_str}")
            
            # Default to all platforms if none specified
            if not platforms:
                platforms = [Platform.TWITTER, Platform.INSTAGRAM, Platform.FACEBOOK]
            
            # Process content
            self.logger.info("Processing content", 
                           content_id=content_item.id,
                           platforms=[p.value for p in platforms])
            
            result = await self.processor.process_content(
                content_item, 
                platforms,
                analyze_with_ai=analyze_with_ai
            )
            
            # Convert result to dictionary
            result_dict = result.to_dict()
            
            self.logger.info("Content processing completed", 
                           content_id=content_item.id,
                           processing_time=result.processing_time)
            
            return result_dict
            
        except Exception as e:
            self.logger.error("Content processing failed", error=str(e))
            raise ServiceError(f"Content processing failed: {str(e)}")
    
    async def process_image(
        self,
        image_path: str,
        target_platform: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process image content for optimization."""
        try:
            self.logger.info("Processing image", 
                           path=image_path, 
                           platform=target_platform)
            
            # Create content item from image
            content_data = {
                "content_type": ContentType.IMAGE.value,
                "media_urls": [image_path],
                "metadata": metadata or {}
            }
            
            platforms = []
            if target_platform:
                try:
                    platform = Platform[target_platform.upper()]
                    platforms = [platform]
                except (KeyError, ValueError):
                    self.logger.warning(f"Invalid platform: {target_platform}")
                    platforms = [Platform.INSTAGRAM]  # Default for images
            else:
                platforms = [Platform.INSTAGRAM]
            
            content_item = self._create_content_item(content_data)
            result = await self.processor.process_content(content_item, platforms)
            
            return result.to_dict()
            
        except Exception as e:
            self.logger.error("Image processing failed", 
                            path=image_path, error=str(e))
            raise ServiceError(f"Image processing failed: {str(e)}")
    
    async def process_video(
        self,
        video_path: str,
        target_platform: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process video content for optimization."""
        try:
            self.logger.info("Processing video", 
                           path=video_path, 
                           platform=target_platform)
            
            # Create content item from video
            content_data = {
                "content_type": ContentType.VIDEO.value,
                "media_urls": [video_path],
                "metadata": metadata or {}
            }
            
            platforms = []
            if target_platform:
                try:
                    platform = Platform[target_platform.upper()]
                    platforms = [platform]
                except (KeyError, ValueError):
                    self.logger.warning(f"Invalid platform: {target_platform}")
                    platforms = [Platform.TIKTOK]  # Default for videos
            else:
                platforms = [Platform.TIKTOK]
            
            content_item = self._create_content_item(content_data)
            result = await self.processor.process_content(content_item, platforms)
            
            return result.to_dict()
            
        except Exception as e:
            self.logger.error("Video processing failed", 
                            path=video_path, error=str(e))
            raise ServiceError(f"Video processing failed: {str(e)}")
    
    def get_platform_requirements(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific content requirements."""
        try:
            platform_enum = Platform[platform.upper()]
            return {
                "platform": platform,
                "limits": {
                    "text": ContentPipelineProcessor().validator.PLATFORM_LIMITS[platform_enum]["text"],
                    "images": ContentPipelineProcessor().validator.PLATFORM_LIMITS[platform_enum]["images"],
                    "videos": ContentPipelineProcessor().validator.PLATFORM_LIMITS[platform_enum]["videos"]
                }
            }
        except (KeyError, ValueError):
            valid_platforms = [p.value for p in Platform]
            raise ServiceError(f"Invalid platform: {platform}. Valid platforms: {valid_platforms}")
    
    def _create_content_item(self, content_data: Dict[str, Any]) -> ContentItem:
        """Create ContentItem from dictionary data."""
        try:
            # Extract content type
            content_type_str = content_data.get("content_type", "TEXT")
            try:
                content_type = ContentType[content_type_str.upper()]
            except (KeyError, ValueError):
                content_type = ContentType.TEXT
                self.logger.warning(f"Invalid content type: {content_type_str}, using TEXT")
            
            # Generate ID if not provided
            content_id = content_data.get("id")
            if not content_id:
                import uuid
                content_id = str(uuid.uuid4())
            
            # Create ContentItem
            return ContentItem(
                id=content_id,
                content_type=content_type,
                text=content_data.get("text"),
                media_urls=content_data.get("media_urls"),
                hashtags=content_data.get("hashtags"),
                mentions=content_data.get("mentions"),
                metadata=content_data.get("metadata")
            )
            
        except Exception as e:
            self.logger.error("Failed to create ContentItem", error=str(e))
            raise ServiceError(f"Failed to create ContentItem: {str(e)}")


class PlatformService(LoggerMixin):
    """Service for platform-specific optimizations and publishing."""
    
    PLATFORM_SPECS = {
        "instagram": {
            "image": {"max_width": 1080, "max_height": 1080, "aspect_ratios": ["1:1", "4:5", "16:9"]},
            "video": {"max_duration": 60, "max_size_mb": 100, "formats": ["mp4", "mov"]},
            "text": {"max_length": 2200, "hashtag_limit": 30}
        },
        "tiktok": {
            "video": {"max_duration": 180, "max_size_mb": 72, "aspect_ratio": "9:16", "formats": ["mp4", "mov"]},
            "text": {"max_length": 150, "hashtag_limit": 5}
        },
        "twitter": {
            "image": {"max_width": 1200, "max_height": 675, "max_size_mb": 5},
            "video": {"max_duration": 140, "max_size_mb": 512, "formats": ["mp4", "mov"]},
            "text": {"max_length": 280, "hashtag_limit": 3}
        },
        "facebook": {
            "image": {"max_width": 1200, "max_height": 630},
            "video": {"max_duration": 240, "max_size_mb": 4000},
            "text": {"max_length": 63206}
        },
        "linkedin": {
            "image": {"max_width": 1200, "max_height": 627},
            "video": {"max_duration": 600, "max_size_mb": 5000},
            "text": {"max_length": 3000}
        }
    }
    
    def __init__(self):
        self.logger.info("Platform Service initialized")
    
    async def optimize_for_platform(
        self,
        content_data: Dict[str, Any],
        platform: str
    ) -> Dict[str, Any]:
        """Optimize content for specific platform."""
        try:
            platform = platform.lower()
            specs = self.PLATFORM_SPECS.get(platform)
            
            if not specs:
                valid_platforms = list(self.PLATFORM_SPECS.keys())
                raise ServiceError(f"Invalid platform: {platform}. Valid platforms: {valid_platforms}")
            
            self.logger.info("Optimizing for platform", 
                           platform=platform, 
                           content_id=content_data.get("id"))
            
            # Use ContentService for actual optimization
            content_service = ContentService()
            result = await content_service.process_content(
                content_data,
                target_platforms=[platform]
            )
            
            return {
                "platform": platform,
                "optimized": True,
                "specs_applied": specs,
                "result": result
            }
            
        except Exception as e:
            self.logger.error("Platform optimization failed", 
                            platform=platform, error=str(e))
            raise ServiceError(f"Platform optimization failed: {str(e)}")
    
    def get_platform_requirements(self, platform: str = None) -> Dict[str, Any]:
        """Get platform-specific requirements."""
        if platform:
            platform = platform.lower()
            specs = self.PLATFORM_SPECS.get(platform)
            if not specs:
                valid_platforms = list(self.PLATFORM_SPECS.keys())
                raise ServiceError(f"Invalid platform: {platform}. Valid platforms: {valid_platforms}")
            return {platform: specs}
        else:
            return self.PLATFORM_SPECS


# Initialize service instances
ai_service = AIService()
content_service = ContentService()
platform_service = PlatformService()
