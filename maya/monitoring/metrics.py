"""Monitoring and observability for Maya system."""

import time
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import psutil
import threading
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlAlchemyIntegration

from maya.core.logging import LoggerMixin, get_logger
from maya.config.settings import get_settings


@dataclass
class MetricData:
    """Metric data structure."""
    name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class HealthCheck:
    """Health check result."""
    name: str
    status: str  # "healthy", "unhealthy", "degraded"
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    response_time_ms: Optional[float] = None


class PrometheusMetrics(LoggerMixin):
    """Prometheus metrics collection."""
    
    def __init__(self):
        # HTTP metrics
        self.http_requests_total = Counter(
            'maya_http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code']
        )
        
        self.http_request_duration = Histogram(
            'maya_http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint']
        )
        
        # AI model metrics
        self.ai_model_requests_total = Counter(
            'maya_ai_model_requests_total',
            'Total AI model requests',
            ['model_type', 'operation']
        )
        
        self.ai_model_duration = Histogram(
            'maya_ai_model_duration_seconds',
            'AI model operation duration',
            ['model_type', 'operation']
        )
        
        self.ai_model_errors_total = Counter(
            'maya_ai_model_errors_total',
            'Total AI model errors',
            ['model_type', 'error_type']
        )
        
        # Content processing metrics
        self.content_processed_total = Counter(
            'maya_content_processed_total',
            'Total content items processed',
            ['content_type', 'platform']
        )
        
        self.content_processing_duration = Histogram(
            'maya_content_processing_duration_seconds',
            'Content processing duration',
            ['content_type']
        )
        
        # Social platform metrics
        self.social_posts_total = Counter(
            'maya_social_posts_total',
            'Total social media posts',
            ['platform', 'status']
        )
        
        self.social_api_errors_total = Counter(
            'maya_social_api_errors_total',
            'Total social media API errors',
            ['platform', 'error_type']
        )
        
        # System metrics
        self.system_cpu_usage = Gauge(
            'maya_system_cpu_usage_percent',
            'System CPU usage percentage'
        )
        
        self.system_memory_usage = Gauge(
            'maya_system_memory_usage_bytes',
            'System memory usage in bytes'
        )
        
        self.system_disk_usage = Gauge(
            'maya_system_disk_usage_percent',
            'System disk usage percentage'
        )
        
        # Database metrics
        self.database_connections = Gauge(
            'maya_database_connections_active',
            'Active database connections'
        )
        
        self.database_query_duration = Histogram(
            'maya_database_query_duration_seconds',
            'Database query duration',
            ['operation']
        )
        
        self.logger.info("Prometheus metrics initialized")
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        self.http_requests_total.labels(
            method=method, 
            endpoint=endpoint, 
            status_code=status_code
        ).inc()
        
        self.http_request_duration.labels(
            method=method, 
            endpoint=endpoint
        ).observe(duration)
    
    def record_ai_model_request(self, model_type: str, operation: str, duration: float, error: Optional[str] = None):
        """Record AI model request metrics."""
        self.ai_model_requests_total.labels(
            model_type=model_type, 
            operation=operation
        ).inc()
        
        self.ai_model_duration.labels(
            model_type=model_type, 
            operation=operation
        ).observe(duration)
        
        if error:
            self.ai_model_errors_total.labels(
                model_type=model_type, 
                error_type=error
            ).inc()
    
    def record_content_processing(self, content_type: str, platform: str, duration: float):
        """Record content processing metrics."""
        self.content_processed_total.labels(
            content_type=content_type, 
            platform=platform
        ).inc()
        
        self.content_processing_duration.labels(
            content_type=content_type
        ).observe(duration)
    
    def record_social_post(self, platform: str, status: str, error_type: Optional[str] = None):
        """Record social media post metrics."""
        self.social_posts_total.labels(
            platform=platform, 
            status=status
        ).inc()
        
        if error_type:
            self.social_api_errors_total.labels(
                platform=platform, 
                error_type=error_type
            ).inc()
    
    def update_system_metrics(self):
        """Update system resource metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.system_cpu_usage.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.system_memory_usage.set(memory.used)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.system_disk_usage.set(disk_percent)
            
        except Exception as e:
            self.logger.error("Failed to update system metrics", error=str(e))
    
    def get_metrics(self) -> str:
        """Get Prometheus metrics in text format."""
        return generate_latest()


class PerformanceTracker(LoggerMixin):
    """Performance tracking and analysis."""
    
    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self.response_times = defaultdict(lambda: deque(maxlen=max_samples))
        self.error_counts = defaultdict(int)
        self.request_counts = defaultdict(int)
    
    def track_request(self, endpoint: str, duration: float, success: bool = True):
        """Track request performance."""
        self.response_times[endpoint].append(duration)
        self.request_counts[endpoint] += 1
        
        if not success:
            self.error_counts[endpoint] += 1
    
    def get_performance_stats(self, endpoint: str) -> Dict[str, Any]:
        """Get performance statistics for an endpoint."""
        times = list(self.response_times[endpoint])
        
        if not times:
            return {"error": "No data available"}
        
        times.sort()
        count = len(times)
        
        stats = {
            "count": count,
            "min": min(times),
            "max": max(times),
            "avg": sum(times) / count,
            "p50": times[count // 2],
            "p95": times[int(count * 0.95)] if count > 20 else times[-1],
            "p99": times[int(count * 0.99)] if count > 100 else times[-1],
            "error_rate": self.error_counts[endpoint] / self.request_counts[endpoint] if self.request_counts[endpoint] > 0 else 0
        }
        
        return stats
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics for all tracked endpoints."""
        return {
            endpoint: self.get_performance_stats(endpoint)
            for endpoint in self.response_times.keys()
        }


