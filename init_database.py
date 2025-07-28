#!/usr/bin/env python3
"""
Database initialization script for Maya AI Content Optimization
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import init_db, check_db_health
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Initialize the database"""
    logger.info("Starting database initialization...")
    
    try:
        # Check database connectivity
        if not check_db_health():
            logger.error("Database health check failed")
            return False
        
        logger.info("Database connectivity verified")
        
        # Initialize database tables
        init_db()
        logger.info("Database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)