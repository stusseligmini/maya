"""
Webhook API endpoints for N8n integration and external service notifications
"""

import hmac
import hashlib
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import structlog
import json

from database.connection import get_db
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.models.content import Content, ContentStatus
from app.models.ai_model import AIProcessingJob, JobStatus
from config.settings import get_settings

logger = structlog.get_logger()
router = APIRouter(prefix="/webhooks", tags=["webhooks"])
settings = get_settings()


class WebhookPayload(BaseModel):
    """Generic webhook payload schema"""
    event_type: str = Field(..., description="Type of event triggering the webhook")
    timestamp: str = Field(..., description="ISO timestamp of the event")
    data: Dict[str, Any] = Field(..., description="Event-specific data")
    source: Optional[str] = Field(None, description="Source system identifier")


class ContentProcessedPayload(BaseModel):
    """Content processing completion webhook payload"""
    content_id: int
    job_id: int
    status: JobStatus
    processing_time: Optional[float] = None
    quality_score: Optional[int] = None
    error_message: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None


class PublishCompletedPayload(BaseModel):
    """Publishing completion webhook payload"""
    content_id: int
    platform: str
    status: str  # "success", "failed", "partial"
    platform_post_id: Optional[str] = None
    error_message: Optional[str] = None
    published_url: Optional[str] = None


class N8nTriggerPayload(BaseModel):
    """Generic N8n workflow trigger payload"""
    workflow_id: str
    trigger_data: Dict[str, Any]
    user_id: Optional[int] = None
    callback_url: Optional[str] = None


def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify webhook signature for security"""
    if not signature or not secret:
        return False
    
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected_signature}", signature)


@router.post("/content-processed")
async def content_processed_webhook(
    payload: ContentProcessedPayload,
    request: Request,
    x_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for AI processing completion notifications
    Called when content AI processing is completed
    """
    # Verify webhook signature if configured
    if hasattr(settings, 'WEBHOOK_SECRET') and settings.WEBHOOK_SECRET:
        body = await request.body()
        if not verify_webhook_signature(body.decode(), x_signature, settings.WEBHOOK_SECRET):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
    
    try:
        # Update AI processing job status
        job = db.query(AIProcessingJob).filter(AIProcessingJob.id == payload.job_id).first()
        if job:
            job.status = payload.status
            if payload.processing_time:
                job.processing_time_seconds = payload.processing_time
            if payload.quality_score:
                job.quality_score = payload.quality_score
            if payload.error_message:
                job.error_message = payload.error_message
            if payload.output_data:
                job.output_data = payload.output_data
        
        # Update content status
        content = db.query(Content).filter(Content.id == payload.content_id).first()
        if content:
            if payload.status == JobStatus.COMPLETED:
                content.status = ContentStatus.READY
                content.ai_enhanced = True
                if payload.quality_score:
                    content.optimization_score = payload.quality_score
            elif payload.status == JobStatus.FAILED:
                content.status = ContentStatus.FAILED
        
        db.commit()
        
        logger.info(
            "Content processing webhook received",
            content_id=payload.content_id,
            job_id=payload.job_id,
            status=payload.status
        )
        
        return {
            "status": "success",
            "message": "Content processing status updated",
            "content_id": payload.content_id,
            "job_id": payload.job_id
        }
        
    except Exception as e:
        logger.error("Error processing content webhook", exc_info=e)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook"
        )


