"""
Background tasks for content processing, moderation, and publishing
"""
from celery import Celery
from typing import Dict, Any, List
import logging
import asyncio
from datetime import datetime

from .worker import celery_app, run_async_task
from ..database.models import ContentItem, ContentStatus, ProcessingQueue
from ..database.connection import get_db_session
from ..services.ai_service import AIService
from ..services.moderation_service import ModerationService
from ..services.publishing_service import PublishingService

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="queue.tasks.process_content")
def process_content_task(self, content_id: int, user_id: int) -> Dict[str, Any]:
    """Main content processing task that orchestrates the full pipeline"""
    try:
        logger.info(f"Starting content processing for content_id: {content_id}")
        
        # Update task status
        with get_db_session() as db:
            # Update content status
            content = db.query(ContentItem).filter(ContentItem.id == content_id).first()
            if not content:
                raise ValueError(f"Content {content_id} not found")
            
            content.status = ContentStatus.PROCESSING
            db.commit()
            
            # Create processing queue entry
            queue_entry = ProcessingQueue(
                content_item_id=content_id,
                task_type="full_processing",
                status="processing",
                started_at=datetime.utcnow()
            )
            db.add(queue_entry)
            db.commit()
        
        # Step 1: Content Moderation
        moderation_result = run_async_task(
            ModerationService().moderate_content(content_id, user_id)
        )
        
        if moderation_result.get("result") == "blocked":
            logger.warning(f"Content {content_id} blocked by moderation")
            with get_db_session() as db:
                content = db.query(ContentItem).filter(ContentItem.id == content_id).first()
                content.status = ContentStatus.REJECTED
                db.commit()
            return {"status": "rejected", "reason": "moderation_failed"}
        
        # Step 2: AI Analysis and Enhancement
        ai_analysis = run_async_task(
            AIService().analyze_content(content_id, user_id)
        )
        
        # Step 3: Caption Generation
        caption_task = run_async_task(
            AIService().generate_caption(content_id, "instagram", user_id)
        )
        
        # Step 4: Platform Optimization
        optimization_results = {}
        platforms = ["instagram", "tiktok", "twitter"]
        
        for platform in platforms:
            try:
                optimization = run_async_task(
                    AIService().optimize_for_platform(content_id, platform, user_id)
                )
                optimization_results[platform] = optimization
            except Exception as e:
                logger.error(f"Optimization failed for {platform}: {str(e)}")
                optimization_results[platform] = {"error": str(e)}
        
        # Update content status
        with get_db_session() as db:
            content = db.query(ContentItem).filter(ContentItem.id == content_id).first()
            content.status = ContentStatus.APPROVED
            content.processed_at = datetime.utcnow()
            
            # Update queue entry
            queue_entry = db.query(ProcessingQueue).filter(
                ProcessingQueue.content_item_id == content_id,
                ProcessingQueue.task_type == "full_processing"
            ).first()
            if queue_entry:
                queue_entry.status = "completed"
                queue_entry.completed_at = datetime.utcnow()
            
            db.commit()
        
        logger.info(f"Content processing completed for content_id: {content_id}")
        
        return {
            "status": "success",
            "content_id": content_id,
            "moderation": moderation_result,
            "ai_analysis": ai_analysis,
            "caption": caption_task,
            "optimizations": optimization_results,
            "processed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Content processing failed for {content_id}: {str(e)}")
        
        # Update status to failed
        try:
            with get_db_session() as db:
                content = db.query(ContentItem).filter(ContentItem.id == content_id).first()
                if content:
                    content.status = ContentStatus.FAILED
                
                queue_entry = db.query(ProcessingQueue).filter(
                    ProcessingQueue.content_item_id == content_id,
                    ProcessingQueue.task_type == "full_processing"
                ).first()
                if queue_entry:
                    queue_entry.status = "failed"
                    queue_entry.error_message = str(e)
                    queue_entry.completed_at = datetime.utcnow()
                
                db.commit()
        except Exception as db_error:
            logger.error(f"Failed to update database after error: {str(db_error)}")
        
        # Retry logic
        if self.request.retries < 3:
            logger.info(f"Retrying content processing for {content_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (2 ** self.request.retries), max_retries=3)
        
        return {
            "status": "failed",
            "content_id": content_id,
            "error": str(e),
            "retries": self.request.retries
        }

@celery_app.task(name="queue.tasks.batch_process_content")
def batch_process_content_task(content_ids: List[int], user_id: int) -> Dict[str, Any]:
    """Process multiple content items in batch"""
    results = []
    
    for content_id in content_ids:
        try:
            result = process_content_task.delay(content_id, user_id)
            results.append({
                "content_id": content_id,
                "task_id": result.id,
                "status": "queued"
            })
        except Exception as e:
            results.append({
                "content_id": content_id,
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "batch_id": self.request.id,
        "total_items": len(content_ids),
        "results": results
    }

@celery_app.task(name="queue.tasks.priority_process_content")
def priority_process_content_task(content_id: int, user_id: int, priority: int = 1) -> Dict[str, Any]:
    """High-priority content processing task"""
    logger.info(f"Priority processing content {content_id} with priority {priority}")
    
    # Same as regular processing but with higher priority
    return process_content_task(content_id, user_id)

@celery_app.task(name="queue.tasks.schedule_publishing")
def schedule_publishing_task(content_id: int, platforms: List[str], schedule_time: str, user_id: int) -> Dict[str, Any]:
    """Schedule content publishing for future time"""
    try:
        # Parse schedule time
        from datetime import datetime
        scheduled_datetime = datetime.fromisoformat(schedule_time)
        
        # Create scheduled publishing tasks
        results = []
        for platform in platforms:
            # Schedule individual platform publishing
            task = publish_to_platform_task.apply_async(
                args=[content_id, platform, user_id],
                eta=scheduled_datetime
            )
            results.append({
                "platform": platform,
                "task_id": task.id,
                "scheduled_for": schedule_time
            })
        
        return {
            "status": "scheduled",
            "content_id": content_id,
            "platforms": platforms,
            "scheduled_for": schedule_time,
            "tasks": results
        }
        
    except Exception as e:
        logger.error(f"Scheduling failed for content {content_id}: {str(e)}")
        return {
            "status": "failed",
            "error": str(e)
        }

@celery_app.task(name="queue.tasks.publish_to_platform")
def publish_to_platform_task(content_id: int, platform: str, user_id: int) -> Dict[str, Any]:
    """Publish content to specific platform"""
    try:
        logger.info(f"Publishing content {content_id} to {platform}")
        
        result = run_async_task(
            PublishingService().publish_to_platform(content_id, platform, user_id)
        )
        
        return {
            "status": "success",
            "content_id": content_id,
            "platform": platform,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Publishing failed for content {content_id} to {platform}: {str(e)}")
        return {
            "status": "failed",
            "content_id": content_id,
            "platform": platform,
            "error": str(e)
        }

@celery_app.task(name="queue.tasks.cleanup_old_tasks")
def cleanup_old_tasks() -> Dict[str, Any]:
    """Clean up old completed tasks and queue entries"""
    try:
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        with get_db_session() as db:
            # Clean up old queue entries
            deleted_count = db.query(ProcessingQueue).filter(
                ProcessingQueue.completed_at < cutoff_date
            ).delete()
            
            db.commit()
        
        logger.info(f"Cleaned up {deleted_count} old queue entries")
        
        return {
            "status": "success",
            "deleted_entries": deleted_count,
            "cutoff_date": cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {str(e)}")
        return {
            "status": "failed",
            "error": str(e)
        }

@celery_app.task(name="queue.tasks.health_check")
def health_check_task() -> Dict[str, Any]:
    """Health check task to verify worker is functioning"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "worker_id": celery_app.current_worker_task.request.hostname if hasattr(celery_app, 'current_worker_task') else "unknown"
    }
