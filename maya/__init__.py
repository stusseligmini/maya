"""
Maya AI Content Optimization System

A comprehensive AI system for optimizing content across social media platforms.
"""

__version__ = "0.1.0"
__author__ = "Maya Team"

# Core services
from maya.core.config import get_settings
from maya.core.logging import LoggerMixin
from maya.core.exceptions import (
    MayaBaseException, 
    ServiceError, 
    AuthenticationError, 
    ContentProcessingError,
    AIModelError,
)

# AI services
from maya.ai.models import (
    BaseAIModel,
    OpenAIIntegration,
    HuggingFaceIntegration,
    AIModelManager,
    ai_manager
)

# Content services
from maya.content.processor import (
    ContentType,
    Platform,
    ContentItem,
    ProcessingResult,
    ContentValidator,
    ContentOptimizer,
    ContentProcessor
)

# Security services
from maya.security.auth import get_current_user

# Unified services
from maya.services.services import (
    AIService,
    PlatformService,
    ai_service,
    content_service,
    platform_service
)

# Worker services
from maya.worker.worker import (
    TaskWorker,
    WorkerManager,
    worker_manager
)

# API
from maya.api.routes import router as api_router

__all__ = [
    # Core
    'get_settings',
    'LoggerMixin',
    'MayaBaseException',
    'ServiceError',
    'AuthenticationError',
    'ContentProcessingError',
    'AIModelError',
    'WorkerError',
    
    # AI
    'BaseAIModel',
    'OpenAIIntegration',
    'HuggingFaceIntegration',
    'AIModelManager',
    'ai_manager',
    
    # Content
    'ContentType',
    'Platform',
    'ContentItem',
    'ProcessingResult',
    'ContentValidator',
    'ContentOptimizer',
    'ContentProcessor',
    
    # Security
    'get_current_user',
    'create_access_token',
    'verify_token',
    # 'authenticate_user',  # Not defined in maya.security.auth
    # 'User',  # User is not defined here; import from app.models.user where needed
    
    # Services
    'AIService',
    'ContentService',
    'PlatformService',
    'ai_service',
    'content_service',
    'platform_service',
    
    # Worker
    'TaskWorker',
    'WorkerManager',
    'worker_manager',
    
    # API
    'api_router'
]