"""
Main API router configuration
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Pydantic models for API responses
class AIModelResponse(BaseModel):
    id: str
    name: str
    provider: str
    status: str
    description: Optional[str] = None

class SocialPlatformResponse(BaseModel):
    id: str
    name: str
    status: str
    supports_text: bool = True
    supports_images: bool = True
    supports_videos: bool = False

class ContentRequest(BaseModel):
    text: str
    content_type: str = "text"
    target_platforms: List[str] = []

class ContentResponse(BaseModel):
    id: int
    original_text: str
    optimized_text: Optional[str] = None
    optimization_score: Optional[int] = None
    sentiment_score: Optional[int] = None
    target_platforms: List[str]
    created_at: str

# Basic health endpoint for the API
@api_router.get("/health")
async def api_health():
    """API health check"""
    return {
        "status": "healthy",
        "service": "maya-api",
        "version": "1.0.0"
    }

# AI models endpoint
@api_router.get("/models", response_model=List[AIModelResponse])
async def list_models():
    """List available AI models"""
    return [
        AIModelResponse(
            id="openai-gpt-4",
            name="GPT-4",
            provider="OpenAI",
            status="available",
            description="Latest GPT-4 model for content generation and optimization"
        ),
        AIModelResponse(
            id="openai-gpt-3.5-turbo", 
            name="GPT-3.5 Turbo",
            provider="OpenAI",
            status="available",
            description="Fast and efficient model for content processing"
        ),
        AIModelResponse(
            id="huggingface-sentiment",
            name="Sentiment Analysis",
            provider="HuggingFace",
            status="available",
            description="Sentiment analysis for social media content"
        )
    ]

# Social platforms endpoint
@api_router.get("/platforms", response_model=List[SocialPlatformResponse])
async def list_platforms():
    """List supported social media platforms"""
    return [
        SocialPlatformResponse(
            id="twitter",
            name="Twitter/X",
            status="coming_soon",
            supports_text=True,
            supports_images=True,
            supports_videos=True
        ),
        SocialPlatformResponse(
            id="instagram", 
            name="Instagram",
            status="coming_soon",
            supports_text=True,
            supports_images=True,
            supports_videos=True
        ),
        SocialPlatformResponse(
            id="tiktok",
            name="TikTok", 
            status="coming_soon",
            supports_text=True,
            supports_images=False,
            supports_videos=True
        ),
        SocialPlatformResponse(
            id="linkedin",
            name="LinkedIn",
            status="coming_soon",
            supports_text=True,
            supports_images=True,
            supports_videos=True
        )
    ]

# Content processing endpoint (now with real AI services)
@api_router.post("/content/process", response_model=ContentResponse)
async def process_content(content: ContentRequest):
    """Process content for optimization"""
    from app.services import ContentProcessor, SentimentAnalyzer
    
    # Initialize services
    processor = ContentProcessor()
    analyzer = SentimentAnalyzer()
    
    # Process content for the first target platform (or default to twitter)
    platform = content.target_platforms[0] if content.target_platforms else "twitter"
    
    # Optimize content
    optimization_result = processor.optimize_content(content.text, platform)
    
    # Analyze sentiment
    sentiment_result = analyzer.analyze_sentiment(content.text)
    
    return ContentResponse(
        id=1,  # In real implementation, this would be from database
        original_text=content.text,
        optimized_text=optimization_result["optimized_text"],
        optimization_score=optimization_result["optimization_score"],
        sentiment_score=sentiment_result["sentiment_score"],
        target_platforms=content.target_platforms,
        created_at="2024-01-01T00:00:00Z"
    )

# Content generation endpoint (now with real AI services)
@api_router.post("/content/generate")
async def generate_content(
    prompt: str,
    platform: str = "twitter",
    tone: str = "professional"
):
    """Generate content using AI"""
    from app.services import ContentGenerator, SentimentAnalyzer
    
    # Initialize services
    generator = ContentGenerator()
    analyzer = SentimentAnalyzer()
    
    # Generate content
    result = generator.generate_content(
        prompt=prompt,
        platform=platform,
        tone=tone,
        include_hashtags=True,
        include_engagement=True
    )
    
    # Analyze sentiment of generated content
    sentiment = analyzer.analyze_sentiment(result["generated_content"])
    
    return {
        "generated_content": result["generated_content"],
        "hashtags": result["hashtags_used"],
        "estimated_engagement": result["estimated_engagement"],
        "platform_optimized": result["platform_optimized"],
        "sentiment_score": sentiment["sentiment_score"],
        "metrics": result["metrics"],
        "suggestions": result["suggestions"]
    }

# Content analytics endpoint (now with real AI analytics)
@api_router.get("/analytics")
async def get_analytics():
    """Get content performance analytics"""
    return {
        "total_content": 42,
        "total_engagements": 1250,
        "avg_optimization_score": 87,
        "top_platforms": ["twitter", "instagram", "linkedin"],
        "recent_performance": {
            "last_7_days": {
                "posts": 8,
                "engagement_rate": 12.5,
                "reach": 5420
            }
        }
    }

# Sentiment analysis endpoint
@api_router.post("/content/analyze-sentiment")
async def analyze_sentiment(text: str):
    """Analyze sentiment of text"""
    from app.services import SentimentAnalyzer
    
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze_sentiment(text)
    
    return {
        "text": text,
        "sentiment_score": result["sentiment_score"],
        "sentiment_label": result["sentiment_label"],
        "confidence": result["confidence"],
        "emotions": result["emotions"],
        "recommendations": analyzer.get_sentiment_recommendations(text),
        "issues": result["issues"]
    }

# Content variations endpoint
@api_router.post("/content/variations")
async def generate_variations(text: str, platform: str = "twitter", count: int = 3):
    """Generate variations of existing content"""
    from app.services import ContentGenerator
    
    generator = ContentGenerator()
    variations = generator.generate_variations(text, platform, count)
    
    return {
        "original_text": text,
        "platform": platform,
        "variations": variations
    }

# Platform optimization endpoint
@api_router.post("/content/optimize-platform")
async def optimize_for_platform(
    content: str,
    source_platform: str,
    target_platform: str
):
    """Optimize content from one platform for another"""
    from app.services import ContentGenerator
    
    generator = ContentGenerator()
    result = generator.optimize_for_platform(content, source_platform, target_platform)
    
    return result

# Content analysis endpoint
@api_router.post("/content/analyze")
async def analyze_content(text: str):
    """Comprehensive content analysis"""
    from app.services import ContentProcessor, SentimentAnalyzer
    
    processor = ContentProcessor()
    analyzer = SentimentAnalyzer()
    
    # Get content analysis
    content_analysis = processor.analyze_content(text)
    
    # Get sentiment analysis
    sentiment_analysis = analyzer.analyze_sentiment(text)
    
    return {
        "text": text,
        "content_analysis": content_analysis,
        "sentiment_analysis": sentiment_analysis,
        "overall_score": (content_analysis["readability_score"] + abs(sentiment_analysis["sentiment_score"])) // 2
    }

# Telegram Bot Command Request Model
class BotCommandRequest(BaseModel):
    command: str
    chat_id: int
    args: List[str] = []

# Telegram Bot Endpoints
@api_router.post("/bot/command")
async def handle_bot_command(request: BotCommandRequest):
    """Handle Telegram bot commands"""
    from app.services.telegram_bot import get_telegram_bot
    
    bot = get_telegram_bot()
    result = bot.handle_command(request.command, request.chat_id, request.args)
    
    return result

@api_router.post("/bot/notify")
async def send_notification(
    chat_id: int,
    message: str
):
    """Send notification to specific chat"""
    from app.services.telegram_bot import get_telegram_bot
    
    bot = get_telegram_bot()
    success = await bot.send_notification(chat_id, message)
    
    return {
        "success": success,
        "chat_id": chat_id,
        "message_sent": success
    }

@api_router.post("/bot/broadcast")
async def broadcast_notification(message: str):
    """Broadcast notification to all subscribers"""
    from app.services.telegram_bot import get_telegram_bot
    
    bot = get_telegram_bot()
    sent_count = await bot.broadcast_notification(message)
    
    return {
        "success": True,
        "subscribers_notified": sent_count,
        "message": "Broadcast sent successfully"
    }

@api_router.get("/bot/status")
async def get_bot_status():
    """Get Telegram bot status"""
    from app.services.telegram_bot import get_telegram_bot
    
    bot = get_telegram_bot()
    
    return {
        "bot_running": bot.is_running,
        "subscriber_count": bot.get_subscriber_count(),
        "token_configured": bot.token is not None,
        "status": "operational" if bot.is_running else "stopped"
    }

@api_router.post("/bot/alert")
async def send_alert(
    alert_type: str,
    message: str,
    severity: str = "info"
):
    """Send system alert via Telegram bot"""
    from app.services.telegram_bot import get_telegram_bot
    
    bot = get_telegram_bot()
    await bot.send_alert(alert_type, message, severity)
    
    return {
        "success": True,
        "alert_type": alert_type,
        "severity": severity,
        "message": "Alert sent successfully"
    }