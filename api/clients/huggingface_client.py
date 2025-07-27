"""
Hugging Face API client for AI model inference
"""
import aiohttp
import json
from typing import Dict, List, Optional, Any
from ..config.secrets import HUGGINGFACE_API_KEY

class HuggingFaceClient:
    def __init__(self):
        if not HUGGINGFACE_API_KEY:
            raise ValueError("Hugging Face API key not configured")
        
        self.api_key = HUGGINGFACE_API_KEY
        self.base_url = "https://api-inference.huggingface.co/models"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    async def _make_request(self, model: str, payload: Dict) -> Any:
        """Make async request to Hugging Face API"""
        url = f"{self.base_url}/{model}"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Hugging Face API error: {response.status} - {error_text}")
    
    async def analyze_image_content(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze image content using vision models"""
        # Use BLIP for image captioning
        try:
            result = await self._make_request(
                "Salesforce/blip-image-captioning-large",
                {"inputs": image_data.decode('latin-1') if isinstance(image_data, bytes) else image_data}
            )
            
            caption = result[0]["generated_text"] if result else "Could not generate caption"
            
            return {
                "generated_caption": caption,
                "confidence": 0.8,  # Mock confidence score
                "detected_objects": [],  # Would need object detection model
                "scene_description": caption
            }
        except Exception as e:
            return {
                "generated_caption": "Analysis failed",
                "confidence": 0.0,
                "detected_objects": [],
                "scene_description": "Could not analyze image",
                "error": str(e)
            }
    
    async def detect_nsfw_content(self, image_data: bytes) -> Dict[str, float]:
        """Detect NSFW content in images"""
        try:
            # Use a NSFW detection model
            result = await self._make_request(
                "Falconsai/nsfw_image_detection",
                {"inputs": image_data}
            )
            
            # Parse results and return scores
            scores = {}
            if isinstance(result, list) and result:
                for item in result:
                    if isinstance(item, dict) and 'label' in item and 'score' in item:
                        scores[item['label']] = item['score']
            
            # Normalize to expected format
            return {
                "nsfw_score": scores.get("nsfw", 0.0),
                "safe_score": scores.get("safe", 1.0),
                "suggestive_score": scores.get("suggestive", 0.0),
                "explicit_score": scores.get("explicit", 0.0)
            }
            
        except Exception as e:
            # Return safe defaults if detection fails
            return {
                "nsfw_score": 0.0,
                "safe_score": 1.0,
                "suggestive_score": 0.0,
                "explicit_score": 0.0,
                "error": str(e)
            }
    
    async def analyze_text_emotion(self, text: str) -> Dict[str, float]:
        """Analyze emotional content of text"""
        try:
            result = await self._make_request(
                "j-hartmann/emotion-english-distilroberta-base",
                {"inputs": text}
            )
            
            emotions = {}
            if isinstance(result, list) and result:
                for emotion_data in result:
                    if isinstance(emotion_data, list):
                        for emotion in emotion_data:
                            if isinstance(emotion, dict) and 'label' in emotion and 'score' in emotion:
                                emotions[emotion['label']] = emotion['score']
            
            # Ensure we have all expected emotions
            expected_emotions = ['joy', 'sadness', 'anger', 'fear', 'surprise', 'disgust', 'neutral']
            for emotion in expected_emotions:
                if emotion not in emotions:
                    emotions[emotion] = 0.0
            
            return emotions
            
        except Exception as e:
            # Return neutral defaults
            return {
                'joy': 0.1,
                'sadness': 0.1,
                'anger': 0.1,
                'fear': 0.1,
                'surprise': 0.1,
                'disgust': 0.1,
                'neutral': 0.4,
                'error': str(e)
            }
    
    async def classify_content_category(self, text: str) -> Dict[str, Any]:
        """Classify content into categories"""
        try:
            result = await self._make_request(
                "facebook/bart-large-mnli",
                {
                    "inputs": text,
                    "parameters": {
                        "candidate_labels": [
                            "entertainment", "education", "lifestyle", "business",
                            "technology", "fashion", "travel", "food", "fitness",
                            "art", "music", "sports", "news", "personal"
                        ]
                    }
                }
            )
            
            if result and 'labels' in result and 'scores' in result:
                categories = {}
                for label, score in zip(result['labels'], result['scores']):
                    categories[label] = score
                
                return {
                    "primary_category": result['labels'][0],
                    "confidence": result['scores'][0],
                    "all_categories": categories
                }
            
            return {
                "primary_category": "general",
                "confidence": 0.5,
                "all_categories": {"general": 0.5}
            }
            
        except Exception as e:
            return {
                "primary_category": "general",
                "confidence": 0.0,
                "all_categories": {"general": 0.5},
                "error": str(e)
            }
    
    async def extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract keywords using NER and keyword extraction"""
        try:
            # Use Named Entity Recognition
            ner_result = await self._make_request(
                "dbmdz/bert-large-cased-finetuned-conll03-english",
                {"inputs": text}
            )
            
            keywords = []
            if isinstance(ner_result, list):
                for entity in ner_result:
                    if isinstance(entity, dict) and 'word' in entity:
                        # Clean up word (remove ## tokens from BERT)
                        word = entity['word'].replace('##', '')
                        if len(word) > 2 and word not in keywords:
                            keywords.append(word)
            
            return keywords[:10]  # Return top 10 keywords
            
        except Exception as e:
            # Fallback: simple keyword extraction
            words = text.split()
            # Filter out common words and return unique words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
            keywords = [word.lower().strip('.,!?;:') for word in words if len(word) > 3 and word.lower() not in stop_words]
            return list(set(keywords))[:10]
    
    async def generate_hashtags(self, text: str, platform: str = "instagram") -> List[str]:
        """Generate relevant hashtags for content"""
        try:
            # Use text classification to understand content
            categories_result = await self.classify_content_category(text)
            keywords = await self.extract_keywords_from_text(text)
            
            # Generate hashtags based on categories and keywords
            hashtags = []
            
            # Add category-based hashtags
            primary_category = categories_result.get("primary_category", "general")
            hashtags.append(f"#{primary_category}")
            
            # Add keyword-based hashtags
            for keyword in keywords[:5]:
                hashtag = f"#{keyword.replace(' ', '').lower()}"
                if hashtag not in hashtags:
                    hashtags.append(hashtag)
            
            # Add platform-specific hashtags
            platform_hashtags = {
                "instagram": ["#instagram", "#insta", "#instagood"],
                "tiktok": ["#tiktok", "#fyp", "#foryou"],
                "twitter": ["#twitter", "#trending"],
                "fanvue": ["#fanvue", "#content"],
                "snapchat": ["#snapchat", "#snap"]
            }
            
            if platform in platform_hashtags:
                hashtags.extend(platform_hashtags[platform][:2])
            
            return hashtags[:15]  # Limit to 15 hashtags
            
        except Exception as e:
            # Return basic hashtags as fallback
            return ["#content", "#social", "#post", f"#{platform}"]
    
    async def predict_engagement(self, content_features: Dict) -> float:
        """Predict engagement score based on content features"""
        try:
            # This would typically use a trained model
            # For now, we'll use a simple heuristic based on features
            
            score = 0.5  # Base score
            
            # Adjust based on text length
            text_length = content_features.get("text_length", 100)
            if 50 <= text_length <= 200:
                score += 0.1
            
            # Adjust based on emotion scores
            emotions = content_features.get("emotions", {})
            joy_score = emotions.get("joy", 0)
            if joy_score > 0.5:
                score += 0.15
            
            # Adjust based on hashtag count
            hashtag_count = content_features.get("hashtag_count", 0)
            if 5 <= hashtag_count <= 10:
                score += 0.1
            
            # Adjust based on content category
            category = content_features.get("category", "general")
            if category in ["entertainment", "lifestyle", "fashion"]:
                score += 0.1
            
            # Ensure score is between 0 and 1
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            return 0.5  # Return neutral score if prediction fails