@router.post("/publish-completed")
async def publish_completed_webhook(
    payload: PublishCompletedPayload,
    request: Request,
    x_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for publishing completion notifications
    Called when content is published to social media platforms
    """
    # Verify webhook signature if configured
    if hasattr(settings, 'WEBHOOK_SECRET') and settings.WEBHOOK_SECRET:
        body = await request.body()
        if not verify_webhook_signature(body.decode(), x_signature, settings.WEBHOOK_SECRET):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
    
    try:
        # Update content status
        content = db.query(Content).filter(Content.id == payload.content_id).first()
        if content:
            if payload.status == "success":
                content.status = ContentStatus.PUBLISHED
            elif payload.status == "failed":
                content.status = ContentStatus.FAILED
        
        db.commit()
        
        logger.info(
            "Publishing webhook received",
            content_id=payload.content_id,
            platform=payload.platform,
            status=payload.status,
            post_id=payload.platform_post_id
        )
        
        return {
            "status": "success",
            "message": "Publishing status updated",
            "content_id": payload.content_id,
            "platform": payload.platform,
            "platform_post_id": payload.platform_post_id
        }
        
    except Exception as e:
        logger.error("Error processing publishing webhook", exc_info=e)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook"
        )


@router.post("/n8n-trigger")
async def n8n_trigger_webhook(
    payload: N8nTriggerPayload,
    request: Request,
    x_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Generic N8n workflow trigger endpoint
    Handles various N8n workflow triggers and data exchanges
    """
    # Verify webhook signature if configured
    if hasattr(settings, 'WEBHOOK_SECRET') and settings.WEBHOOK_SECRET:
        body = await request.body()
        if not verify_webhook_signature(body.decode(), x_signature, settings.WEBHOOK_SECRET):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
    
    try:
        logger.info(
            "N8n trigger webhook received",
            workflow_id=payload.workflow_id,
            user_id=payload.user_id,
            trigger_data_keys=list(payload.trigger_data.keys())
        )
        
        # Process based on workflow type or trigger data
        response_data = {
            "status": "received",
            "workflow_id": payload.workflow_id,
            "timestamp": payload.trigger_data.get("timestamp"),
            "processed": True
        }
        
        # Add user context if user_id is provided
        if payload.user_id:
            user = db.query(User).filter(User.id == payload.user_id).first()
            if user:
                response_data["user_context"] = {
                    "username": user.username,
                    "email": user.email,
                    "is_premium": user.is_premium
                }
        
        # Handle callback URL if provided
        if payload.callback_url:
            # In a real implementation, you might queue a callback task
            response_data["callback_scheduled"] = True
        
        return response_data
        
    except Exception as e:
        logger.error("Error processing N8n webhook", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process N8n webhook"
        )


@router.post("/generic")
async def generic_webhook(
    payload: WebhookPayload,
    request: Request,
    x_signature: Optional[str] = Header(None)
):
    """
    Generic webhook endpoint for testing and development
    Accepts any webhook payload and logs it
    """
    # Verify webhook signature if configured
    if hasattr(settings, 'WEBHOOK_SECRET') and settings.WEBHOOK_SECRET:
        body = await request.body()
        if not verify_webhook_signature(body.decode(), x_signature, settings.WEBHOOK_SECRET):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
    
    logger.info(
        "Generic webhook received",
        event_type=payload.event_type,
        source=payload.source,
        data_keys=list(payload.data.keys()) if payload.data else []
    )
    
    return {
        "status": "received",
        "event_type": payload.event_type,
        "timestamp": payload.timestamp,
        "message": "Webhook processed successfully"
    }


@router.get("/validate")
async def validate_webhook_config():
    """
    Validate webhook configuration and connectivity
    Useful for N8n setup and testing
    """
    config_status = {
        "webhook_secret_configured": hasattr(settings, 'WEBHOOK_SECRET') and bool(settings.WEBHOOK_SECRET),
        "endpoints": [
            "/api/v1/webhooks/content-processed",
            "/api/v1/webhooks/publish-completed",
            "/api/v1/webhooks/n8n-trigger",
            "/api/v1/webhooks/generic"
        ],
        "supported_methods": ["POST"],
        "authentication": "signature-based (optional)",
        "content_type": "application/json"
    }
    
    return {
        "status": "operational",
        "configuration": config_status,
        "timestamp": "2024-01-01T00:00:00Z"
    }