class HealthMonitor(LoggerMixin):
    """System health monitoring."""
    
    def __init__(self):
        self.health_checks: Dict[str, Callable] = {}
        self.last_check_results: Dict[str, HealthCheck] = {}
    
    def register_health_check(self, name: str, check_func: Callable) -> None:
        """Register a health check function."""
        self.health_checks[name] = check_func
        self.logger.info("Health check registered", name=name)
    
    async def run_health_check(self, name: str) -> HealthCheck:
        """Run a specific health check."""
        if name not in self.health_checks:
            return HealthCheck(
                name=name,
                status="unhealthy",
                details={"error": "Health check not found"}
            )
        
        start_time = time.time()
        
        try:
            check_func = self.health_checks[name]
            
            if asyncio.iscoroutinefunction(check_func):
                result = await check_func()
            else:
                result = check_func()
            
            response_time = (time.time() - start_time) * 1000
            
            if isinstance(result, dict):
                status = result.get("status", "healthy")
                details = result.get("details", {})
            else:
                status = "healthy" if result else "unhealthy"
                details = {}
            
            health_check = HealthCheck(
                name=name,
                status=status,
                details=details,
                response_time_ms=response_time
            )
            
            self.last_check_results[name] = health_check
            return health_check
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            health_check = HealthCheck(
                name=name,
                status="unhealthy",
                details={"error": str(e)},
                response_time_ms=response_time
            )
            
            self.last_check_results[name] = health_check
            self.logger.error("Health check failed", name=name, error=str(e))
            return health_check
    
    async def run_all_health_checks(self) -> Dict[str, HealthCheck]:
        """Run all registered health checks."""
        tasks = []
        
        for name in self.health_checks:
            task = asyncio.create_task(
                self.run_health_check(name),
                name=f"health_check_{name}"
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        health_status = {}
        for i, result in enumerate(results):
            check_name = list(self.health_checks.keys())[i]
            
            if isinstance(result, Exception):
                health_status[check_name] = HealthCheck(
                    name=check_name,
                    status="unhealthy",
                    details={"error": str(result)}
                )
            else:
                health_status[check_name] = result
        
        return health_status
    
    def get_overall_health(self) -> str:
        """Get overall system health status."""
        if not self.last_check_results:
            return "unknown"
        
        statuses = [check.status for check in self.last_check_results.values()]
        
        if all(status == "healthy" for status in statuses):
            return "healthy"
        elif any(status == "unhealthy" for status in statuses):
            return "unhealthy"
        else:
            return "degraded"


class AlertManager(LoggerMixin):
    """Alert management system."""
    
    def __init__(self):
        self.alert_rules: List[Dict[str, Any]] = []
        self.active_alerts: Dict[str, Dict[str, Any]] = {}
    
    def add_alert_rule(
        self, 
        name: str, 
        condition: Callable, 
        severity: str = "warning",
        description: str = ""
    ):
        """Add an alert rule."""
        rule = {
            "name": name,
            "condition": condition,
            "severity": severity,
            "description": description,
            "created_at": datetime.utcnow()
        }
        
        self.alert_rules.append(rule)
        self.logger.info("Alert rule added", name=name, severity=severity)
    
    async def check_alerts(self, metrics: Dict[str, Any]):
        """Check all alert rules against current metrics."""
        for rule in self.alert_rules:
            try:
                rule_name = rule["name"]
                condition = rule["condition"]
                
                if asyncio.iscoroutinefunction(condition):
                    triggered = await condition(metrics)
                else:
                    triggered = condition(metrics)
                
                if triggered:
                    if rule_name not in self.active_alerts:
                        # New alert
                        alert = {
                            "rule": rule,
                            "triggered_at": datetime.utcnow(),
                            "metrics": metrics.copy()
                        }
                        
                        self.active_alerts[rule_name] = alert
                        await self._send_alert(alert)
                        
                        self.logger.warning("Alert triggered", 
                                          rule_name=rule_name, 
                                          severity=rule["severity"])
                else:
                    if rule_name in self.active_alerts:
                        # Alert resolved
                        del self.active_alerts[rule_name]
                        self.logger.info("Alert resolved", rule_name=rule_name)
                        
            except Exception as e:
                self.logger.error("Alert rule check failed", 
                                rule_name=rule.get("name", "unknown"), 
                                error=str(e))
    
    async def _send_alert(self, alert: Dict[str, Any]):
        """Send alert notification."""
        # This is where you would integrate with notification systems
        # like Slack, email, PagerDuty, etc.
        rule = alert["rule"]
        
        self.logger.critical("ALERT",
                           alert_name=rule["name"],
                           severity=rule["severity"],
                           description=rule["description"],
                           triggered_at=alert["triggered_at"].isoformat())


class MonitoringMiddleware:
    """FastAPI middleware for monitoring."""
    
    def __init__(self, metrics: PrometheusMetrics, performance_tracker: PerformanceTracker):
        self.metrics = metrics
        self.performance_tracker = performance_tracker
        self.logger = get_logger("MonitoringMiddleware")
    
    async def __call__(self, request: Request, call_next):
        """Process request and collect metrics."""
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Extract endpoint path
            endpoint = request.url.path
            method = request.method
            status_code = response.status_code
            
            # Record metrics
            self.metrics.record_http_request(method, endpoint, status_code, duration)
            self.performance_tracker.track_request(endpoint, duration, status_code < 400)
            
            # Add monitoring headers
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            endpoint = request.url.path
            method = request.method
            
            # Record error metrics
            self.metrics.record_http_request(method, endpoint, 500, duration)
            self.performance_tracker.track_request(endpoint, duration, False)
            
            self.logger.error("Request processing failed", 
                            method=method, endpoint=endpoint, error=str(e))
            raise


def configure_sentry():
    """Configure Sentry for error tracking."""
    settings = get_settings()
    
    if settings.monitoring.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.monitoring.sentry_dsn,
            integrations=[
                FastApiIntegration(),
                SqlAlchemyIntegration(),
            ],
            traces_sample_rate=0.1,  # Adjust based on needs
            environment=settings.environment
        )


# Global monitoring instances
prometheus_metrics = PrometheusMetrics()
performance_tracker = PerformanceTracker()
health_monitor = HealthMonitor()
alert_manager = AlertManager()


# System metrics update task
async def update_system_metrics_task():
    """Background task to update system metrics."""
    logger = get_logger("SystemMetrics")
    
    while True:
        try:
            prometheus_metrics.update_system_metrics()
            await asyncio.sleep(30)  # Update every 30 seconds
        except Exception as e:
            logger.error("System metrics update failed", error=str(e))
            await asyncio.sleep(60)  # Wait longer on error


# Default health checks
async def database_health_check():
    """Check database connectivity."""
    # This would check actual database connection
    # For now, returning healthy
    return {"status": "healthy", "details": {"connection": "ok"}}


async def redis_health_check():
    """Check Redis connectivity."""
    # This would check actual Redis connection
    # For now, returning healthy
    return {"status": "healthy", "details": {"connection": "ok"}}


# Register default health checks
health_monitor.register_health_check("database", database_health_check)
health_monitor.register_health_check("redis", redis_health_check)