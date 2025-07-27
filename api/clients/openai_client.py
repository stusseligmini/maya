"""
OpenAI API client for content generation and analysis
"""
import openai
from typing import List, Dict, Optional
import json
import asyncio
from ..config.secrets import OPENAI_API_KEY

class OpenAIClient:
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        openai.api_key = OPENAI_API_KEY
    
    async def generate_caption(
        self, 
        content_description: str, 
        platform: str, 
        target_keywords: Optional[str] = None
    ) -> str:
        """Generate platform-specific caption"""
        
        platform_instructions = {
            "instagram": "Create an engaging Instagram caption with emojis and hashtags",
            "tiktok": "Create a catchy TikTok caption that's short and trendy",
            "twitter": "Create a Twitter post under 280 characters",
            "fanvue": "Create professional, engaging content for Fanvue platform",
            "snapchat": "Create a fun, casual Snapchat caption"
        }
        
        prompt = f"""
        Create a {platform} caption for content described as: {content_description}
        
        Instructions: {platform_instructions.get(platform, 'Create an engaging caption')}
        {f'Include these keywords naturally: {target_keywords}' if target_keywords else ''}
        
        Requirements:
        - Platform-appropriate tone and style
        - Engaging and authentic
        - Proper use of hashtags and emojis where appropriate
        - Optimized for {platform} algorithm
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert social media content creator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI caption generation failed: {str(e)}")
    
    async def analyze_content_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text content"""
        prompt = f"""
        Analyze the sentiment of this text and return scores (0-1) for:
        - positive: How positive the content is
        - negative: How negative the content is  
        - neutral: How neutral the content is
        - engagement: Predicted engagement potential
        - professionalism: How professional the tone is
        
        Text: {text}
        
        Return only a JSON object with the scores.
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a sentiment analysis expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return result
        except Exception as e:
            # Return default scores if analysis fails
            return {
                "positive": 0.5,
                "negative": 0.2,
                "neutral": 0.3,
                "engagement": 0.5,
                "professionalism": 0.6
            }
    
    async def extract_keywords(self, text: str, count: int = 10) -> List[str]:
        """Extract relevant keywords from text"""
        prompt = f"""
        Extract the {count} most relevant keywords from this text for SEO and content optimization:
        
        {text}
        
        Return only a JSON array of keywords, no other text.
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an SEO expert. Return only valid JSON arrays."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            keywords = json.loads(response.choices[0].message.content.strip())
            return keywords if isinstance(keywords, list) else []
        except Exception as e:
            return []
    
    async def optimize_for_platform(
        self, 
        content: str, 
        platform: str, 
        current_performance: Optional[Dict] = None
    ) -> Dict[str, str]:
        """Provide optimization suggestions for specific platform"""
        
        performance_context = ""
        if current_performance:
            performance_context = f"Current performance data: {json.dumps(current_performance)}"
        
        prompt = f"""
        Optimize this content for {platform}:
        
        Current content: {content}
        {performance_context}
        
        Provide optimization suggestions for:
        1. Caption improvements
        2. Hashtag strategy
        3. Posting time recommendations
        4. Engagement tactics
        5. Visual suggestions
        
        Return as JSON object with these keys: caption, hashtags, timing, engagement, visual
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are a {platform} optimization expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.6
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return result
        except Exception as e:
            return {
                "caption": "Could not generate optimization",
                "hashtags": "Could not generate hashtags", 
                "timing": "Could not generate timing suggestions",
                "engagement": "Could not generate engagement tactics",
                "visual": "Could not generate visual suggestions"
            }
    
    async def generate_content_insights(self, performance_data: List[Dict]) -> Dict:
        """Generate insights from content performance data"""
        prompt = f"""
        Analyze this content performance data and provide actionable insights:
        
        {json.dumps(performance_data, indent=2)}
        
        Provide insights on:
        1. Top performing content types
        2. Optimal posting patterns
        3. Audience engagement trends
        4. Content optimization recommendations
        5. Platform-specific strategies
        
        Return as JSON with keys: top_content, posting_patterns, engagement_trends, recommendations, platform_strategies
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a data analyst and content strategy expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.5
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return result
        except Exception as e:
            return {
                "top_content": "Analysis unavailable",
                "posting_patterns": "Analysis unavailable",
                "engagement_trends": "Analysis unavailable", 
                "recommendations": "Analysis unavailable",
                "platform_strategies": "Analysis unavailable"
            }
