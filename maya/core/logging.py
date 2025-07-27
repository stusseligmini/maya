"""Core logging configuration for Maya system."""

try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False

import logging
import sys
from typing import Any, Dict


if STRUCTLOG_AVAILABLE:

    def configure_logging(level: str = "INFO", json_logs: bool = True) -> None:
        """Configure structured logging for the application."""
        
        timestamper = structlog.processors.TimeStamper(fmt="ISO")
        
        shared_processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            timestamper,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
        ]
        
        if json_logs:
            # Use JSON formatting for production
            shared_processors.append(structlog.processors.JSONRenderer())
        else:
            # Use console formatting for development
            shared_processors.append(structlog.dev.ConsoleRenderer())
        
        structlog.configure(
            processors=shared_processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        
        # Configure standard library logging
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=getattr(logging, level.upper()),
        )


    def get_logger(name: str) -> structlog.BoundLogger:
        """Get a structured logger instance."""
        return structlog.get_logger(name)


    class LoggerMixin:
        """Mixin class to add logging capabilities to any class."""
        
        @property
        def logger(self) -> structlog.BoundLogger:
            """Get logger instance for this class."""
            return get_logger(self.__class__.__name__)


else:
    # Fallback implementation when structlog is not available
    
    def configure_logging(level: str = "INFO", json_logs: bool = True) -> None:
        """Configure basic logging for the application (fallback)."""
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            stream=sys.stdout,
        )
    
    
    class FallbackLogger:
        """Fallback logger that mimics structlog interface."""
        
        def __init__(self, name: str):
            self._logger = logging.getLogger(name)
        
        def info(self, msg: str, **kwargs):
            extra_info = " ".join(f"{k}={v}" for k, v in kwargs.items())
            self._logger.info(f"{msg} {extra_info}" if extra_info else msg)
        
        def error(self, msg: str, **kwargs):
            extra_info = " ".join(f"{k}={v}" for k, v in kwargs.items())
            self._logger.error(f"{msg} {extra_info}" if extra_info else msg)
        
        def warning(self, msg: str, **kwargs):
            extra_info = " ".join(f"{k}={v}" for k, v in kwargs.items())
            self._logger.warning(f"{msg} {extra_info}" if extra_info else msg)
        
        def debug(self, msg: str, **kwargs):
            extra_info = " ".join(f"{k}={v}" for k, v in kwargs.items())
            self._logger.debug(f"{msg} {extra_info}" if extra_info else msg)
    
    
    def get_logger(name: str) -> FallbackLogger:
        """Get a logger instance (fallback version)."""
        return FallbackLogger(name)
    
    
    class LoggerMixin:
        """Mixin class to add logging capabilities to any class (fallback)."""
        
        @property
        def logger(self) -> FallbackLogger:
            """Get logger instance for this class."""
            return get_logger(self.__class__.__name__)