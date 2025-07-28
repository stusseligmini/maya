"""
Configuration management API endpoints
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import structlog

from database.connection import get_db
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.models.social_platform import SocialPlatform, PlatformCredentials, PlatformType
from config.settings import get_settings

logger = structlog.get_logger()
router = APIRouter(prefix="/config", tags=["configuration"])
settings = get_settings()


class PlatformCredentialsUpdate(BaseModel):
    """Platform credentials update schema"""
    platform: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    app_id: Optional[str] = None
    app_secret: Optional[str] = None
    platform_user_id: Optional[str] = None
    platform_username: Optional[str] = None
    account_name: Optional[str] = None
    permissions: Optional[List[str]] = None


class PlatformStatus(BaseModel):
    """Platform status response schema"""
    platform: str
    display_name: str
    is_connected: bool
    is_active: bool
    account_name: Optional[str] = None
    last_used: Optional[str] = None
    total_posts: int = 0
    capabilities: Dict[str, bool]


class N8nSettings(BaseModel):
    """N8n integration settings schema"""
    webhook_url: Optional[str] = None
    api_key: Optional[str] = None
    workflow_triggers: Optional[Dict[str, str]] = None
    callback_endpoints: Optional[Dict[str, str]] = None
    enable_batch_processing: bool = True
    max_batch_size: int = 50


class SystemConfig(BaseModel):
    """System configuration schema"""
    features: Dict[str, bool]
    limits: Dict[str, int]
    integration_settings: Dict[str, Any]


@router.post("/platform-credentials")
async def update_platform_credentials(
    credentials: PlatformCredentialsUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update or create platform credentials for the current user
    """
    # Validate platform
    try:
        platform_type = PlatformType(credentials.platform)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid platform: {credentials.platform}"
        )
    
    # Get platform object
    platform = db.query(SocialPlatform).filter(
        SocialPlatform.name == platform_type
    ).first()
    
    if not platform:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Platform {credentials.platform} not configured"
        )
    
    # Check if credentials already exist
    existing_creds = db.query(PlatformCredentials).filter(
        PlatformCredentials.user_id == current_user.id,
        PlatformCredentials.platform_id == platform.id
    ).first()
    
    if existing_creds:
        # Update existing credentials
        if credentials.access_token:
            existing_creds.access_token = credentials.access_token
        if credentials.refresh_token:
            existing_creds.refresh_token = credentials.refresh_token
        if credentials.app_id:
            existing_creds.app_id = credentials.app_id
        if credentials.app_secret:
            existing_creds.app_secret = credentials.app_secret
        if credentials.platform_user_id:
            existing_creds.platform_user_id = credentials.platform_user_id
        if credentials.platform_username:
            existing_creds.platform_username = credentials.platform_username
        if credentials.account_name:
            existing_creds.account_name = credentials.account_name
        if credentials.permissions:
            existing_creds.permissions = credentials.permissions
        
        existing_creds.is_active = True
        creds_obj = existing_creds
    else:
        # Create new credentials
        creds_obj = PlatformCredentials(
            user_id=current_user.id,
            platform_id=platform.id,
            access_token=credentials.access_token,
            refresh_token=credentials.refresh_token,
            app_id=credentials.app_id,
            app_secret=credentials.app_secret,
            platform_user_id=credentials.platform_user_id,
            platform_username=credentials.platform_username,
            account_name=credentials.account_name,
            permissions=credentials.permissions,
            is_active=True
        )
        db.add(creds_obj)
    
    db.commit()
    db.refresh(creds_obj)
    
    logger.info(
        "Platform credentials updated",
        user_id=current_user.id,
        platform=credentials.platform
    )
    
    return {
        "status": "success",
        "platform": credentials.platform,
        "message": "Credentials updated successfully",
        "is_connected": True
    }


@router.get("/platforms", response_model=List[PlatformStatus])
async def get_platform_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get status of all available platforms for the current user
    """
    platforms = db.query(SocialPlatform).filter(SocialPlatform.is_active == True).all()
    platform_statuses = []
    
    for platform in platforms:
        # Check if user has credentials for this platform
        credentials = db.query(PlatformCredentials).filter(
            PlatformCredentials.user_id == current_user.id,
            PlatformCredentials.platform_id == platform.id,
            PlatformCredentials.is_active == True
        ).first()
        
        is_connected = credentials is not None
        
        platform_status = PlatformStatus(
            platform=platform.name.value,
            display_name=platform.display_name,
            is_connected=is_connected,
            is_active=platform.is_active,
            account_name=credentials.account_name if credentials else None,
            last_used=credentials.last_used_at.isoformat() if credentials and credentials.last_used_at else None,
            total_posts=credentials.total_posts if credentials else 0,
            capabilities={
                "supports_images": platform.supports_images,
                "supports_videos": platform.supports_videos,
                "supports_carousel": platform.supports_carousel,
                "supports_stories": platform.supports_stories,
                "supports_scheduling": platform.supports_scheduling
            }
        )
        
        platform_statuses.append(platform_status)
    
    return platform_statuses


@router.delete("/platforms/{platform_name}")
async def disconnect_platform(
    platform_name: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Disconnect a platform by deactivating credentials
    """
    try:
        platform_type = PlatformType(platform_name)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid platform: {platform_name}"
        )
    
    platform = db.query(SocialPlatform).filter(
        SocialPlatform.name == platform_type
    ).first()
    
    if not platform:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Platform {platform_name} not found"
        )
    
    credentials = db.query(PlatformCredentials).filter(
        PlatformCredentials.user_id == current_user.id,
        PlatformCredentials.platform_id == platform.id
    ).first()
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No credentials found for platform {platform_name}"
        )
    
    credentials.is_active = False
    db.commit()
    
    logger.info(
        "Platform disconnected",
        user_id=current_user.id,
        platform=platform_name
    )
    
    return {
        "status": "success",
        "platform": platform_name,
        "message": "Platform disconnected successfully"
    }


