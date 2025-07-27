"""Social media platform integrations for Maya system."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
import json

from maya.core.exceptions import SocialPlatformError, AuthenticationError, RateLimitError
from maya.core.logging import LoggerMixin
from maya.config.settings import get_settings
from maya.content.processor import ContentItem, Platform


@dataclass
class PostResult:
    """Result of a social media post."""
    platform: Platform
    post_id: str
    url: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    status: str = "published"
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ScheduledPost:
    """Scheduled social media post."""
    id: str
    content: ContentItem
    platform: Platform
    scheduled_time: datetime
    status: str = "scheduled"
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class BaseSocialPlatform(ABC, LoggerMixin):
    """Base class for social media platform integrations."""
    
    def __init__(self, platform: Platform):
        self.platform = platform
        self.settings = get_settings()
        self._rate_limits = {}
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the platform."""
        pass
    
    @abstractmethod
    async def publish_content(self, content: ContentItem) -> PostResult:
        """Publish content to the platform."""
        pass
    
    @abstractmethod
    async def schedule_content(self, content: ContentItem, publish_time: datetime) -> PostResult:
        """Schedule content for future publishing."""
        pass
    
    @abstractmethod
    async def unpublish_content(self, post_id: str) -> bool:
        """Remove published content."""
        pass
    
    async def _check_rate_limit(self, endpoint: str) -> bool:
        """Check if rate limit allows the request."""
        current_time = datetime.utcnow()
        
        if endpoint not in self._rate_limits:
            self._rate_limits[endpoint] = {
                "requests": 0,
                "reset_time": current_time + timedelta(hours=1)
            }
        
        limit_info = self._rate_limits[endpoint]
        
        # Reset counter if time window has passed
        if current_time >= limit_info["reset_time"]:
            limit_info["requests"] = 0
            limit_info["reset_time"] = current_time + timedelta(hours=1)
        
        # Simple rate limiting (adjust per platform)
        max_requests = 100  # Default limit
        if limit_info["requests"] >= max_requests:
            self.logger.warning("Rate limit exceeded", 
                              platform=self.platform.value, endpoint=endpoint)
            return False
        
        limit_info["requests"] += 1
        return True


class TwitterIntegration(BaseSocialPlatform):
    """Twitter/X platform integration."""
    
    def __init__(self):
        super().__init__(Platform.TWITTER)
        self._api_client = None
    
    async def authenticate(self) -> bool:
        """Authenticate with Twitter API."""
        try:
            api_key = self.settings.social.twitter_api_key
            api_secret = self.settings.social.twitter_api_secret
            
            if not api_key or not api_secret:
                raise AuthenticationError("Twitter API credentials not configured")
            
            # In a real implementation, you would use tweepy or similar
            # For demonstration, we'll simulate authentication
            self.logger.info("Twitter authentication successful")
            return True
            
        except Exception as e:
            self.logger.error("Twitter authentication failed", error=str(e))
            raise AuthenticationError(f"Twitter authentication failed: {str(e)}")
    
    async def publish_content(self, content: ContentItem) -> PostResult:
        """Publish content to Twitter."""
        try:
            if not await self._check_rate_limit("publish"):
                raise RateLimitError("Twitter publish rate limit exceeded")
            
            await self.authenticate()
            
            self.logger.info("Publishing content to Twitter", content_id=content.id)
            
            # Simulate posting to Twitter
            # In real implementation, use tweepy.Client.create_tweet()
            post_id = f"twitter_{content.id}_{int(datetime.utcnow().timestamp())}"
            
            result = PostResult(
                platform=self.platform,
                post_id=post_id,
                url=f"https://twitter.com/user/status/{post_id}",
                status="published",
                metadata={
                    "character_count": len(content.text) if content.text else 0,
                    "hashtag_count": len(content.hashtags) if content.hashtags else 0
                }
            )
            
            self.logger.info("Content published to Twitter successfully", 
                           post_id=post_id, content_id=content.id)
            
            return result
            
        except Exception as e:
            self.logger.error("Twitter publishing failed", 
                            content_id=content.id, error=str(e))
            raise SocialPlatformError(f"Twitter publishing failed: {str(e)}")
    
    async def schedule_content(self, content: ContentItem, publish_time: datetime) -> PostResult:
        """Schedule content for Twitter."""
        try:
            await self.authenticate()
            
            self.logger.info("Scheduling content for Twitter", 
                           content_id=content.id, publish_time=publish_time.isoformat())
            
            # Simulate scheduling
            post_id = f"twitter_scheduled_{content.id}_{int(datetime.utcnow().timestamp())}"
            
            result = PostResult(
                platform=self.platform,
                post_id=post_id,
                scheduled_time=publish_time,
                status="scheduled",
                metadata={
                    "scheduled_for": publish_time.isoformat(),
                    "character_count": len(content.text) if content.text else 0
                }
            )
            
            self.logger.info("Content scheduled for Twitter successfully", 
                           post_id=post_id, content_id=content.id)
            
            return result
            
        except Exception as e:
            self.logger.error("Twitter scheduling failed", 
                            content_id=content.id, error=str(e))
            raise SocialPlatformError(f"Twitter scheduling failed: {str(e)}")
    
    async def unpublish_content(self, post_id: str) -> bool:
        """Delete a Twitter post."""
        try:
            await self.authenticate()
            
            self.logger.info("Unpublishing content from Twitter", post_id=post_id)
            
            # Simulate deletion
            # In real implementation, use tweepy.Client.delete_tweet()
            
            self.logger.info("Content unpublished from Twitter successfully", post_id=post_id)
            return True
            
        except Exception as e:
            self.logger.error("Twitter unpublishing failed", 
                            post_id=post_id, error=str(e))
            raise SocialPlatformError(f"Twitter unpublishing failed: {str(e)}")


