"""
Instagram API integration for publishing content
"""
import aiohttp
import json
import asyncio
from typing import Dict, Any, Optional
import logging
from pathlib import Path

from ..config.secrets import INSTAGRAM_ACCESS_TOKEN
from ..database.models import PublishingRecord, Platform

logger = logging.getLogger(__name__)

class InstagramAPI:
    def __init__(self):
        if not INSTAGRAM_ACCESS_TOKEN:
            raise ValueError("Instagram access token not configured")
        
        self.access_token = INSTAGRAM_ACCESS_TOKEN
        self.base_url = "https://graph.facebook.com/v18.0"
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _make_request(self, method: str, endpoint: str, data: Dict = None, files: Dict = None) -> Dict[str, Any]:
        """Make API request to Instagram"""
        session = await self._get_session()
        url = f"{self.base_url}/{endpoint}"
        
        params = {"access_token": self.access_token}
        if data:
            params.update(data)
        
        try:
            if method.upper() == "POST":
                if files:
                    async with session.post(url, params=params, data=files) as response:
                        result = await response.json()
                else:
                    async with session.post(url, params=params) as response:
                        result = await response.json()
            else:
                async with session.get(url, params=params) as response:
                    result = await response.json()
            
            if response.status != 200:
                raise Exception(f"Instagram API error: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"Instagram API request failed: {str(e)}")
            raise
    
    async def get_user_info(self) -> Dict[str, Any]:
        """Get Instagram user information"""
        try:
            result = await self._make_request("GET", "me", {"fields": "id,username,account_type"})
            return result
        except Exception as e:
            logger.error(f"Failed to get Instagram user info: {str(e)}")
            raise
    
    async def upload_image(self, image_path: str, caption: str) -> Dict[str, Any]:
        """Upload image to Instagram"""
        try:
            # Step 1: Create media object
            with open(image_path, 'rb') as image_file:
                create_data = {
                    "image_url": image_path,  # For production, use a public URL
                    "caption": caption,
                    "media_type": "IMAGE"
                }
                
                # Create media container
                create_result = await self._make_request("POST", "me/media", create_data)
                creation_id = create_result.get("id")
                
                if not creation_id:
                    raise Exception("Failed to create media container")
            
            # Step 2: Publish the media
            publish_result = await self._make_request(
                "POST", 
                f"{creation_id}/publish"
            )
            
            return {
                "status": "success",
                "media_id": publish_result.get("id"),
                "creation_id": creation_id,
                "post_url": f"https://instagram.com/p/{publish_result.get('id')}"
            }
            
        except Exception as e:
            logger.error(f"Instagram image upload failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def upload_video(self, video_path: str, caption: str, thumbnail_path: Optional[str] = None) -> Dict[str, Any]:
        """Upload video to Instagram"""
        try:
            create_data = {
                "media_type": "VIDEO",
                "video_url": video_path,  # For production, use a public URL
                "caption": caption
            }
            
            if thumbnail_path:
                create_data["thumb_url"] = thumbnail_path
            
            # Create video container
            create_result = await self._make_request("POST", "me/media", create_data)
            creation_id = create_result.get("id")
            
            if not creation_id:
                raise Exception("Failed to create video container")
            
            # Wait for video processing
            await self._wait_for_video_processing(creation_id)
            
            # Publish the video
            publish_result = await self._make_request(
                "POST", 
                f"{creation_id}/publish"
            )
            
            return {
                "status": "success",
                "media_id": publish_result.get("id"),
                "creation_id": creation_id,
                "post_url": f"https://instagram.com/p/{publish_result.get('id')}"
            }
            
        except Exception as e:
            logger.error(f"Instagram video upload failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _wait_for_video_processing(self, creation_id: str, max_wait: int = 300) -> bool:
        """Wait for video processing to complete"""
        wait_time = 0
        while wait_time < max_wait:
            try:
                status_result = await self._make_request("GET", creation_id, {"fields": "status_code"})
                status_code = status_result.get("status_code")
                
                if status_code == "FINISHED":
                    return True
                elif status_code == "ERROR":
                    raise Exception("Video processing failed")
                
                # Wait before checking again
                await asyncio.sleep(10)
                wait_time += 10
                
            except Exception as e:
                logger.error(f"Error checking video status: {str(e)}")
                await asyncio.sleep(10)
                wait_time += 10
        
        raise Exception("Video processing timeout")
    
    async def upload_carousel(self, media_items: list, caption: str) -> Dict[str, Any]:
        """Upload carousel post with multiple images/videos"""
        try:
            children_ids = []
            
            # Create each media item
            for item in media_items:
                if item["type"] == "image":
                    create_data = {
                        "image_url": item["path"],
                        "media_type": "IMAGE",
                        "is_carousel_item": True
                    }
                else:  # video
                    create_data = {
                        "video_url": item["path"],
                        "media_type": "VIDEO",
                        "is_carousel_item": True
                    }
                
                create_result = await self._make_request("POST", "me/media", create_data)
                children_ids.append(create_result.get("id"))
            
            # Create carousel container
            carousel_data = {
                "media_type": "CAROUSEL",
                "children": ",".join(children_ids),
                "caption": caption
            }
            
            carousel_result = await self._make_request("POST", "me/media", carousel_data)
            carousel_id = carousel_result.get("id")
            
            # Publish carousel
            publish_result = await self._make_request(
                "POST", 
                f"{carousel_id}/publish"
            )
            
            return {
                "status": "success",
                "media_id": publish_result.get("id"),
                "carousel_id": carousel_id,
                "children_count": len(children_ids),
                "post_url": f"https://instagram.com/p/{publish_result.get('id')}"
            }
            
        except Exception as e:
            logger.error(f"Instagram carousel upload failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def get_media_insights(self, media_id: str) -> Dict[str, Any]:
        """Get insights for a published media"""
        try:
            insights_result = await self._make_request(
                "GET", 
                f"{media_id}/insights",
                {"metric": "impressions,reach,likes,comments,shares,saves"}
            )
            
            metrics = {}
            for data in insights_result.get("data", []):
                metrics[data.get("name")] = data.get("values", [{}])[0].get("value", 0)
            
            return {
                "status": "success",
                "media_id": media_id,
                "metrics": metrics
            }
            
        except Exception as e:
            logger.error(f"Failed to get Instagram insights: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def delete_media(self, media_id: str) -> Dict[str, Any]:
        """Delete a media post"""
        try:
            delete_result = await self._make_request("DELETE", media_id)
            return {
                "status": "success",
                "deleted": True
            }
        except Exception as e:
            logger.error(f"Failed to delete Instagram media: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()

# Helper functions for content optimization
def optimize_caption_for_instagram(caption: str, max_length: int = 2200) -> str:
    """Optimize caption for Instagram's requirements"""
    if len(caption) <= max_length:
        return caption
    
    # Truncate and add ellipsis
    return caption[:max_length-3] + "..."

def generate_instagram_hashtags(keywords: list, max_hashtags: int = 30) -> str:
    """Generate Instagram hashtags from keywords"""
    hashtags = []
    
    for keyword in keywords:
        # Clean keyword and make hashtag
        clean_keyword = keyword.strip().replace(" ", "").lower()
        hashtag = f"#{clean_keyword}"
        
        if hashtag not in hashtags and len(hashtags) < max_hashtags:
            hashtags.append(hashtag)
    
    return " ".join(hashtags)

def get_optimal_posting_time() -> str:
    """Get optimal posting time for Instagram (placeholder)"""
    # This would typically be based on audience analytics
    # For now, return a general best practice time
    return "2024-01-01 14:00:00"  # 2 PM is generally good for engagement
