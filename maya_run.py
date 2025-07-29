#!/usr/bin/env python3
"""
Run script for the new unified Maya system.

This script provides simplified commands to run the different components
of the Maya system using the new consolidated structure.
"""

import os
import sys
import argparse
import uvicorn
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import core components
from maya.core.config import get_settings
from maya.core.logging import configure_logging, get_logger

# Initialize logger
logger = get_logger()


def main():
    """Main entry point for Maya system."""
    parser = argparse.ArgumentParser(description="Maya AI Content Optimization System")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # API server command
    api_parser = subparsers.add_parser("api", help="Run the API server")
    api_parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    api_parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    api_parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    api_parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    
    # Worker command
    worker_parser = subparsers.add_parser("worker", help="Run the background worker")
    worker_parser.add_argument("--workers", type=int, default=2, help="Number of worker processes")
    
    # Database init command
    subparsers.add_parser("init-db", help="Initialize the database")
    
    # Version command
    subparsers.add_parser("version", help="Show version information")
    
    # Config command
    subparsers.add_parser("config", help="Show configuration information")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Configure logging
    configure_logging()
    
    # Handle commands
    if args.command == "api":
        run_api_server(args.host, args.port, args.reload, args.workers)
    elif args.command == "worker":
        run_worker(args.workers)
    elif args.command == "init-db":
        init_database()
    elif args.command == "version":
        show_version()
    elif args.command == "config":
        show_config()
    else:
        parser.print_help()


def run_api_server(host="0.0.0.0", port=8000, reload=False, workers=1):
    """Run the API server."""
    logger.info(f"Starting Maya API server on {host}:{port}")
    
    # Import app factory function
    from maya.api.app import create_app
    
    if reload:
        # For development with auto-reload
        uvicorn.run(
            "maya.api.app:create_app",
            host=host,
            port=port,
            reload=True,
            factory=True
        )
    else:
        # For production
        uvicorn.run(
            "maya.api.app:create_app",
            host=host,
            port=port,
            workers=workers,
            factory=True
        )


def run_worker(workers=2):
    """Run the background worker."""
    logger.info(f"Starting Maya worker with {workers} processes")
    
    import asyncio
    from maya.worker.worker import WorkerManager
    
    async def run_worker_async():
        worker_manager = WorkerManager(worker_count=workers)
        await worker_manager.start()
        
        try:
            # Keep worker running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down worker...")
            await worker_manager.stop()
    
    # Run the worker
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_worker_async())
    finally:
        loop.close()


def init_database():
    """Initialize the database."""
    logger.info("Initializing database schema")
    
    import asyncio
    from maya.core.database import init_database
    
    async def init_db_async():
        await init_database()
        logger.info("Database schema initialized successfully")
    
    # Run the initialization
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(init_db_async())
    finally:
        loop.close()


def show_version():
    """Show version information."""
    import maya
    version = getattr(maya, "__version__", "0.1.0")
    logger.info(f"Maya AI Content Optimization System v{version}")
    print(f"Maya AI Content Optimization System v{version}")


def show_config():
    """Show configuration information."""
    settings = get_settings()
    
    config_info = {
        "Environment": settings.app.environment,
        "Debug mode": settings.app.debug,
        "API cors origins": settings.api.cors_origins,
        "Database URL": settings.database.url.replace("://", "://<user>:<pass>@") if hasattr(settings.database, "url") else "Not configured",
        "OpenAI API configured": "Yes" if settings.ai.openai_api_key else "No",
        "HuggingFace API configured": "Yes" if settings.ai.huggingface_api_key else "No"
    }
    
    logger.info("Configuration information", **config_info)
    
    print("\nMaya AI Configuration:")
    print("=====================")
    for key, value in config_info.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
