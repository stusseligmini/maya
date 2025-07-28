"""Unit tests for Maya core functionality."""

import pytest
from datetime import datetime
from maya.core.exceptions import ValidationError, ContentProcessingError
from maya.content.processor import ContentItem, ContentType, ContentProcessor, Platform
from maya.security.auth import PasswordValidator, InputValidator, JWTManager
from maya.config.settings import Settings


class TestContentProcessor:
    """Test content processing functionality."""
    
    def test_content_item_creation(self):
        """Test creating a content item."""
        content = ContentItem(
            id="test_123",
            content_type=ContentType.TEXT,
            text="Test content",
            hashtags=["test", "maya"],
            mentions=["@testuser"]
        )
        
        assert content.id == "test_123"
        assert content.content_type == ContentType.TEXT
        assert content.text == "Test content"
        assert content.hashtags == ["test", "maya"]
        assert content.mentions == ["@testuser"]
        assert isinstance(content.created_at, datetime)
    
    def test_content_item_auto_id(self):
        """Test auto-generation of content ID."""
        content = ContentItem(
            id=None,
            content_type=ContentType.TEXT,
            text="Test content"
        )
        
        assert content.id is not None
        assert len(content.id) == 32  # MD5 hash length
    
    @pytest.mark.asyncio
    async def test_content_processing(self):
        """Test basic content processing."""
        processor = ContentProcessor()
        
        content = ContentItem(
            id="test_process",
            content_type=ContentType.TEXT,
            text="This is a test post for social media optimization!"
        )
        
        platforms = [Platform.TWITTER, Platform.INSTAGRAM]
        
        result = await processor.process_content(content, platforms, analyze_with_ai=False)
        
        assert result.original_content.id == "test_process"
        assert result.optimized_content is not None
        assert len(result.platform_specific) == 2
        assert Platform.TWITTER in result.platform_specific
        assert Platform.INSTAGRAM in result.platform_specific
        assert isinstance(result.processing_time, float)
        assert result.processing_time > 0


class TestSecurityAuth:
    """Test security and authentication functionality."""
    
    def test_password_validator(self):
        """Test password validation."""
        validator = PasswordValidator()
        
        # Test weak password
        weak_issues = validator.validate_password("123")
        assert len(weak_issues) > 0
        assert any("8 characters" in issue for issue in weak_issues)
        
        # Test strong password
        strong_issues = validator.validate_password("StrongPass123!")
        assert len(strong_issues) == 0
        
        # Test common pattern
        common_issues = validator.validate_password("Password123!")
        assert any("common patterns" in issue for issue in common_issues)
    
    def test_input_validator(self):
        """Test input validation."""
        validator = InputValidator()
        
        # Test email validation
        assert validator.validate_email("test@example.com") is True
        assert validator.validate_email("invalid-email") is False
        assert validator.validate_email("test@") is False
        
        # Test username validation
        username_issues = validator.validate_username("ab")
        assert any("3 characters" in issue for issue in username_issues)
        
        valid_issues = validator.validate_username("validuser123")
        assert len(valid_issues) == 0
        
        invalid_issues = validator.validate_username("invalid@user")
        assert len(invalid_issues) > 0
    
    def test_input_sanitization(self):
        """Test input sanitization."""
        validator = InputValidator()
        
        # Test script removal
        malicious = "<script>alert('xss')</script>Hello world"
        sanitized = validator.sanitize_input(malicious)
        assert "<script>" not in sanitized
        assert "Hello world" in sanitized
        
        # Test length limiting
        long_text = "A" * 2000
        sanitized = validator.sanitize_input(long_text, max_length=100)
        assert len(sanitized) == 100
    
    def test_jwt_token_creation_and_verification(self):
        """Test JWT token creation and verification."""
        # Note: This test assumes a default secret key is set
        import os
        os.environ["SECRET_KEY"] = "test-secret-key-at-least-32-characters-long"
        
        jwt_manager = JWTManager()
        
        # Create token
        token = jwt_manager.create_access_token(
            user_id="test_user",
            username="testuser",
            email="test@example.com",
            scopes=["read", "write"]
        )
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token
        token_data = jwt_manager.verify_token(token)
        
        assert token_data.user_id == "test_user"
        assert token_data.username == "testuser"
        assert token_data.email == "test@example.com"
        assert "read" in token_data.scopes
        assert "write" in token_data.scopes


class TestConfiguration:
    """Test configuration management."""
    
    def test_settings_creation(self):
        """Test settings creation with defaults."""
        settings = Settings()
        
        assert settings.app_name == "Maya AI Content System"
        assert settings.debug is False
        assert settings.environment == "development"
        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 8000
    
    def test_database_settings(self):
        """Test database configuration."""
        settings = Settings()
        
        assert settings.database.pool_size == 10
        assert settings.database.max_overflow == 20
        assert "postgresql" in settings.database.url
    
    def test_security_settings(self):
        """Test security configuration."""
        import os
        os.environ["SECRET_KEY"] = "test-secret-key-at-least-32-characters-long"
        
        settings = Settings()
        
        assert settings.security.algorithm == "HS256"
        assert settings.security.access_token_expire_minutes == 30
        assert len(settings.security.secret_key) >= 32


class TestExceptions:
    """Test custom exception handling."""
    
    def test_validation_error(self):
        """Test ValidationError exception."""
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError("Test validation error")
        
        assert "Test validation error" in str(exc_info.value)
    
    def test_content_processing_error(self):
        """Test ContentProcessingError exception."""
        with pytest.raises(ContentProcessingError) as exc_info:
            raise ContentProcessingError("Test processing error")
        
        assert "Test processing error" in str(exc_info.value)


class TestContentValidation:
    """Test content validation for different platforms."""
    
    def test_twitter_text_limit(self):
        """Test Twitter text length validation."""
        from maya.content.processor import ContentValidator
        
        validator = ContentValidator()
        
        # Test valid content
        valid_content = ContentItem(
            id="test",
            content_type=ContentType.TEXT,
            text="Short tweet"
        )
        
        issues = validator.validate_content(valid_content, Platform.TWITTER)
        assert len(issues) == 0
        
        # Test content exceeding limit
        long_content = ContentItem(
            id="test",
            content_type=ContentType.TEXT,
            text="A" * 300  # Exceeds Twitter's 280 character limit
        )
        
        issues = validator.validate_content(long_content, Platform.TWITTER)
        assert len(issues) > 0
        assert any("280 characters" in issue for issue in issues)
    
    def test_instagram_media_validation(self):
        """Test Instagram media validation."""
        from maya.content.processor import ContentValidator
        
        validator = ContentValidator()
        
        # Test too many images
        many_images_content = ContentItem(
            id="test",
            content_type=ContentType.MIXED,
            text="Test post",
            media_urls=[f"image{i}.jpg" for i in range(15)]  # Exceeds Instagram's 10 image limit
        )
        
        issues = validator.validate_content(many_images_content, Platform.INSTAGRAM)
        assert len(issues) > 0
        assert any("Too many images" in issue for issue in issues)


if __name__ == "__main__":
    pytest.main([__file__])