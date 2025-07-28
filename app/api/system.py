"""
System monitoring and status API endpoints
"""

import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
import structlog

from database.connection import get_db, check_db_health
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.models.content import Content, ContentStatus
from app.models.ai_model import AIProcessingJob, JobStatus
from config.settings import get_settings

logger = structlog.get_logger()
router = APIRouter(prefix="/system", tags=["system"])
settings = get_settings()


class HealthCheckResponse(BaseModel):
    """Enhanced health check response schema"""
    status: str
    timestamp: datetime
    version: str
    uptime_seconds: float
    services: Dict[str, Dict[str, Any]]
    environment: str


class SystemStatusResponse(BaseModel):
    """Comprehensive system status response"""
    status: str
    timestamp: datetime
    system_metrics: Dict[str, Any]
    database_metrics: Dict[str, Any]
    application_metrics: Dict[str, Any]
    service_health: Dict[str, str]


class QueueStatusResponse(BaseModel):
    """Job queue status response"""
    total_jobs: int
    pending_jobs: int
    running_jobs: int
    completed_jobs: int
    failed_jobs: int
    queue_health: str
    average_processing_time: Optional[float]
    oldest_pending_job: Optional[datetime]


class MetricsResponse(BaseModel):
    """System metrics response"""
    cpu_usage: float
    memory_usage: Dict[str, Any]
    disk_usage: Dict[str, Any]
    network_stats: Dict[str, Any]
    process_stats: Dict[str, Any]
    database_connections: int
    active_users: int
    request_count_24h: int


# System startup time for uptime calculation
STARTUP_TIME = time.time()


def get_system_metrics() -> Dict[str, Any]:
    """Get system performance metrics"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_info = {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "percentage": memory.percent
        }
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_info = {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percentage": round((disk.used / disk.total) * 100, 2)
        }
        
        # Network stats
        network = psutil.net_io_counters()
        network_info = {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
            "packets_sent": network.packets_sent,
            "packets_recv": network.packets_recv
        }
        
        # Process info
        process = psutil.Process()
        process_info = {
            "pid": process.pid,
            "cpu_percent": process.cpu_percent(),
            "memory_mb": round(process.memory_info().rss / (1024**2), 2),
            "threads": process.num_threads(),
            "connections": len(process.connections()),
            "create_time": datetime.fromtimestamp(process.create_time()).isoformat()
        }
        
        return {
            "cpu_usage": cpu_percent,
            "memory_usage": memory_info,
            "disk_usage": disk_info,
            "network_stats": network_info,
            "process_stats": process_info
        }
        
    except Exception as e:
        logger.error("Error getting system metrics", exc_info=e)
        return {
            "error": "Failed to retrieve system metrics",
            "cpu_usage": 0.0,
            "memory_usage": {},
            "disk_usage": {},
            "network_stats": {},
            "process_stats": {}
        }


def get_database_metrics(db: Session) -> Dict[str, Any]:
    """Get database performance metrics"""
    try:
        # Connection count (approximation for SQLite)
        db_health = check_db_health()
        
        # Table row counts
        total_users = db.query(User).count()
        total_content = db.query(Content).count()
        total_jobs = db.query(AIProcessingJob).count()
        
        # Recent activity
        recent_content = db.query(Content).filter(
            Content.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        recent_jobs = db.query(AIProcessingJob).filter(
            AIProcessingJob.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        return {
            "health": "healthy" if db_health else "unhealthy",
            "total_users": total_users,
            "total_content": total_content,
            "total_processing_jobs": total_jobs,
            "content_created_24h": recent_content,
            "jobs_created_24h": recent_jobs,
            "connection_status": "active"
        }
        
    except Exception as e:
        logger.error("Error getting database metrics", exc_info=e)
        return {
            "health": "unhealthy",
            "error": str(e),
            "total_users": 0,
            "total_content": 0,
            "total_processing_jobs": 0,
            "content_created_24h": 0,
            "jobs_created_24h": 0,
            "connection_status": "error"
        }


@router.get("/health", response_model=HealthCheckResponse)
async def enhanced_health_check(db: Session = Depends(get_db)):
    """
    Enhanced health check endpoint for monitoring systems
    Provides detailed service status information
    """
    uptime = time.time() - STARTUP_TIME
    
    # Check database health
    db_health = check_db_health()
    
    # Check various services
    services = {
        "database": {
            "status": "healthy" if db_health else "unhealthy",
            "response_time_ms": 0  # Could measure actual response time
        },
        "ai_processing": {
            "status": "healthy",  # In production, check actual AI service
            "response_time_ms": 0
        },
        "file_storage": {
            "status": "healthy",  # In production, check storage service
            "response_time_ms": 0
        },
        "cache": {
            "status": "healthy",  # In production, check Redis/cache
            "response_time_ms": 0
        }
    }
    
    # Determine overall status
    overall_status = "healthy" if all(
        service["status"] == "healthy" for service in services.values()
    ) else "degraded"
    
    return HealthCheckResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version=settings.VERSION,
        uptime_seconds=uptime,
        services=services,
        environment=getattr(settings, 'ENVIRONMENT', 'development')
    )


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Comprehensive system status endpoint
    Requires authentication for detailed system information
    """
    system_metrics = get_system_metrics()
    database_metrics = get_database_metrics(db)
    
    # Application-specific metrics
    app_metrics = {
        "total_users": database_metrics.get("total_users", 0),
        "active_content": database_metrics.get("total_content", 0),
        "pending_jobs": db.query(AIProcessingJob).filter(
            AIProcessingJob.status == JobStatus.PENDING
        ).count(),
        "processing_jobs": db.query(AIProcessingJob).filter(
            AIProcessingJob.status == JobStatus.RUNNING
        ).count(),
        "uptime_hours": round((time.time() - STARTUP_TIME) / 3600, 2)
    }
    
    # Service health summary
    service_health = {
        "database": "healthy" if database_metrics["health"] == "healthy" else "unhealthy",
        "ai_processing": "healthy",
        "file_storage": "healthy",
        "cache": "healthy",
        "webhooks": "healthy"
    }
    
    # Overall system status
    overall_status = "healthy" if all(
        status == "healthy" for status in service_health.values()
    ) else "degraded"
    
    return SystemStatusResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        system_metrics=system_metrics,
        database_metrics=database_metrics,
        application_metrics=app_metrics,
        service_health=service_health
    )


