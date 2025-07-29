"""
n8n integration module for Maya system.

This module provides webhooks, actions and triggers for n8n integration,
allowing Maya to be used in automated workflows.
"""

import json
import hmac
import hashlib
import time
import uuid
from typing import Dict, Any, List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status, Body, Request, Header
from fastapi.responses import JSONResponse

import structlog
from datetime import datetime

from maya.core.config import get_settings
from maya.core.exceptions import ServiceError, AuthenticationError
from maya.security.auth import get_current_user, User
from maya.services.services import ai_service, content_service, platform_service
from maya.worker.worker import worker_manager

logger = structlog.get_logger()
settings = get_settings()

# Create router with prefix
router = APIRouter(prefix="/n8n", tags=["n8n"])


def verify_webhook_signature(request_body: bytes, signature: str, secret: str) -> bool:
    """Verify the webhook signature from n8n."""
    if not signature or not secret:
        return False
    
    # Create expected signature
    expected_signature = hmac.new(
        secret.encode(), 
        request_body, 
        hashlib.sha256
    ).hexdigest()
    
    # Constant time comparison to prevent timing attacks
    return hmac.compare_digest(expected_signature, signature)


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def n8n_webhook(
    request: Request,
    x_n8n_signature: Optional[str] = Header(None)
):
    """
    Webhook endpoint for n8n integration.
    
    This allows n8n to trigger Maya processes via webhooks.
    """
    # Get webhook secret from settings
    webhook_secret = settings.integrations.n8n_webhook_secret
    
    # Read request body
    body = await request.body()
    
    # Verify signature if configured
    if webhook_secret and x_n8n_signature:
        if not verify_webhook_signature(body, x_n8n_signature, webhook_secret):
            logger.warning("Invalid n8n webhook signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
    
    try:
        # Parse JSON body
        payload = json.loads(body)
        
        # Get action type
        action = payload.get("action", "process_content")
        
        # Process based on action type
        if action == "process_content":
            result = await process_content_webhook(payload)
        elif action == "generate_content":
            result = await generate_content_webhook(payload)
        elif action == "analyze_content":
            result = await analyze_content_webhook(payload)
        else:
            logger.warning(f"Unknown n8n webhook action: {action}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": f"Unknown action: {action}"}
            )
        
        return result
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in n8n webhook payload")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Invalid JSON payload"}
        )
    except Exception as e:
        logger.error(f"Error processing n8n webhook: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)}
        )


async def process_content_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process content webhook from n8n."""
    try:
        # Extract content data
        content_data = payload.get("content_data", {})
        target_platforms = payload.get("target_platforms", ["twitter", "instagram"])
        analyze_with_ai = payload.get("analyze_with_ai", True)
        
        if not content_data:
            raise ValueError("No content data provided")
        
        # Process content
        result = await content_service.process_content(
            content_data,
            target_platforms=target_platforms,
            analyze_with_ai=analyze_with_ai
        )
        
        # Return processed content
        return {
            "success": True,
            "processed_content": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Content processing webhook failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


async def generate_content_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate content webhook from n8n."""
    try:
        # Extract generation parameters
        prompt = payload.get("prompt")
        model_type = payload.get("model_type", "openai")
        max_tokens = payload.get("max_tokens", 150)
        temperature = payload.get("temperature", 0.7)
        
        if not prompt:
            raise ValueError("No prompt provided")
        
        # Generate content
        result = await ai_service.generate_content(
            prompt,
            model_type=model_type,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Return generated content
        return {
            "success": True,
            "generated_content": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Content generation webhook failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


async def analyze_content_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze content webhook from n8n."""
    try:
        # Extract analysis parameters
        content = payload.get("content")
        model_types = payload.get("model_types")
        
        if not content:
            raise ValueError("No content provided")
        
        # Analyze content
        result = await ai_service.analyze_content(
            content,
            model_types=model_types
        )
        
        # Return analysis results
        return {
            "success": True,
            "analysis": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Content analysis webhook failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.post("/task", status_code=status.HTTP_202_ACCEPTED)
async def submit_n8n_task(
    task_data: Dict[str, Any] = Body(...),
    x_n8n_signature: Optional[str] = Header(None)
):
    """
    Submit a background task from n8n.
    
    This allows n8n to trigger background tasks in Maya.
    """
    # Get webhook secret from settings
    webhook_secret = settings.integrations.n8n_webhook_secret
    
    # Verify signature if configured
    if webhook_secret and x_n8n_signature:
        request_body = json.dumps(task_data).encode()
        if not verify_webhook_signature(request_body, x_n8n_signature, webhook_secret):
            logger.warning("Invalid n8n task signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid task signature"
            )
    
    try:
        # Add task metadata
        if "id" not in task_data:
            task_data["id"] = str(uuid.uuid4())
        
        task_data["submitted_by"] = "n8n"
        task_data["submitted_at"] = datetime.utcnow().isoformat()
        
        # Submit task to worker
        await worker_manager.process_task(task_data)
        
        return {
            "success": True,
            "task_id": task_data["id"],
            "status": "accepted",
            "message": "Task submitted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error submitting n8n task: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": str(e)
            }
        )


@router.get("/platform-specs", status_code=status.HTTP_200_OK)
async def get_platform_specs():
    """
    Get platform specifications for n8n integration.
    
    This allows n8n to dynamically configure nodes based on platform requirements.
    """
    try:
        platform_specs = platform_service.get_platform_requirements()
        
        return {
            "success": True,
            "platform_specs": platform_specs
        }
        
    except Exception as e:
        logger.error(f"Error getting platform specs: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": str(e)
            }
        )


@router.get("/health", status_code=status.HTTP_200_OK)
async def n8n_health_check():
    """
    Health check endpoint for n8n integration.
    
    This allows n8n to check if Maya is available.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Maya AI - n8n Integration"
    }
