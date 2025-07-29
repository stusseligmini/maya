"""
Database configuration and connection management for Maya AI Content Optimization

This module provides database initialization, session management, and health check functions.
"""

from sqlalchemy import create_engine, MetaData, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging
from typing import Generator, Dict, Any, Optional
from contextlib import contextmanager
import time

# Import the settings
from maya.core.config import settings

# Configure logger
logger = logging.getLogger(__name__)

# Create base declarative model class - imported by models
Base = declarative_base()

# Create database engine with appropriate configuration
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL and other databases
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,
        pool_recycle=300,  # Recycle connections after 5 minutes
        pool_size=10,      # Maximum connection pool size
        max_overflow=20    # Allow up to 20 connections beyond pool_size
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Metadata for migrations and schema inspection
metadata = MetaData()


def init_db() -> None:
    """
    Initialize database schemas and tables
    
    This function creates all tables defined in the models if they don't exist.
    In production, you would typically use Alembic migrations instead.
    """
    logger.info("Initializing database schemas and tables")
    try:
        # Import all models that should create tables
        from maya.core.models import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialization complete")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Get database session context manager
    
    Usage:
        with get_db() as db:
            # use db session here
    
    Yields:
        Database session that will be automatically closed
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database session
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def close_db() -> None:
    """
    Close database connections
    
    This should be called during application shutdown to properly release resources.
    """
    logger.info("Closing database connections")
    try:
        engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {str(e)}")


def check_db_health() -> Dict[str, Any]:
    """
    Check database health
    
    Returns:
        Dictionary with health status information
    """
    start_time = time.time()
    health_info = {
        "status": "unhealthy",
        "message": "Database health check failed",
        "latency_ms": 0,
        "details": {}
    }
    
    try:
        # Run a simple query to check database connectivity
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        
        # Get database info
        inspector = inspect(engine)
        health_info["details"] = {
            "dialect": engine.dialect.name,
            "driver": engine.dialect.driver,
            "tables_count": len(inspector.get_table_names()),
        }
        
        health_info["status"] = "healthy"
        health_info["message"] = "Database is connected and responding"
    except Exception as e:
        health_info["details"]["error"] = str(e)
    finally:
        health_info["latency_ms"] = round((time.time() - start_time) * 1000, 2)
    
    return health_info


def get_table_sizes() -> Dict[str, int]:
    """
    Get sizes of database tables (PostgreSQL only)
    
    Returns:
        Dictionary mapping table names to sizes in bytes
    """
    if not engine.dialect.name == 'postgresql':
        return {}
    
    try:
        with engine.connect() as connection:
            query = text("""
                SELECT
                    relname as table_name,
                    pg_total_relation_size(c.oid) as total_size
                FROM pg_class c
                LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE
                    relkind = 'r' AND
                    n.nspname = 'public'
                ORDER BY total_size DESC
            """)
            result = connection.execute(query)
            return {row[0]: row[1] for row in result}
    except Exception as e:
        logger.error(f"Error getting table sizes: {str(e)}")
        return {}
