"""
Content generation service for Maya AI Content Optimization
"""

import random
from typing import Dict, List, Optional
from datetime import datetime


class ContentGenerator:
    """AI-powered content generation service (mock implementation)"""
    
    def __init__(self):
        self.platform_templates = {
            "twitter": {
                "professional": [
                    "🎯 {topic}: {content} #Professional #Business",
                    "💡 Insight: {content} What's your take? #Thoughts #Discussion",
                    "🚀 {topic} update: {content} #Innovation #Growth",
                    "📈 {topic}: {content} #Success #Strategy"
                ],
                "casual": [
                    "Just thinking about {topic}... {content} 😊",
                    "Anyone else excited about {topic}? {content} 🔥",
                    "Random thought: {content} #JustSaying",
                    "{content} What do you think? 🤔"
                ],
                "promotional": [
                    "🌟 Excited to share: {content} #Announcement",
                    "🎉 Big news about {topic}: {content} #Launch",
                    "✨ New: {content} Check it out! #NewFeature",
                    "🚀 Launching: {content} #Innovation #Product"
                ]
            },
            "instagram": {
                "professional": [
                    "✨ {topic}\n\n{content}\n\nWhat's your experience with this? Share in the comments! 👇\n\n#Professional #Business #Growth #Success #Motivation",
                    "🎯 Focus on {topic}\n\n{content}\n\nDouble tap if you agree! ❤️\n\n#Strategy #Business #Entrepreneurship #Goals #Achievement",
                    "💡 {topic} insights:\n\n{content}\n\nSave this post for later! 📌\n\n#Knowledge #Learning #Professional #Development #Tips"
                ],
                "casual": [
                    "Hey everyone! 👋\n\n{content}\n\nWhat do you think about {topic}? Let me know! 💭\n\n#Life #Thoughts #Community #Sharing #Connection",
                    "Just had to share this about {topic}... ✨\n\n{content}\n\nWho else can relate? 🙋‍♀️\n\n#RealTalk #Authentic #Sharing #Community",
                    "Weekend vibes: thinking about {topic} 🌟\n\n{content}\n\nWhat's on your mind today? 💭\n\n#WeekendThoughts #Reflection #Life"
                ]
            },
            "linkedin": {
                "professional": [
                    "Insights on {topic}:\n\n{content}\n\nI'd love to hear your thoughts and experiences in the comments.\n\n#Professional #Industry #Growth #Leadership #Strategy",
                    "Key learnings about {topic}:\n\n{content}\n\nWhat has been your experience? Please share your perspective.\n\n#Learning #Development #Business #Innovation #Success",
                    "Reflecting on {topic}:\n\n{content}\n\nHow do you approach this in your organization?\n\n#Leadership #Management #Strategy #Best Practices"
                ]
            },
            "tiktok": {
                "casual": [
                    "POV: {content} #fyp #viral #trending",
                    "When {topic}: {content} #relatable #funny",
                    "Tell me you {content} without telling me #trend #viral"
                ]
            }
        }
        
        self.engagement_phrases = {
            "questions": [
                "What's your take on this?",
                "Have you experienced this too?",
                "What would you do?",
                "Am I the only one thinking this?",
                "What's your experience been?",
                "Thoughts?",
                "Agree or disagree?",
                "What do you think?",
                "Any similar experiences?",
                "How do you handle this?"
            ],
            "calls_to_action": [
                "Let me know in the comments!",
                "Share your thoughts below!",
                "Tag someone who needs to see this!",
                "Save this for later!",
                "Double tap if you agree!",
                "Follow for more tips!",
                "Share this with your network!",
                "What would you add to this list?",
                "Tell me your story!",
                "Join the conversation!"
            ]
        }
        
        self.trending_hashtags = {
            "general": ["#viral", "#trending", "#content", "#social", "#digital"],
            "business": ["#business", "#entrepreneur", "#startup", "#innovation", "#growth"],
            "tech": ["#technology", "#ai", "#digital", "#innovation", "#future"],
            "lifestyle": ["#lifestyle", "#wellness", "#motivation", "#inspiration", "#life"],
            "education": ["#learning", "#education", "#tips", "#knowledge", "#growth"]
        }
    
    def generate_content(
        self, 
        prompt: str, 
        platform: str = "twitter", 
        tone: str = "professional",
        topic: Optional[str] = None,
        include_hashtags: bool = True,
        include_engagement: bool = True
    ) -> Dict:
        """Generate content based on prompt and parameters"""
        
        # Process the prompt to extract key information
        processed_prompt = self._process_prompt(prompt)
        
        # Select appropriate template
        template = self._select_template(platform, tone)
        
        # Generate base content
        base_content = self._generate_base_content(processed_prompt, template, topic)
        
        # Add engagement elements
        if include_engagement:
            base_content = self._add_engagement_elements(base_content, platform)
        
        # Add hashtags
        if include_hashtags:
            hashtags = self._generate_hashtags(processed_prompt, platform)
            base_content = self._add_hashtags(base_content, hashtags, platform)
        
        # Calculate metrics
        metrics = self._calculate_content_metrics(base_content, platform)
        
        return {
            "generated_content": base_content,
            "platform": platform,
            "tone": tone,
            "metrics": metrics,
            "suggestions": self._generate_suggestions(base_content, platform),
            "hashtags_used": self._extract_hashtags(base_content),
            "estimated_engagement": metrics["engagement_score"],
            "character_count": len(base_content),
            "platform_optimized": metrics["platform_optimized"]
        }
    
    def generate_variations(self, content: str, platform: str, count: int = 3) -> List[Dict]:
        """Generate variations of existing content"""
        variations = []
        
        for i in range(count):
            # Create variation by modifying tone and structure
            tone = random.choice(["professional", "casual", "promotional"])
            
            # Generate new version
            variation = self.generate_content(
                prompt=content,
                platform=platform,
                tone=tone,
                include_hashtags=True,
                include_engagement=True
            )
            
            variation["variation_number"] = i + 1
            variations.append(variation)
        
        return variations
    
    def optimize_for_platform(self, content: str, source_platform: str, target_platform: str) -> Dict:
        """Optimize content from one platform for another"""
        # Extract core message
        core_message = self._extract_core_message(content)
        
        # Generate new version for target platform
        optimized = self.generate_content(
            prompt=core_message,
            platform=target_platform,
            tone="professional",
            include_hashtags=True,
            include_engagement=True
        )
        
        return {
            "original_content": content,
            "source_platform": source_platform,
            "target_platform": target_platform,
            "optimized_content": optimized["generated_content"],
            "optimization_changes": self._identify_optimization_changes(content, optimized["generated_content"]),
            "metrics": optimized["metrics"]
        }
    
    def _process_prompt(self, prompt: str) -> str:
        """Process and clean the input prompt"""
        # Remove excessive whitespace
        prompt = " ".join(prompt.split())
        
        # Ensure it ends with proper punctuation
        if not prompt.endswith(('.', '!', '?')):
            prompt += '.'
        
        return prompt
    
    def _select_template(self, platform: str, tone: str) -> str:
        """Select appropriate template for platform and tone"""
        templates = self.platform_templates.get(platform, {})
        tone_templates = templates.get(tone, templates.get("professional", []))
        
        if tone_templates:
            return random.choice(tone_templates)
        
        # Fallback template
        return "{content}"
    
    def _generate_base_content(self, prompt: str, template: str, topic: Optional[str] = None) -> str:
        """Generate base content using template"""
        if not topic:
            topic = self._extract_topic(prompt)
        
        # Fill in template
        content = template.format(
            content=prompt,
            topic=topic
        )
        
        return content
    
    def _extract_topic(self, prompt: str) -> str:
        """Extract main topic from prompt"""
        # Simple topic extraction - in a real implementation, this would use NLP
        words = prompt.lower().split()
        
        # Look for key nouns/topics
        topics = ["ai", "technology", "business", "marketing", "social media", "content", "strategy"]
        
        for topic in topics:
            if topic in " ".join(words):
                return topic.title()
        
        # Default topic
        return "Innovation"
    
    def _add_engagement_elements(self, content: str, platform: str) -> str:
        """Add engagement elements to content"""
        if platform in ["twitter", "instagram"]:
            # Add question or call to action
            if random.choice([True, False]):
                question = random.choice(self.engagement_phrases["questions"])
                content += f" {question}"
        
        return content
    
    def _generate_hashtags(self, content: str, platform: str) -> List[str]:
        """Generate relevant hashtags"""
        hashtags = []
        content_lower = content.lower()
        
        # Determine category
        if any(word in content_lower for word in ["business", "entrepreneur", "startup"]):
            hashtags.extend(random.sample(self.trending_hashtags["business"], 2))
        elif any(word in content_lower for word in ["ai", "tech", "digital"]):
            hashtags.extend(random.sample(self.trending_hashtags["tech"], 2))
        elif any(word in content_lower for word in ["life", "motivation", "inspiration"]):
            hashtags.extend(random.sample(self.trending_hashtags["lifestyle"], 2))
        else:
            hashtags.extend(random.sample(self.trending_hashtags["general"], 2))
        
        # Add platform-specific limits
        platform_limits = {
            "twitter": 3,
            "instagram": 8,
            "linkedin": 5,
            "tiktok": 5
        }
        
        max_hashtags = platform_limits.get(platform, 3)
        return hashtags[:max_hashtags]
    
    def _add_hashtags(self, content: str, hashtags: List[str], platform: str) -> str:
        """Add hashtags to content"""
        if not hashtags:
            return content
        
        hashtag_str = " ".join(hashtags)
        
        if platform == "instagram":
            # Instagram hashtags often go at the end
            content += f"\n\n{hashtag_str}"
        else:
            # Other platforms mix hashtags in content
            content += f" {hashtag_str}"
        
        return content
    
    def _calculate_content_metrics(self, content: str, platform: str) -> Dict:
        """Calculate content performance metrics"""
        char_count = len(content)
        word_count = len(content.split())
        hashtag_count = len(self._extract_hashtags(content))
        
        # Platform limits
        platform_limits = {
            "twitter": {"max_chars": 280, "ideal_chars": 250},
            "instagram": {"max_chars": 2200, "ideal_chars": 1000},
            "linkedin": {"max_chars": 3000, "ideal_chars": 1500},
            "tiktok": {"max_chars": 150, "ideal_chars": 100}
        }
        
        limits = platform_limits.get(platform, platform_limits["twitter"])
        
        # Calculate engagement score
        engagement_score = 50  # Base score
        
        # Length optimization
        if char_count <= limits["ideal_chars"]:
            engagement_score += 20
        elif char_count <= limits["max_chars"]:
            engagement_score += 10
        
        # Hashtag optimization
        if hashtag_count > 0:
            engagement_score += 15
        
        # Engagement elements
        if any(char in content for char in "?!"):
            engagement_score += 10
        
        platform_optimized = char_count <= limits["max_chars"]
        
        return {
            "character_count": char_count,
            "word_count": word_count,
            "hashtag_count": hashtag_count,
            "engagement_score": min(engagement_score, 100),
            "platform_optimized": platform_optimized,
            "readability_score": self._calculate_readability(content)
        }
    
    def _extract_hashtags(self, content: str) -> List[str]:
        """Extract hashtags from content"""
        import re
        return re.findall(r'#\w+', content)
    
    def _calculate_readability(self, content: str) -> int:
        """Calculate readability score"""
        words = content.split()
        if not words:
            return 0
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        sentences = [s for s in content.split('.') if s.strip()]
        avg_sentence_length = len(words) / len(sentences) if sentences else len(words)
        
        # Simple readability (higher is better)
        score = 100 - (avg_word_length * 3) - (avg_sentence_length * 1.5)
        return max(0, min(100, int(score)))
    
    def _generate_suggestions(self, content: str, platform: str) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        char_count = len(content)
        platform_limits = {
            "twitter": 280,
            "instagram": 2200,
            "linkedin": 3000,
            "tiktok": 150
        }
        
        limit = platform_limits.get(platform, 280)
        
        if char_count > limit:
            suggestions.append(f"Content exceeds {platform} character limit ({char_count}/{limit})")
        
        if not self._extract_hashtags(content):
            suggestions.append("Consider adding relevant hashtags for better discoverability")
        
        if "?" not in content and "!" not in content:
            suggestions.append("Consider adding a question or exclamation for better engagement")
        
        return suggestions
    
    def _extract_core_message(self, content: str) -> str:
        """Extract core message from content"""
        # Remove hashtags and mentions for core message
        import re
        clean_content = re.sub(r'[#@]\w+', '', content)
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        
        # Return first sentence or first 100 characters
        sentences = clean_content.split('.')
        if sentences and len(sentences[0]) > 10:
            return sentences[0].strip()
        
        return clean_content[:100] + "..." if len(clean_content) > 100 else clean_content
    
    def _identify_optimization_changes(self, original: str, optimized: str) -> List[str]:
        """Identify what changed during optimization"""
        changes = []
        
        if len(optimized) != len(original):
            changes.append(f"Length changed from {len(original)} to {len(optimized)} characters")
        
        original_hashtags = len(self._extract_hashtags(original))
        optimized_hashtags = len(self._extract_hashtags(optimized))
        
        if original_hashtags != optimized_hashtags:
            changes.append(f"Hashtags changed from {original_hashtags} to {optimized_hashtags}")
        
        if "?" in optimized and "?" not in original:
            changes.append("Added engagement question")
        
        return changes