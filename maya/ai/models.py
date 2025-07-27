"""AI model integrations for Maya system."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

# Try to import AI libraries with fallback handling
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

import io
import base64

from maya.core.exceptions import AIModelError, ConfigurationError
from maya.core.logging import LoggerMixin
from maya.config.settings import get_settings


class BaseAIModel(ABC, LoggerMixin):
    """Base class for AI model integrations."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.settings = get_settings()
    
    @abstractmethod
    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content based on prompt."""
        pass
    
    @abstractmethod
    async def analyze_content(self, content: str, **kwargs) -> Dict[str, Any]:
        """Analyze content and return insights."""
        pass


class OpenAIIntegration(BaseAIModel):
    """OpenAI GPT model integration."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        super().__init__(model_name)
        
        if not OPENAI_AVAILABLE:
            raise ConfigurationError("OpenAI library not available. Install with: pip install openai")
        
        if not self.settings.ai.openai_api_key:
            raise ConfigurationError("OpenAI API key not configured")
        
        openai.api_key = self.settings.ai.openai_api_key
        self.client = openai.OpenAI(api_key=self.settings.ai.openai_api_key)
    
    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using OpenAI GPT."""
        try:
            max_tokens = kwargs.get("max_tokens", 150)
            temperature = kwargs.get("temperature", 0.7)
            
            self.logger.info("Generating content with OpenAI", 
                           model=self.model_name, prompt_length=len(prompt))
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            content = response.choices[0].message.content
            self.logger.info("Content generated successfully", 
                           content_length=len(content))
            
            return content
            
        except Exception as e:
            self.logger.error("OpenAI content generation failed", error=str(e))
            raise AIModelError(f"OpenAI content generation failed: {str(e)}")
    
    async def analyze_content(self, content: str, **kwargs) -> Dict[str, Any]:
        """Analyze content sentiment and engagement potential."""
        try:
            analysis_prompt = f"""
            Analyze the following social media content and provide:
            1. Sentiment (positive/negative/neutral)
            2. Engagement potential (high/medium/low)
            3. Key topics/hashtags
            4. Suggested improvements
            
            Content: {content}
            
            Respond in JSON format.
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            # Note: In production, you'd want to parse this more robustly
            analysis = response.choices[0].message.content
            
            return {
                "model": self.model_name,
                "analysis": analysis,
                "content_length": len(content)
            }
            
        except Exception as e:
            self.logger.error("OpenAI content analysis failed", error=str(e))
            raise AIModelError(f"OpenAI content analysis failed: {str(e)}")


class HuggingFaceIntegration(BaseAIModel):
    """HuggingFace transformers integration."""
    
    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"):
        super().__init__(model_name)
        
        if not TRANSFORMERS_AVAILABLE:
            raise ConfigurationError("Transformers library not available. Install with: pip install transformers torch")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.logger.info("HuggingFace model loaded successfully", model=model_name)
            
        except Exception as e:
            self.logger.error("Failed to load HuggingFace model", error=str(e))
            raise ConfigurationError(f"Failed to load HuggingFace model: {str(e)}")
    
    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using HuggingFace models."""
        # This is a placeholder - HuggingFace generation would require different models
        # like GPT-2, T5, etc. For demonstration, we return a processed version
        try:
            self.logger.info("Processing content with HuggingFace", 
                           model=self.model_name)
            
            # This is a simplified example
            processed_content = f"Processed: {prompt[:100]}..."
            
            return processed_content
            
        except Exception as e:
            self.logger.error("HuggingFace content generation failed", error=str(e))
            raise AIModelError(f"HuggingFace content generation failed: {str(e)}")
    
    async def analyze_content(self, content: str, **kwargs) -> Dict[str, Any]:
        """Analyze content sentiment using HuggingFace."""
        try:
            self.logger.info("Analyzing content sentiment", 
                           content_length=len(content))
            
            # Truncate content if too long
            max_length = 512
            if len(content) > max_length:
                content = content[:max_length]
            
            results = self.sentiment_pipeline(content)
            
            analysis = {
                "model": self.model_name,
                "sentiment": results[0]["label"],
                "confidence": results[0]["score"],
                "content_length": len(content)
            }
            
            self.logger.info("Content analysis completed", 
                           sentiment=analysis["sentiment"],
                           confidence=analysis["confidence"])
            
            return analysis
            
        except Exception as e:
            self.logger.error("HuggingFace content analysis failed", error=str(e))
            raise AIModelError(f"HuggingFace content analysis failed: {str(e)}")


class AIModelManager(LoggerMixin):
    """Manager for AI model integrations."""
    
    def __init__(self):
        self.models: Dict[str, BaseAIModel] = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize available AI models."""
        settings = get_settings()
        
        try:
            if settings.ai.openai_api_key:
                self.models["openai"] = OpenAIIntegration()
                self.logger.info("OpenAI model initialized")
        except Exception as e:
            self.logger.warning("Failed to initialize OpenAI model", error=str(e))
        
        try:
            self.models["huggingface"] = HuggingFaceIntegration()
            self.logger.info("HuggingFace model initialized")
        except Exception as e:
            self.logger.warning("Failed to initialize HuggingFace model", error=str(e))
    
    def get_model(self, model_type: str) -> BaseAIModel:
        """Get AI model by type."""
        if model_type not in self.models:
            raise AIModelError(f"Model type '{model_type}' not available")
        
        return self.models[model_type]
    
    def list_available_models(self) -> List[str]:
        """List available model types."""
        return list(self.models.keys())


# Global AI model manager instance
ai_manager = AIModelManager()