@router.get("/queue-status", response_model=QueueStatusResponse)
async def get_queue_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get job queue status and metrics
    Useful for monitoring processing workload
    """
    # Count jobs by status
    total_jobs = db.query(AIProcessingJob).count()
    pending_jobs = db.query(AIProcessingJob).filter(
        AIProcessingJob.status == JobStatus.PENDING
    ).count()
    running_jobs = db.query(AIProcessingJob).filter(
        AIProcessingJob.status == JobStatus.RUNNING
    ).count()
    completed_jobs = db.query(AIProcessingJob).filter(
        AIProcessingJob.status == JobStatus.COMPLETED
    ).count()
    failed_jobs = db.query(AIProcessingJob).filter(
        AIProcessingJob.status == JobStatus.FAILED
    ).count()
    
    # Calculate average processing time for completed jobs
    completed_with_time = db.query(AIProcessingJob).filter(
        AIProcessingJob.status == JobStatus.COMPLETED,
        AIProcessingJob.processing_time_seconds.isnot(None)
    ).all()
    
    avg_processing_time = None
    if completed_with_time:
        total_time = sum(job.processing_time_seconds for job in completed_with_time)
        avg_processing_time = total_time / len(completed_with_time)
    
    # Get oldest pending job
    oldest_pending = db.query(AIProcessingJob).filter(
        AIProcessingJob.status == JobStatus.PENDING
    ).order_by(AIProcessingJob.created_at.asc()).first()
    
    oldest_pending_time = oldest_pending.created_at if oldest_pending else None
    
    # Determine queue health
    queue_health = "healthy"
    if pending_jobs > 100:
        queue_health = "overloaded"
    elif pending_jobs > 50:
        queue_health = "busy"
    elif failed_jobs > pending_jobs + running_jobs:
        queue_health = "degraded"
    
    return QueueStatusResponse(
        total_jobs=total_jobs,
        pending_jobs=pending_jobs,
        running_jobs=running_jobs,
        completed_jobs=completed_jobs,
        failed_jobs=failed_jobs,
        queue_health=queue_health,
        average_processing_time=avg_processing_time,
        oldest_pending_job=oldest_pending_time
    )


@router.get("/metrics", response_model=MetricsResponse)
async def get_system_metrics_endpoint(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed system metrics for monitoring and alerting
    """
    system_metrics = get_system_metrics()
    
    # Database connection count (simplified for SQLite)
    database_connections = 1  # In production, get actual connection count
    
    # Active users (users who logged in within last 24 hours)
    active_users = db.query(User).filter(
        User.last_login >= datetime.utcnow() - timedelta(hours=24)
    ).count()
    
    # Request count (simplified - in production, use middleware to track)
    request_count_24h = 0  # Would be tracked by middleware
    
    return MetricsResponse(
        cpu_usage=system_metrics["cpu_usage"],
        memory_usage=system_metrics["memory_usage"],
        disk_usage=system_metrics["disk_usage"],
        network_stats=system_metrics["network_stats"],
        process_stats=system_metrics["process_stats"],
        database_connections=database_connections,
        active_users=active_users,
        request_count_24h=request_count_24h
    )


@router.get("/logs")
async def get_recent_logs(
    lines: int = 100,
    level: str = "INFO",
    current_user: User = Depends(get_current_active_user)
):
    """
    Get recent application logs
    Useful for debugging and monitoring
    """
    # In production, this would read from actual log files
    # For now, return a sample response
    
    sample_logs = [
        {
            "timestamp": "2024-01-01T12:00:00Z",
            "level": "INFO",
            "message": "Application started successfully",
            "module": "main"
        },
        {
            "timestamp": "2024-01-01T12:01:00Z",
            "level": "INFO",
            "message": "Database connection established",
            "module": "database"
        },
        {
            "timestamp": "2024-01-01T12:02:00Z",
            "level": "DEBUG",
            "message": "Processing AI job",
            "module": "ai_service"
        }
    ]
    
    return {
        "total_lines": len(sample_logs),
        "requested_lines": lines,
        "level_filter": level,
        "logs": sample_logs[:lines]
    }


@router.post("/restart")
async def restart_services(
    service: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Restart specific services (placeholder for production implementation)
    """
    # This would restart actual services in production
    valid_services = ["ai_processing", "webhook_handler", "file_processor"]
    
    if service not in valid_services:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid service. Valid options: {valid_services}"
        )
    
    logger.info(f"Service restart requested", service=service, user_id=current_user.id)
    
    return {
        "status": "success",
        "message": f"Service {service} restart initiated",
        "timestamp": datetime.utcnow().isoformat()
    }