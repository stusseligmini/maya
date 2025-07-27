"""Content processing pipeline for Maya system."""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import asyncio
from datetime import datetime
import hashlib
import json

from maya.core.exceptions import ContentProcessingError, ValidationError
from maya.core.logging import LoggerMixin
from maya.ai.models import ai_manager


class ContentType(Enum):
    """Content type enumeration."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    MIXED = "mixed"


class Platform(Enum):
    """Social media platform enumeration."""
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"


@dataclass
class ContentItem:
    """Content item data structure."""
    id: str
    content_type: ContentType
    text: Optional[str] = None
    media_urls: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        
        if self.id is None:
            # Generate ID from content hash
            content_str = f"{self.text or ''}{self.media_urls or []}"
            self.id = hashlib.md5(content_str.encode()).hexdigest()


@dataclass
class ProcessingResult:
    """Content processing result."""
    original_content: ContentItem
    optimized_content: ContentItem
    analysis: Dict[str, Any]
    recommendations: List[str]
    platform_specific: Dict[Platform, Dict[str, Any]]
    processing_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "original_content": self._content_to_dict(self.original_content),
            "optimized_content": self._content_to_dict(self.optimized_content),
            "analysis": self.analysis,
            "recommendations": self.recommendations,
            "platform_specific": {p.value: data for p, data in self.platform_specific.items()},
            "processing_time": self.processing_time
        }
    
    def _content_to_dict(self, content: ContentItem) -> Dict[str, Any]:
        """Convert ContentItem to dictionary."""
        return {
            "id": content.id,
            "content_type": content.content_type.value,
            "text": content.text,
            "media_urls": content.media_urls,
            "hashtags": content.hashtags,
            "mentions": content.mentions,
            "metadata": content.metadata,
            "created_at": content.created_at.isoformat() if content.created_at else None
        }


class ContentValidator(LoggerMixin):
    """Content validation utilities."""
    
    PLATFORM_LIMITS = {
        Platform.TWITTER: {"text": 280, "images": 4, "videos": 1},
        Platform.INSTAGRAM: {"text": 2200, "images": 10, "videos": 1},
        Platform.TIKTOK: {"text": 150, "images": 0, "videos": 1},
        Platform.FACEBOOK: {"text": 63206, "images": 10, "videos": 1},
        Platform.LINKEDIN: {"text": 3000, "images": 20, "videos": 1}
    }
    
    def validate_content(self, content: ContentItem, platform: Platform) -> List[str]:
        """Validate content for specific platform."""
        issues = []
        limits = self.PLATFORM_LIMITS.get(platform)
        
        if not limits:
            return issues
        
        # Text length validation
        if content.text and len(content.text) > limits["text"]:
            issues.append(f"Text exceeds {platform.value} limit of {limits['text']} characters")
        
        # Media validation
        if content.media_urls:
            image_count = sum(1 for url in content.media_urls if self._is_image(url))
            video_count = sum(1 for url in content.media_urls if self._is_video(url))
            
            if image_count > limits["images"]:
                issues.append(f"Too many images for {platform.value} (max: {limits['images']})")
            
            if video_count > limits["videos"]:
                issues.append(f"Too many videos for {platform.value} (max: {limits['videos']})")
        
        self.logger.info("Content validation completed", 
                        platform=platform.value, issues_count=len(issues))
        
        return issues
    
    def _is_image(self, url: str) -> bool:
        """Check if URL is an image."""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        return any(url.lower().endswith(ext) for ext in image_extensions)
    
    def _is_video(self, url: str) -> bool:
        """Check if URL is a video."""
        video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm'}
        return any(url.lower().endswith(ext) for ext in video_extensions)


class ContentOptimizer(LoggerMixin):
    """Content optimization engine."""
    
    def __init__(self):
        self.validator = ContentValidator()
    
    async def optimize_for_platform(self, content: ContentItem, platform: Platform) -> ContentItem:
        """Optimize content for specific platform."""
        try:
            self.logger.info("Optimizing content for platform", 
                           platform=platform.value, content_id=content.id)
            
            # Validate original content
            issues = self.validator.validate_content(content, platform)
            
            optimized_content = ContentItem(
                id=f"{content.id}_optimized_{platform.value}",
                content_type=content.content_type,
                text=content.text,
                media_urls=content.media_urls.copy() if content.media_urls else None,
                hashtags=content.hashtags.copy() if content.hashtags else None,
                mentions=content.mentions.copy() if content.mentions else None,
                metadata=content.metadata.copy() if content.metadata else {}
            )
            
            # Apply platform-specific optimizations
            if platform == Platform.TWITTER:
                optimized_content = await self._optimize_for_twitter(optimized_content)
            elif platform == Platform.INSTAGRAM:
                optimized_content = await self._optimize_for_instagram(optimized_content)
            elif platform == Platform.TIKTOK:
                optimized_content = await self._optimize_for_tiktok(optimized_content)
            
            # Add optimization metadata
            if not optimized_content.metadata:
                optimized_content.metadata = {}
            
            optimized_content.metadata.update({
                "platform": platform.value,
                "optimization_applied": True,
                "original_issues": issues,
                "optimized_at": datetime.utcnow().isoformat()
            })
            
            self.logger.info("Content optimization completed", 
                           platform=platform.value, content_id=optimized_content.id)
            
            return optimized_content
            
        except Exception as e:
            self.logger.error("Content optimization failed", 
                            platform=platform.value, error=str(e))
            raise ContentProcessingError(f"Content optimization failed: {str(e)}")
    
    async def _optimize_for_twitter(self, content: ContentItem) -> ContentItem:
        """Twitter-specific optimizations."""
        if content.text and len(content.text) > 280:
            # Truncate and add "..."
            content.text = content.text[:277] + "..."
        
        # Optimize hashtags (max 2-3 for better engagement)
        if content.hashtags and len(content.hashtags) > 3:
            content.hashtags = content.hashtags[:3]
        
        return content
    
    async def _optimize_for_instagram(self, content: ContentItem) -> ContentItem:
        """Instagram-specific optimizations."""
        # Instagram allows more hashtags (up to 30)
        if content.hashtags and len(content.hashtags) > 30:
            content.hashtags = content.hashtags[:30]
        
        return content
    
    async def _optimize_for_tiktok(self, content: ContentItem) -> ContentItem:
        """TikTok-specific optimizations."""
        if content.text and len(content.text) > 150:
            content.text = content.text[:147] + "..."
        
        # TikTok prefers fewer hashtags (3-5)
        if content.hashtags and len(content.hashtags) > 5:
            content.hashtags = content.hashtags[:5]
        
        return content


class ContentProcessor(LoggerMixin):
    """Main content processing pipeline."""
    
    def __init__(self):
        self.optimizer = ContentOptimizer()
        self.validator = ContentValidator()
    
    async def process_content(
        self, 
        content: ContentItem, 
        target_platforms: List[Platform],
        analyze_with_ai: bool = True
    ) -> ProcessingResult:
        """Process content for multiple platforms."""
        start_time = datetime.utcnow()
        
        try:
            self.logger.info("Starting content processing", 
                           content_id=content.id, 
                           platforms=[p.value for p in target_platforms])
            
            # AI Analysis
            analysis = {}
            if analyze_with_ai and content.text:
                analysis = await self._analyze_with_ai(content.text)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(content, analysis)
            
            # Platform-specific optimization
            platform_specific = {}
            optimized_content = content
            
            for platform in target_platforms:
                platform_optimized = await self.optimizer.optimize_for_platform(content, platform)
                platform_specific[platform] = {
                    "optimized_content": platform_optimized,
                    "validation_issues": self.validator.validate_content(platform_optimized, platform)
                }
                
                # Use the first platform's optimization as the main optimized content
                if platform == target_platforms[0]:
                    optimized_content = platform_optimized
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = ProcessingResult(
                original_content=content,
                optimized_content=optimized_content,
                analysis=analysis,
                recommendations=recommendations,
                platform_specific=platform_specific,
                processing_time=processing_time
            )
            
            self.logger.info("Content processing completed", 
                           content_id=content.id, 
                           processing_time=processing_time)
            
            return result
            
        except Exception as e:
            self.logger.error("Content processing failed", 
                            content_id=content.id, error=str(e))
            raise ContentProcessingError(f"Content processing failed: {str(e)}")
    
    async def _analyze_with_ai(self, text: str) -> Dict[str, Any]:
        """Analyze content using AI models."""
        try:
            analysis = {}
            
            # Try different AI models
            available_models = ai_manager.list_available_models()
            
            for model_type in available_models:
                try:
                    model = ai_manager.get_model(model_type)
                    model_analysis = await model.analyze_content(text)
                    analysis[model_type] = model_analysis
                except Exception as e:
                    self.logger.warning(f"AI analysis failed for {model_type}", error=str(e))
            
            return analysis
            
        except Exception as e:
            self.logger.error("AI analysis failed", error=str(e))
            return {"error": str(e)}
    
    async def _generate_recommendations(
        self, 
        content: ContentItem, 
        analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate content improvement recommendations."""
        recommendations = []
        
        # Basic recommendations based on content
        if content.text:
            if len(content.text) < 50:
                recommendations.append("Consider adding more descriptive text for better engagement")
            
            if not content.hashtags:
                recommendations.append("Add relevant hashtags to increase discoverability")
            elif len(content.hashtags) > 10:
                recommendations.append("Consider reducing hashtags for better readability")
        
        # AI-based recommendations
        if analysis:
            for model_type, model_analysis in analysis.items():
                if isinstance(model_analysis, dict):
                    if model_analysis.get("sentiment") == "NEGATIVE":
                        recommendations.append("Content has negative sentiment - consider more positive framing")
                    
                    confidence = model_analysis.get("confidence", 0)
                    if confidence < 0.5:
                        recommendations.append("AI sentiment analysis shows low confidence - content may be ambiguous")
        
        return recommendations