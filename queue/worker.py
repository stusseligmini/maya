"""
Background task worker using Celery for Maya AI Content Optimization
"""
from celery import Celery
import os
from typing import Dict, Any
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "maya_worker",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/1"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/2"),
    include=[
        "queue.tasks",
        "moderation.tasks",
        "processing.tasks",
        "publishing.tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Task routing
celery_app.conf.task_routes = {
    "queue.tasks.process_content": {"queue": "content_processing"},
    "moderation.tasks.moderate_content": {"queue": "moderation"},
    "processing.tasks.generate_caption": {"queue": "ai_processing"},
    "processing.tasks.optimize_content": {"queue": "ai_processing"},
    "publishing.tasks.publish_to_platform": {"queue": "publishing"},
}

def run_async_task(coro):
    """Helper to run async functions in Celery tasks"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

if __name__ == "__main__":
    celery_app.start()
