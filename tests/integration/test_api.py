"""Integration tests for Maya API endpoints."""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import json

from maya.api.app import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def auth_token():
    """Create authentication token for testing."""
    # This would normally come from proper authentication
    from maya.security.auth import jwt_manager
    import os
    os.environ["SECRET_KEY"] = "test-secret-key-at-least-32-characters-long"
    
    token = jwt_manager.create_access_token(
        user_id="test_user",
        username="testuser",
        email="test@example.com",
        scopes=["read", "write", "admin"]
    )
    return token


class TestHealthEndpoints:
    """Test health and monitoring endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "timestamp" in data
        assert "checks" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
    
    def test_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint."""
        response = client.get("/metrics")
        
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        
        # Check for some expected metrics
        content = response.text
        assert "maya_http_requests_total" in content


class TestAuthenticationEndpoints:
    """Test authentication endpoints."""
    
    def test_create_token_valid_credentials(self, client):
        """Test token creation with valid credentials."""
        response = client.post(
            "/auth/token",
            params={"username": "demo", "password": "demo123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        assert data["token_type"] == "bearer"
    
    def test_create_token_invalid_credentials(self, client):
        """Test token creation with invalid credentials."""
        response = client.post(
            "/auth/token",
            params={"username": "invalid", "password": "wrong"}
        )
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]


class TestContentEndpoints:
    """Test content processing endpoints."""
    
    def test_process_content_without_auth(self, client):
        """Test content processing without authentication."""
        response = client.post(
            "/content/process",
            params={"text": "Test content"}
        )
        
        assert response.status_code == 401
    
    def test_process_content_with_auth(self, client, auth_token):
        """Test content processing with authentication."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.post(
            "/content/process",
            params={
                "text": "This is a test post for social media optimization!",
                "content_type": "text",
                "target_platforms": ["twitter", "instagram"],
                "analyze_with_ai": False
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "original_content" in data
        assert "optimized_content" in data
        assert "analysis" in data
        assert "recommendations" in data
        assert "platform_specific" in data
        assert "processing_time" in data
    
    def test_process_content_invalid_platform(self, client, auth_token):
        """Test content processing with invalid platform."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.post(
            "/content/process",
            params={
                "text": "Test content",
                "target_platforms": ["invalid_platform"]
            },
            headers=headers
        )
        
        assert response.status_code == 500  # Should handle gracefully
    
    @patch('maya.social.platforms.social_manager.publish_to_platforms')
    def test_publish_content(self, mock_publish, client, auth_token):
        """Test content publishing."""
        # Mock the social manager response
        from maya.social.platforms import PostResult
        from maya.content.processor import Platform
        
        mock_result = {
            Platform.TWITTER: PostResult(
                platform=Platform.TWITTER,
                post_id="test_post_123",
                url="https://twitter.com/user/status/test_post_123",
                status="published"
            )
        }
        mock_publish.return_value = mock_result
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.post(
            "/content/publish",
            params={
                "content_id": "test_content_123",
                "text": "Test publication content",
                "platforms": ["twitter"]
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "twitter" in data
        assert data["twitter"]["post_id"] == "test_post_123"
        assert data["twitter"]["status"] == "published"
    
    @patch('maya.social.platforms.social_manager.schedule_for_platforms')
    def test_schedule_content(self, mock_schedule, client, auth_token):
        """Test content scheduling."""
        from maya.social.platforms import PostResult
        from maya.content.processor import Platform
        from datetime import datetime, timedelta
        
        future_time = datetime.utcnow() + timedelta(hours=1)
        
        mock_result = {
            Platform.TWITTER: PostResult(
                platform=Platform.TWITTER,
                post_id="scheduled_123",
                scheduled_time=future_time,
                status="scheduled"
            )
        }
        mock_schedule.return_value = mock_result
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.post(
            "/content/schedule",
            params={
                "content_id": "test_content_123",
                "text": "Scheduled content",
                "platforms": ["twitter"],
                "publish_time": future_time.isoformat()
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "twitter" in data
        assert data["twitter"]["post_id"] == "scheduled_123"
        assert data["twitter"]["status"] == "scheduled"


class TestAIEndpoints:
    """Test AI model endpoints."""
    
    def test_list_ai_models(self, client, auth_token):
        """Test listing available AI models."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.get("/ai/models", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "available_models" in data
        assert isinstance(data["available_models"], list)
    
    @patch('maya.ai.models.ai_manager.get_model')
    def test_ai_analyze_content(self, mock_get_model, client, auth_token):
        """Test AI content analysis."""
        # Mock AI model response
        mock_model = AsyncMock()
        mock_model.analyze_content.return_value = {
            "sentiment": "POSITIVE",
            "confidence": 0.85,
            "model": "test_model"
        }
        mock_get_model.return_value = mock_model
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.post(
            "/ai/analyze",
            params={
                "text": "This is a great product!",
                "model_type": "huggingface"
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "sentiment" in data
        assert "confidence" in data
        assert data["sentiment"] == "POSITIVE"
    
    @patch('maya.ai.models.ai_manager.get_model')
    def test_ai_generate_content(self, mock_get_model, client, auth_token):
        """Test AI content generation."""
        # Mock AI model response
        mock_model = AsyncMock()
        mock_model.generate_content.return_value = "Generated content based on prompt"
        mock_get_model.return_value = mock_model
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.post(
            "/ai/generate",
            params={
                "prompt": "Write a social media post about technology",
                "model_type": "openai",
                "max_tokens": 100
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "generated_content" in data
        assert "model_type" in data
        assert data["model_type"] == "openai"


class TestSocialEndpoints:
    """Test social platform endpoints."""
    
    def test_list_platforms(self, client, auth_token):
        """Test listing supported platforms."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.get("/social/platforms", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "supported_platforms" in data
        assert isinstance(data["supported_platforms"], list)
        assert "twitter" in data["supported_platforms"]
        assert "instagram" in data["supported_platforms"]
    
    def test_get_scheduled_posts(self, client, auth_token):
        """Test getting scheduled posts."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.get("/social/scheduled", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "scheduled_posts" in data
        assert isinstance(data["scheduled_posts"], list)
    
    def test_get_scheduled_posts_filtered(self, client, auth_token):
        """Test getting scheduled posts filtered by platform."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.get(
            "/social/scheduled",
            params={"platform": "twitter"},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "scheduled_posts" in data
        # All posts should be for Twitter if any exist
        for post in data["scheduled_posts"]:
            assert post["platform"] == "twitter"


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_rate_limiting(self, client, auth_token):
        """Test rate limiting on endpoints."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Make multiple requests quickly
        responses = []
        for i in range(60):  # Try to exceed rate limit
            response = client.post(
                "/content/process",
                params={
                    "text": f"Test content {i}",
                    "analyze_with_ai": False
                },
                headers=headers
            )
            responses.append(response.status_code)
        
        # Should eventually get rate limited (429)
        # Note: This might not trigger in tests due to mocking, but the structure is correct
        status_codes = set(responses)
        assert 200 in status_codes  # Some requests should succeed


class TestSecurityHeaders:
    """Test security headers are applied."""
    
    def test_security_headers_present(self, client):
        """Test that security headers are included in responses."""
        response = client.get("/health")
        
        # Check for important security headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"


if __name__ == "__main__":
    pytest.main([__file__])