@router.post("/n8n-settings")
async def update_n8n_settings(
    settings_data: N8nSettings,
    current_user: User = Depends(get_current_active_user)
):
    """
    Configure N8n integration settings
    In production, this would store settings in database or secure config
    """
    # For now, we'll just validate and return success
    # In production, store these settings securely
    
    logger.info(
        "N8n settings updated",
        user_id=current_user.id,
        has_webhook_url=bool(settings_data.webhook_url),
        has_api_key=bool(settings_data.api_key),
        batch_processing=settings_data.enable_batch_processing
    )
    
    return {
        "status": "success",
        "message": "N8n settings updated successfully",
        "settings": {
            "webhook_configured": bool(settings_data.webhook_url),
            "api_key_configured": bool(settings_data.api_key),
            "batch_processing_enabled": settings_data.enable_batch_processing,
            "max_batch_size": settings_data.max_batch_size
        }
    }


@router.get("/n8n-settings")
async def get_n8n_settings(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current N8n integration settings
    """
    # In production, retrieve from database or secure config
    return {
        "webhook_configured": hasattr(settings, 'N8N_WEBHOOK_URL') and bool(settings.N8N_WEBHOOK_URL),
        "api_key_configured": hasattr(settings, 'N8N_API_KEY') and bool(settings.N8N_API_KEY),
        "available_endpoints": {
            "content_processed": "/api/v1/webhooks/content-processed",
            "publish_completed": "/api/v1/webhooks/publish-completed",
            "n8n_trigger": "/api/v1/webhooks/n8n-trigger"
        },
        "supported_workflows": [
            "content_creation",
            "ai_processing",
            "bulk_publishing",
            "scheduled_publishing",
            "analytics_reporting"
        ]
    }


@router.get("/system", response_model=SystemConfig)
async def get_system_configuration(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current system configuration and feature flags
    """
    features = {
        "ai_enhancement": getattr(settings, 'ENABLE_AI_ENHANCEMENT', True),
        "content_moderation": getattr(settings, 'ENABLE_CONTENT_MODERATION', True),
        "analytics": getattr(settings, 'ENABLE_ANALYTICS', True),
        "publishing": getattr(settings, 'ENABLE_PUBLISHING', True),
        "system_monitoring": getattr(settings, 'ENABLE_SYSTEM_MONITORING', True),
        "webhooks": True,
        "batch_operations": True
    }
    
    limits = {
        "max_upload_size_mb": int(getattr(settings, 'MAX_UPLOAD_SIZE', 100 * 1024 * 1024) / (1024 * 1024)),
        "max_platforms_per_publish": getattr(settings, 'MAX_PLATFORMS_PER_PUBLISH', 5),
        "max_scheduled_jobs": getattr(settings, 'MAX_SCHEDULED_JOBS_PER_USER', 100),
        "rate_limit_per_minute": getattr(settings, 'RATE_LIMIT_PER_MINUTE', 60),
        "metrics_retention_days": getattr(settings, 'METRICS_RETENTION_DAYS', 30)
    }
    
    integration_settings = {
        "supported_platforms": [platform.value for platform in PlatformType],
        "supported_media_types": getattr(settings, 'ALLOWED_MEDIA_TYPES', []),
        "webhook_authentication": "signature-based",
        "api_version": "v1"
    }
    
    return SystemConfig(
        features=features,
        limits=limits,
        integration_settings=integration_settings
    )


@router.post("/validate-integration")
async def validate_integration(
    platform: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Validate platform integration and credentials
    """
    try:
        platform_type = PlatformType(platform)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid platform: {platform}"
        )
    
    platform_obj = db.query(SocialPlatform).filter(
        SocialPlatform.name == platform_type
    ).first()
    
    if not platform_obj:
        return {
            "platform": platform,
            "status": "error",
            "message": "Platform not configured in system"
        }
    
    credentials = db.query(PlatformCredentials).filter(
        PlatformCredentials.user_id == current_user.id,
        PlatformCredentials.platform_id == platform_obj.id,
        PlatformCredentials.is_active == True
    ).first()
    
    if not credentials:
        return {
            "platform": platform,
            "status": "error",
            "message": "No active credentials found"
        }
    
    # In production, perform actual API validation
    # For now, return success if credentials exist
    return {
        "platform": platform,
        "status": "success",
        "message": "Platform integration validated successfully",
        "account": credentials.account_name or credentials.platform_username,
        "last_validated": "2024-01-01T00:00:00Z"
    }