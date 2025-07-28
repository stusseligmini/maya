"""
Content processing service for Maya AI Content Optimization
"""

import re
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class ContentProcessor:
    """Content processing and optimization service"""
    
    def __init__(self):
        self.platform_limits = {
            "twitter": {"max_length": 280, "max_hashtags": 5, "max_mentions": 10},
            "instagram": {"max_length": 2200, "max_hashtags": 30, "max_mentions": 20},
            "linkedin": {"max_length": 3000, "max_hashtags": 10, "max_mentions": 10},
            "tiktok": {"max_length": 150, "max_hashtags": 10, "max_mentions": 5}
        }
    
    def optimize_content(self, text: str, platform: str = "twitter") -> Dict:
        """Optimize content for a specific platform"""
        result = {
            "original_text": text,
            "optimized_text": text,
            "optimization_score": 0,
            "changes_made": [],
            "platform": platform,
            "metadata": {}
        }
        
        # Get platform limits
        limits = self.platform_limits.get(platform, self.platform_limits["twitter"])
        
        # Extract existing hashtags and mentions
        hashtags = self._extract_hashtags(text)
        mentions = self._extract_mentions(text)
        
        optimized_text = text
        changes = []
        
        # Optimize length
        if len(text) > limits["max_length"]:
            optimized_text = self._truncate_text(optimized_text, limits["max_length"])
            changes.append("Truncated text to fit platform limit")
        
        # Optimize hashtags
        if len(hashtags) > limits["max_hashtags"]:
            excess_hashtags = hashtags[limits["max_hashtags"]:]
            for hashtag in excess_hashtags:
                optimized_text = optimized_text.replace(hashtag, "")
            changes.append(f"Removed {len(excess_hashtags)} excess hashtags")
        
        # Add platform-specific optimizations
        if platform == "twitter":
            optimized_text = self._optimize_for_twitter(optimized_text)
            changes.append("Applied Twitter-specific optimizations")
        elif platform == "instagram":
            optimized_text = self._optimize_for_instagram(optimized_text)
            changes.append("Applied Instagram-specific optimizations")
        elif platform == "linkedin":
            optimized_text = self._optimize_for_linkedin(optimized_text)
            changes.append("Applied LinkedIn-specific optimizations")
        
        # Calculate optimization score
        score = self._calculate_optimization_score(text, optimized_text, platform)
        
        result.update({
            "optimized_text": optimized_text.strip(),
            "optimization_score": score,
            "changes_made": changes,
            "hashtags": self._extract_hashtags(optimized_text),
            "mentions": self._extract_mentions(optimized_text),
            "metadata": {
                "character_count": len(optimized_text),
                "word_count": len(optimized_text.split()),
                "hashtag_count": len(self._extract_hashtags(optimized_text)),
                "mention_count": len(self._extract_mentions(optimized_text))
            }
        })
        
        return result
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        return re.findall(r'#\w+', text)
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text"""
        return re.findall(r'@\w+', text)
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Intelligently truncate text to fit within length limit"""
        if len(text) <= max_length:
            return text
        
        # Try to truncate at sentence boundary
        sentences = text.split('. ')
        truncated = ""
        
        for sentence in sentences:
            if len(truncated + sentence + '. ') <= max_length:
                truncated += sentence + '. '
            else:
                break
        
        if truncated:
            return truncated.strip()
        
        # If no sentence boundary works, truncate at word boundary
        words = text.split()
        truncated = ""
        
        for word in words:
            if len(truncated + word + ' ') <= max_length:
                truncated += word + ' '
            else:
                break
        
        return truncated.strip() + "..."
    
    def _optimize_for_twitter(self, text: str) -> str:
        """Apply Twitter-specific optimizations"""
        # Ensure hashtags are relevant and not excessive
        if "#Twitter" not in text and "#X" not in text:
            # Add relevant hashtag if space allows
            if len(text) < 260:
                text += " #SocialMedia"
        
        return text
    
    def _optimize_for_instagram(self, text: str) -> str:
        """Apply Instagram-specific optimizations"""
        # Instagram allows more hashtags and longer content
        if len(text) < 2000 and not any(tag in text for tag in ["#Instagram", "#Insta"]):
            text += " #ContentCreation #DigitalMarketing"
        
        return text
    
    def _optimize_for_linkedin(self, text: str) -> str:
        """Apply LinkedIn-specific optimizations"""
        # LinkedIn prefers professional tone
        if len(text) < 2800 and "#LinkedIn" not in text:
            text += " #Professional #Business"
        
        return text
    
    def _calculate_optimization_score(self, original: str, optimized: str, platform: str) -> int:
        """Calculate optimization score based on various factors"""
        score = 50  # Base score
        
        limits = self.platform_limits.get(platform, self.platform_limits["twitter"])
        
        # Length optimization
        if len(optimized) <= limits["max_length"]:
            score += 20
        
        # Hashtag optimization
        hashtag_count = len(self._extract_hashtags(optimized))
        if hashtag_count > 0 and hashtag_count <= limits["max_hashtags"]:
            score += 15
        
        # Content engagement factors
        if any(word in optimized.lower() for word in ["question", "?", "what", "how", "why"]):
            score += 10  # Questions tend to engage
        
        if any(emoji in optimized for emoji in ["✨", "🚀", "💡", "🎯", "📈"]):
            score += 5  # Emojis can increase engagement
        
        # Readability
        words = optimized.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        if 4 <= avg_word_length <= 6:  # Optimal readability
            score += 10
        
        return min(score, 100)  # Cap at 100
    
    def analyze_content(self, text: str) -> Dict:
        """Analyze content for various metrics"""
        words = text.split()
        sentences = text.split('.')
        
        return {
            "character_count": len(text),
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0,
            "hashtags": self._extract_hashtags(text),
            "mentions": self._extract_mentions(text),
            "urls": re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text),
            "readability_score": self._calculate_readability_score(text),
            "engagement_factors": self._identify_engagement_factors(text)
        }
    
    def _calculate_readability_score(self, text: str) -> int:
        """Calculate a simple readability score"""
        words = text.split()
        if not words:
            return 0
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        sentences = [s for s in text.split('.') if s.strip()]
        avg_sentence_length = len(words) / len(sentences) if sentences else len(words)
        
        # Simple readability calculation (scale 0-100)
        score = 100 - (avg_word_length * 5) - (avg_sentence_length * 2)
        return max(0, min(100, int(score)))
    
    def _identify_engagement_factors(self, text: str) -> List[str]:
        """Identify factors that may increase engagement"""
        factors = []
        
        if '?' in text:
            factors.append("Contains questions")
        
        if any(word in text.lower() for word in ["call", "action", "now", "today", "limited"]):
            factors.append("Call to action")
        
        if any(emoji in text for emoji in ["😊", "😍", "🔥", "💯", "✨", "🚀"]):
            factors.append("Contains emojis")
        
        if len(self._extract_hashtags(text)) > 0:
            factors.append("Uses hashtags")
        
        if len(self._extract_mentions(text)) > 0:
            factors.append("Mentions users")
        
        return factors