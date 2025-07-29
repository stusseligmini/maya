"""
Worker module for Maya system.

This module provides task queue workers for processing background tasks,
handling content processing, and coordinating with external services.
"""

import structlog
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
import time
import traceback

from maya.core.exceptions import WorkerError
from maya.core.logging import LoggerMixin
from maya.core.config import get_settings
from maya.services.services import ai_service, content_service, platform_service

logger = structlog.get_logger()
settings = get_settings()


class TaskWorker(LoggerMixin):
    """Base worker class for background task processing."""
    
    def __init__(self):
        self.logger.info("Task worker initialized")
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task from the queue."""
        task_type = task_data.get("type")
        
        self.logger.info("Processing task", 
                       task_id=task_data.get("id"), 
                       task_type=task_type)
        
        start_time = time.time()
        
        try:
            if task_type == "content_processing":
                result = await self._process_content_task(task_data)
            elif task_type == "ai_generation":
                result = await self._process_ai_task(task_data)
            elif task_type == "platform_publish":
                result = await self._process_publish_task(task_data)
            else:
                raise WorkerError(f"Unknown task type: {task_type}")
            
            processing_time = time.time() - start_time
            
            self.logger.info("Task completed", 
                           task_id=task_data.get("id"),
                           processing_time=processing_time)
            
            return {
                "status": "completed",
                "task_id": task_data.get("id"),
                "result": result,
                "processing_time": processing_time
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_details = traceback.format_exc()
            
            self.logger.error("Task processing failed", 
                            task_id=task_data.get("id"),
                            error=str(e),
                            processing_time=processing_time)
            
            return {
                "status": "failed",
                "task_id": task_data.get("id"),
                "error": str(e),
                "error_details": error_details,
                "processing_time": processing_time
            }
    
    async def _process_content_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process content optimization task."""
        content_data = task_data.get("content")
        target_platforms = task_data.get("platforms", ["twitter", "instagram"])
        
        if not content_data:
            raise WorkerError("No content data provided")
        
        # Use content service to process
        result = await content_service.process_content(
            content_data,
            target_platforms=target_platforms
        )
        
        return result
    
    async def _process_ai_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process AI generation task."""
        prompt = task_data.get("prompt")
        model_type = task_data.get("model", "openai")
        
        if not prompt:
            raise WorkerError("No prompt provided")
        
        # Use AI service to generate content
        result = await ai_service.generate_content(
            prompt,
            model_type=model_type,
            max_tokens=task_data.get("max_tokens", 150),
            temperature=task_data.get("temperature", 0.7)
        )
        
        return result
    
    async def _process_publish_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process platform publishing task."""
        content_data = task_data.get("content")
        platform = task_data.get("platform")
        
        if not content_data or not platform:
            raise WorkerError("Content data and platform are required")
        
        # Use platform service to optimize and publish
        result = await platform_service.optimize_for_platform(
            content_data,
            platform=platform
        )
        
        # Placeholder for actual publishing
        result["published"] = {
            "status": "simulated",
            "timestamp": datetime.utcnow().isoformat(),
            "platform": platform
        }
        
        return result


class WorkerManager(LoggerMixin):
    """Manager for worker tasks and queue processing."""
    
    def __init__(self, worker_count: int = 2):
        self.worker_count = worker_count
        self.task_worker = TaskWorker()
        self.logger.info("Worker manager initialized", worker_count=worker_count)
    
    async def start(self):
        """Start the worker manager."""
        self.logger.info("Worker manager starting")
        # In a real implementation, this would start processing from a queue
        # For now, it's just a placeholder
    
    async def stop(self):
        """Stop the worker manager."""
        self.logger.info("Worker manager stopping")
        # Cleanup resources
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single task."""
        return await self.task_worker.process_task(task_data)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check worker health status."""
        return {
            "status": "healthy",
            "worker_count": self.worker_count,
            "timestamp": datetime.utcnow().isoformat()
        }


# Initialize worker manager
worker_manager = WorkerManager(worker_count=settings.worker.worker_count)