class InstagramIntegration(BaseSocialPlatform):
    """Instagram platform integration."""
    
    def __init__(self):
        super().__init__(Platform.INSTAGRAM)
    
    async def authenticate(self) -> bool:
        """Authenticate with Instagram API."""
        try:
            access_token = self.settings.social.instagram_access_token
            
            if not access_token:
                raise AuthenticationError("Instagram access token not configured")
            
            # Simulate authentication
            self.logger.info("Instagram authentication successful")
            return True
            
        except Exception as e:
            self.logger.error("Instagram authentication failed", error=str(e))
            raise AuthenticationError(f"Instagram authentication failed: {str(e)}")
    
    async def publish_content(self, content: ContentItem) -> PostResult:
        """Publish content to Instagram."""
        try:
            if not await self._check_rate_limit("publish"):
                raise RateLimitError("Instagram publish rate limit exceeded")
            
            await self.authenticate()
            
            self.logger.info("Publishing content to Instagram", content_id=content.id)
            
            # Instagram requires media for posts
            if not content.media_urls:
                raise SocialPlatformError("Instagram posts require media content")
            
            # Simulate posting to Instagram
            post_id = f"instagram_{content.id}_{int(datetime.utcnow().timestamp())}"
            
            result = PostResult(
                platform=self.platform,
                post_id=post_id,
                url=f"https://instagram.com/p/{post_id}",
                status="published",
                metadata={
                    "media_count": len(content.media_urls),
                    "caption_length": len(content.text) if content.text else 0,
                    "hashtag_count": len(content.hashtags) if content.hashtags else 0
                }
            )
            
            self.logger.info("Content published to Instagram successfully", 
                           post_id=post_id, content_id=content.id)
            
            return result
            
        except Exception as e:
            self.logger.error("Instagram publishing failed", 
                            content_id=content.id, error=str(e))
            raise SocialPlatformError(f"Instagram publishing failed: {str(e)}")
    
    async def schedule_content(self, content: ContentItem, publish_time: datetime) -> PostResult:
        """Schedule content for Instagram."""
        try:
            await self.authenticate()
            
            self.logger.info("Scheduling content for Instagram", 
                           content_id=content.id, publish_time=publish_time.isoformat())
            
            # Simulate scheduling
            post_id = f"instagram_scheduled_{content.id}_{int(datetime.utcnow().timestamp())}"
            
            result = PostResult(
                platform=self.platform,
                post_id=post_id,
                scheduled_time=publish_time,
                status="scheduled",
                metadata={
                    "scheduled_for": publish_time.isoformat(),
                    "media_count": len(content.media_urls) if content.media_urls else 0
                }
            )
            
            self.logger.info("Content scheduled for Instagram successfully", 
                           post_id=post_id, content_id=content.id)
            
            return result
            
        except Exception as e:
            self.logger.error("Instagram scheduling failed", 
                            content_id=content.id, error=str(e))
            raise SocialPlatformError(f"Instagram scheduling failed: {str(e)}")
    
    async def unpublish_content(self, post_id: str) -> bool:
        """Delete an Instagram post."""
        try:
            await self.authenticate()
            
            self.logger.info("Unpublishing content from Instagram", post_id=post_id)
            
            # Simulate deletion
            self.logger.info("Content unpublished from Instagram successfully", post_id=post_id)
            return True
            
        except Exception as e:
            self.logger.error("Instagram unpublishing failed", 
                            post_id=post_id, error=str(e))
            raise SocialPlatformError(f"Instagram unpublishing failed: {str(e)}")


