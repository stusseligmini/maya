"""
Content moderation service for images and text
"""
import cv2
import numpy as np
from typing import Dict, Any, List
import asyncio
import logging
from pathlib import Path

from ..api.clients.huggingface_client import HuggingFaceClient
from ..database.models import ModerationResult as ModerationResultEnum, ModerationResult as ModerationResultModel
from ..database.connection import get_db_session
from ..config.settings import settings

logger = logging.getLogger(__name__)

class ImageModerationService:
    def __init__(self):
        self.hf_client = HuggingFaceClient()
        self.nsfw_threshold = getattr(settings, 'NSFW_THRESHOLD', 0.8)
    
    async def moderate_image(self, image_path: str) -> Dict[str, Any]:
        """Moderate image content for NSFW and inappropriate content"""
        try:
            # Read image
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # NSFW Detection
            nsfw_results = await self.hf_client.detect_nsfw_content(image_data)
            
            # Analyze image content
            content_analysis = await self.hf_client.analyze_image_content(image_data)
            
            # Check for explicit content indicators
            explicit_indicators = await self._check_explicit_indicators(image_path)
            
            # Calculate overall safety score
            nsfw_score = nsfw_results.get("nsfw_score", 0.0)
            explicit_score = explicit_indicators.get("explicit_score", 0.0)
            
            # Combine scores
            overall_risk = max(nsfw_score, explicit_score)
            
            # Determine moderation result
            if overall_risk >= self.nsfw_threshold:
                result = ModerationResultEnum.NSFW
            elif overall_risk >= 0.6:
                result = ModerationResultEnum.QUESTIONABLE
            else:
                result = ModerationResultEnum.SAFE
            
            return {
                "result": result,
                "nsfw_score": overall_risk,
                "details": {
                    "nsfw_detection": nsfw_results,
                    "content_analysis": content_analysis,
                    "explicit_indicators": explicit_indicators
                },
                "flagged_content": self._extract_flagged_content(nsfw_results, explicit_indicators),
                "confidence": nsfw_results.get("safe_score", 0.5)
            }
            
        except Exception as e:
            logger.error(f"Image moderation failed: {str(e)}")
            return {
                "result": ModerationResultEnum.SAFE,  # Default to safe if moderation fails
                "nsfw_score": 0.0,
                "details": {"error": str(e)},
                "flagged_content": [],
                "confidence": 0.0
            }
    
    async def _check_explicit_indicators(self, image_path: str) -> Dict[str, Any]:
        """Check for explicit visual indicators using computer vision"""
        try:
            # Load image using OpenCV
            image = cv2.imread(image_path)
            if image is None:
                return {"explicit_score": 0.0, "indicators": []}
            
            indicators = []
            scores = []
            
            # Skin detection (basic heuristic)
            skin_ratio = self._detect_skin_ratio(image)
            if skin_ratio > 0.4:  # High skin exposure
                indicators.append("high_skin_exposure")
                scores.append(skin_ratio)
            
            # Face detection
            face_count = self._detect_faces(image)
            if face_count > 3:  # Many faces might indicate party/inappropriate content
                indicators.append("multiple_faces")
                scores.append(min(face_count / 10, 0.5))
            
            # Blur detection (might indicate hidden content)
            blur_score = self._detect_blur(image)
            if blur_score < 100:  # Very blurry
                indicators.append("blurry_content")
                scores.append(0.3)
            
            explicit_score = max(scores) if scores else 0.0
            
            return {
                "explicit_score": explicit_score,
                "indicators": indicators,
                "skin_ratio": skin_ratio,
                "face_count": face_count,
                "blur_score": blur_score
            }
            
        except Exception as e:
            logger.error(f"Explicit indicator check failed: {str(e)}")
            return {"explicit_score": 0.0, "indicators": [], "error": str(e)}
    
    def _detect_skin_ratio(self, image: np.ndarray) -> float:
        """Detect ratio of skin-colored pixels"""
        try:
            # Convert to HSV for better skin detection
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Define skin color range in HSV
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            
            # Create mask for skin pixels
            skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
            
            # Calculate ratio
            skin_pixels = cv2.countNonZero(skin_mask)
            total_pixels = image.shape[0] * image.shape[1]
            
            return skin_pixels / total_pixels
            
        except Exception:
            return 0.0
    
    def _detect_faces(self, image: np.ndarray) -> int:
        """Detect number of faces in image"""
        try:
            # Load face detection cascade
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            return len(faces)
            
        except Exception:
            return 0
    
    def _detect_blur(self, image: np.ndarray) -> float:
        """Detect image blur using Laplacian variance"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return cv2.Laplacian(gray, cv2.CV_64F).var()
        except Exception:
            return 100.0  # Assume not blurry if detection fails
    
    def _extract_flagged_content(self, nsfw_results: Dict, explicit_indicators: Dict) -> List[str]:
        """Extract list of flagged content types"""
        flagged = []
        
        if nsfw_results.get("nsfw_score", 0) > 0.5:
            flagged.append("nsfw_content")
        
        if nsfw_results.get("suggestive_score", 0) > 0.5:
            flagged.append("suggestive_content")
        
        if nsfw_results.get("explicit_score", 0) > 0.3:
            flagged.append("explicit_content")
        
        flagged.extend(explicit_indicators.get("indicators", []))
        
        return list(set(flagged))  # Remove duplicates

class TextModerationService:
    def __init__(self):
        self.hf_client = HuggingFaceClient()
        self.inappropriate_keywords = self._load_inappropriate_keywords()
    
    def _load_inappropriate_keywords(self) -> List[str]:
        """Load list of inappropriate keywords"""
        # In production, this would be loaded from a database or file
        return [
            "explicit", "nsfw", "adult", "inappropriate",
            # Add more keywords as needed
        ]
    
    async def moderate_text(self, text: str) -> Dict[str, Any]:
        """Moderate text content"""
        try:
            # Emotion analysis
            emotions = await self.hf_client.analyze_text_emotion(text)
            
            # Keyword checking
            keyword_flags = self._check_inappropriate_keywords(text)
            
            # Content classification
            classification = await self.hf_client.classify_content_category(text)
            
            # Calculate risk score
            risk_score = self._calculate_text_risk_score(emotions, keyword_flags, classification)
            
            # Determine result
            if risk_score >= 0.8:
                result = ModerationResultEnum.BLOCKED
            elif risk_score >= 0.6:
                result = ModerationResultEnum.QUESTIONABLE
            else:
                result = ModerationResultEnum.SAFE
            
            return {
                "result": result,
                "risk_score": risk_score,
                "emotions": emotions,
                "flagged_keywords": keyword_flags,
                "classification": classification,
                "details": {
                    "text_length": len(text),
                    "word_count": len(text.split()),
                    "language_detected": "en"  # Placeholder
                }
            }
            
        except Exception as e:
            logger.error(f"Text moderation failed: {str(e)}")
            return {
                "result": ModerationResultEnum.SAFE,
                "risk_score": 0.0,
                "emotions": {},
                "flagged_keywords": [],
                "classification": {},
                "details": {"error": str(e)}
            }
    
    def _check_inappropriate_keywords(self, text: str) -> List[str]:
        """Check for inappropriate keywords in text"""
        text_lower = text.lower()
        flagged = []
        
        for keyword in self.inappropriate_keywords:
            if keyword in text_lower:
                flagged.append(keyword)
        
        return flagged
    
    def _calculate_text_risk_score(self, emotions: Dict, keywords: List, classification: Dict) -> float:
        """Calculate overall risk score for text"""
        score = 0.0
        
        # Check negative emotions
        anger_score = emotions.get("anger", 0)
        disgust_score = emotions.get("disgust", 0)
        
        if anger_score > 0.7 or disgust_score > 0.7:
            score += 0.3
        
        # Check flagged keywords
        if keywords:
            score += min(len(keywords) * 0.2, 0.5)
        
        # Check content category
        category = classification.get("primary_category", "")
        if category in ["adult", "explicit"]:
            score += 0.4
        
        return min(score, 1.0)

class ModerationService:
    def __init__(self):
        self.image_moderator = ImageModerationService()
        self.text_moderator = TextModerationService()
    
    async def moderate_content(self, content_id: int, user_id: int) -> Dict[str, Any]:
        """Main content moderation function"""
        try:
            with get_db_session() as db:
                from ..database.models import ContentItem
                content = db.query(ContentItem).filter(ContentItem.id == content_id).first()
                
                if not content:
                    raise ValueError(f"Content {content_id} not found")
                
                moderation_results = {}
                
                # Moderate image/video if available
                if content.file_path and Path(content.file_path).exists():
                    if content.content_type.value in ["image"]:
                        image_result = await self.image_moderator.moderate_image(content.file_path)
                        moderation_results["image"] = image_result
                    # Video moderation would go here
                
                # Moderate text content
                text_content = f"{content.title} {content.description or ''} {content.caption or ''}"
                if text_content.strip():
                    text_result = await self.text_moderator.moderate_text(text_content)
                    moderation_results["text"] = text_result
                
                # Combine results
                overall_result = self._combine_moderation_results(moderation_results)
                
                # Save to database
                moderation_record = ModerationResultModel(
                    content_item_id=content_id,
                    result=overall_result["result"],
                    nsfw_score=overall_result.get("nsfw_score", 0.0),
                    emotion_scores=overall_result.get("emotions", {}),
                    flagged_content=overall_result.get("flagged_content", []),
                    auto_moderated=True
                )
                
                db.add(moderation_record)
                db.commit()
                
                logger.info(f"Content {content_id} moderated: {overall_result['result'].value}")
                
                return overall_result
                
        except Exception as e:
            logger.error(f"Content moderation failed for {content_id}: {str(e)}")
            raise
    
    def _combine_moderation_results(self, results: Dict[str, Dict]) -> Dict[str, Any]:
        """Combine moderation results from different content types"""
        combined = {
            "result": ModerationResultEnum.SAFE,
            "nsfw_score": 0.0,
            "emotions": {},
            "flagged_content": [],
            "details": results
        }
        
        # Find highest risk result
        risk_levels = {
            ModerationResultEnum.SAFE: 0,
            ModerationResultEnum.QUESTIONABLE: 1,
            ModerationResultEnum.NSFW: 2,
            ModerationResultEnum.BLOCKED: 3
        }
        
        highest_risk = 0
        highest_result = ModerationResultEnum.SAFE
        
        for content_type, result in results.items():
            result_enum = result.get("result", ModerationResultEnum.SAFE)
            risk_level = risk_levels.get(result_enum, 0)
            
            if risk_level > highest_risk:
                highest_risk = risk_level
                highest_result = result_enum
            
            # Combine scores and flags
            if "nsfw_score" in result:
                combined["nsfw_score"] = max(combined["nsfw_score"], result["nsfw_score"])
            
            if "emotions" in result:
                combined["emotions"].update(result["emotions"])
            
            if "flagged_content" in result:
                combined["flagged_content"].extend(result["flagged_content"])
        
        combined["result"] = highest_result
        combined["flagged_content"] = list(set(combined["flagged_content"]))  # Remove duplicates
        
        return combined
