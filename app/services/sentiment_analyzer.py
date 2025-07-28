"""
Sentiment analysis service for Maya AI Content Optimization
"""

import re
from typing import Dict, List, Tuple
from collections import defaultdict


class SentimentAnalyzer:
    """Basic sentiment analysis service"""
    
    def __init__(self):
        # Simple sentiment lexicons
        self.positive_words = {
            "amazing", "awesome", "brilliant", "excellent", "fantastic", "great", "incredible", 
            "outstanding", "perfect", "wonderful", "love", "like", "enjoy", "happy", "excited",
            "thrilled", "delighted", "pleased", "satisfied", "impressed", "remarkable", "superb",
            "terrific", "fabulous", "marvelous", "spectacular", "phenomenal", "magnificent",
            "beautiful", "gorgeous", "stunning", "lovely", "charming", "elegant", "success",
            "achievement", "victory", "win", "triumph", "breakthrough", "progress", "growth",
            "opportunity", "advantage", "benefit", "value", "quality", "premium", "best",
            "top", "leading", "innovative", "creative", "inspiring", "motivating", "uplifting"
        }
        
        self.negative_words = {
            "awful", "terrible", "horrible", "disgusting", "hate", "dislike", "angry", "frustrated",
            "disappointed", "sad", "upset", "annoyed", "irritated", "furious", "outraged",
            "disgusted", "appalled", "shocked", "devastated", "heartbroken", "miserable",
            "depressed", "hopeless", "worthless", "useless", "pointless", "meaningless",
            "failure", "disaster", "catastrophe", "nightmare", "crisis", "problem", "issue",
            "trouble", "difficulty", "challenge", "obstacle", "barrier", "setback", "loss",
            "damage", "harm", "hurt", "pain", "suffering", "struggle", "fight", "battle",
            "conflict", "argument", "dispute", "disagreement", "criticism", "complaint",
            "fake", "fraud", "scam", "lie", "dishonest", "corrupt", "wrong", "bad", "poor",
            "worst", "inferior", "mediocre", "disappointing", "unsatisfactory"
        }
        
        self.neutral_words = {
            "okay", "fine", "average", "normal", "standard", "typical", "regular", "common",
            "ordinary", "basic", "simple", "plain", "neutral", "balanced", "moderate",
            "reasonable", "acceptable", "adequate", "sufficient", "decent", "fair"
        }
        
        # Sentiment modifiers
        self.intensifiers = {
            "very", "extremely", "incredibly", "absolutely", "completely", "totally", "really",
            "quite", "rather", "pretty", "fairly", "somewhat", "highly", "deeply", "truly",
            "genuinely", "seriously", "definitely", "certainly", "surely", "undoubtedly"
        }
        
        self.negators = {
            "not", "no", "never", "nothing", "nobody", "nowhere", "neither", "nor",
            "hardly", "barely", "scarcely", "seldom", "rarely", "without", "except"
        }
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of the given text"""
        # Clean and tokenize text
        clean_text = self._clean_text(text)
        words = clean_text.lower().split()
        
        # Calculate basic sentiment scores
        positive_score = 0
        negative_score = 0
        neutral_score = 0
        
        for i, word in enumerate(words):
            # Check for negation in the previous 2 words
            is_negated = self._is_negated(words, i)
            
            # Check for intensification in the previous 2 words
            intensifier = self._get_intensifier(words, i)
            multiplier = 1.5 if intensifier else 1.0
            
            # Score the word
            if word in self.positive_words:
                score = 1 * multiplier
                if is_negated:
                    negative_score += score
                else:
                    positive_score += score
            elif word in self.negative_words:
                score = 1 * multiplier
                if is_negated:
                    positive_score += score
                else:
                    negative_score += score
            elif word in self.neutral_words:
                neutral_score += 0.5
        
        # Calculate overall sentiment
        total_score = positive_score + negative_score + neutral_score
        
        if total_score == 0:
            sentiment_score = 0
            sentiment_label = "neutral"
        else:
            # Normalize to -100 to 100 scale
            raw_score = (positive_score - negative_score) / max(total_score, 1)
            sentiment_score = int(raw_score * 100)
            
            if sentiment_score > 20:
                sentiment_label = "positive"
            elif sentiment_score < -20:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"
        
        # Calculate confidence
        confidence = min(100, int((abs(sentiment_score) / 100) * 100))
        
        # Analyze emotional indicators
        emotions = self._analyze_emotions(text)
        
        # Detect potential issues
        issues = self._detect_content_issues(text)
        
        return {
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment_label,
            "confidence": confidence,
            "positive_score": round(positive_score, 2),
            "negative_score": round(negative_score, 2),
            "neutral_score": round(neutral_score, 2),
            "emotions": emotions,
            "issues": issues,
            "word_count": len(words),
            "analysis_details": {
                "positive_words_found": [w for w in words if w in self.positive_words],
                "negative_words_found": [w for w in words if w in self.negative_words],
                "intensifiers_found": [w for w in words if w in self.intensifiers],
                "negators_found": [w for w in words if w in self.negators]
            }
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean text for analysis"""
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove mentions and hashtags for sentiment analysis
        text = re.sub(r'[@#]\w+', '', text)
        
        # Remove extra whitespace and punctuation
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _is_negated(self, words: List[str], index: int) -> bool:
        """Check if the word at index is negated by previous words"""
        start = max(0, index - 2)
        for i in range(start, index):
            if words[i] in self.negators:
                return True
        return False
    
    def _get_intensifier(self, words: List[str], index: int) -> str:
        """Get intensifier before the current word if any"""
        start = max(0, index - 2)
        for i in range(start, index):
            if words[i] in self.intensifiers:
                return words[i]
        return None
    
    def _analyze_emotions(self, text: str) -> Dict:
        """Analyze specific emotions in the text"""
        text_lower = text.lower()
        
        emotions = {
            "joy": 0,
            "anger": 0,
            "fear": 0,
            "surprise": 0,
            "sadness": 0,
            "disgust": 0,
            "trust": 0,
            "anticipation": 0
        }
        
        # Joy indicators
        joy_words = ["happy", "joy", "excited", "thrilled", "delighted", "cheerful", "elated"]
        emotions["joy"] = sum(1 for word in joy_words if word in text_lower)
        
        # Anger indicators
        anger_words = ["angry", "furious", "mad", "irritated", "annoyed", "outraged", "frustrated"]
        emotions["anger"] = sum(1 for word in anger_words if word in text_lower)
        
        # Fear indicators
        fear_words = ["afraid", "scared", "worried", "anxious", "nervous", "terrified", "panic"]
        emotions["fear"] = sum(1 for word in fear_words if word in text_lower)
        
        # Surprise indicators
        surprise_words = ["surprised", "shocked", "amazed", "astonished", "wow", "unbelievable"]
        emotions["surprise"] = sum(1 for word in surprise_words if word in text_lower)
        
        # Sadness indicators
        sadness_words = ["sad", "depressed", "miserable", "heartbroken", "grief", "sorrow"]
        emotions["sadness"] = sum(1 for word in sadness_words if word in text_lower)
        
        # Trust indicators
        trust_words = ["trust", "reliable", "honest", "genuine", "authentic", "credible"]
        emotions["trust"] = sum(1 for word in trust_words if word in text_lower)
        
        return emotions
    
    def _detect_content_issues(self, text: str) -> List[str]:
        """Detect potential content issues"""
        issues = []
        text_lower = text.lower()
        
        # Check for excessive caps
        if sum(1 for c in text if c.isupper()) > len(text) * 0.3:
            issues.append("Excessive use of capital letters")
        
        # Check for excessive punctuation
        if text.count('!') > 3 or text.count('?') > 3:
            issues.append("Excessive punctuation")
        
        # Check for potential spam indicators
        spam_words = ["free", "win", "winner", "prize", "money", "cash", "urgent", "act now"]
        if sum(1 for word in spam_words if word in text_lower) > 2:
            issues.append("Potential spam indicators")
        
        # Simple negative sentiment check without recursion
        negative_word_count = sum(1 for word in text_lower.split() if word in self.negative_words)
        positive_word_count = sum(1 for word in text_lower.split() if word in self.positive_words)
        
        if negative_word_count > positive_word_count + 2:
            issues.append("Very negative sentiment detected")
        
        return issues
    
    def get_sentiment_recommendations(self, text: str) -> List[str]:
        """Get recommendations to improve sentiment"""
        analysis = self.analyze_sentiment(text)
        recommendations = []
        
        if analysis["sentiment_score"] < -20:
            recommendations.append("Consider adding more positive language")
            recommendations.append("Try to highlight benefits or solutions")
        
        if analysis["sentiment_score"] > 80:
            recommendations.append("Content has very positive sentiment - good for engagement!")
        
        if len(analysis["analysis_details"]["positive_words_found"]) == 0:
            recommendations.append("Consider adding some positive words to improve tone")
        
        if len(analysis["analysis_details"]["negative_words_found"]) > 3:
            recommendations.append("Consider reducing negative language")
        
        if analysis["confidence"] < 50:
            recommendations.append("Sentiment analysis confidence is low - consider clearer language")
        
        return recommendations