class SocialMediaManager(LoggerMixin):
    """Manager for social media platform integrations."""
    
    def __init__(self):
        self.platforms: Dict[Platform, BaseSocialPlatform] = {
            Platform.TWITTER: TwitterIntegration(),
            Platform.INSTAGRAM: InstagramIntegration(),
        }
        self.scheduled_posts: List[ScheduledPost] = []
    
    def get_platform(self, platform: Platform) -> BaseSocialPlatform:
        """Get platform integration by type."""
        if platform not in self.platforms:
            raise SocialPlatformError(f"Platform '{platform.value}' not supported")
        
        return self.platforms[platform]
    
    async def publish_to_platforms(
        self, 
        content: ContentItem, 
        platforms: List[Platform]
    ) -> Dict[Platform, PostResult]:
        """Publish content to multiple platforms."""
        results = {}
        
        self.logger.info("Publishing content to multiple platforms", 
                        content_id=content.id, 
                        platforms=[p.value for p in platforms])
        
        # Publish to all platforms concurrently
        tasks = []
        for platform in platforms:
            platform_integration = self.get_platform(platform)
            task = asyncio.create_task(
                platform_integration.publish_content(content),
                name=f"publish_{platform.value}"
            )
            tasks.append((platform, task))
        
        # Wait for all publications to complete
        for platform, task in tasks:
            try:
                result = await task
                results[platform] = result
                self.logger.info("Platform publishing completed", 
                               platform=platform.value, post_id=result.post_id)
            except Exception as e:
                self.logger.error("Platform publishing failed", 
                                platform=platform.value, error=str(e))
                results[platform] = PostResult(
                    platform=platform,
                    post_id="",
                    status="failed",
                    metadata={"error": str(e)}
                )
        
        return results
    
    async def schedule_for_platforms(
        self, 
        content: ContentItem, 
        platforms: List[Platform],
        publish_time: datetime
    ) -> Dict[Platform, PostResult]:
        """Schedule content for multiple platforms."""
        results = {}
        
        self.logger.info("Scheduling content for multiple platforms", 
                        content_id=content.id, 
                        platforms=[p.value for p in platforms],
                        publish_time=publish_time.isoformat())
        
        for platform in platforms:
            try:
                platform_integration = self.get_platform(platform)
                result = await platform_integration.schedule_content(content, publish_time)
                results[platform] = result
                
                # Store scheduled post
                scheduled_post = ScheduledPost(
                    id=result.post_id,
                    content=content,
                    platform=platform,
                    scheduled_time=publish_time
                )
                self.scheduled_posts.append(scheduled_post)
                
            except Exception as e:
                self.logger.error("Platform scheduling failed", 
                                platform=platform.value, error=str(e))
                results[platform] = PostResult(
                    platform=platform,
                    post_id="",
                    status="failed",
                    metadata={"error": str(e)}
                )
        
        return results
    
    async def unpublish_from_platforms(
        self, 
        post_ids: Dict[Platform, str]
    ) -> Dict[Platform, bool]:
        """Unpublish content from multiple platforms."""
        results = {}
        
        self.logger.info("Unpublishing content from multiple platforms", 
                        post_ids=post_ids)
        
        for platform, post_id in post_ids.items():
            try:
                platform_integration = self.get_platform(platform)
                success = await platform_integration.unpublish_content(post_id)
                results[platform] = success
                
            except Exception as e:
                self.logger.error("Platform unpublishing failed", 
                                platform=platform.value, post_id=post_id, error=str(e))
                results[platform] = False
        
        return results
    
    def get_scheduled_posts(
        self, 
        platform: Optional[Platform] = None
    ) -> List[ScheduledPost]:
        """Get scheduled posts, optionally filtered by platform."""
        if platform:
            return [post for post in self.scheduled_posts if post.platform == platform]
        return self.scheduled_posts.copy()
    
    def list_supported_platforms(self) -> List[Platform]:
        """List supported social media platforms."""
        return list(self.platforms.keys())


# Global social media manager instance
social_manager = SocialMediaManager()