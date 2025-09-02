#!/usr/bin/env python3
"""
Main entry point for RAG Document QA System
Copyright (c) 2024 Balenci Cash - All Rights Reserved
Protected by Digital Watermark
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from src.api.main import app
from src.utils.logger import logger
from src.utils.watermark import initialize_watermark_protection
from config.settings import settings


def main():
    """Main function to start the application."""
    
    # Display copyright and watermark information
    print("=" * 60)
    print(f"{settings.APP_NAME} v{settings.APP_VERSION}")
    print(settings.APP_COPYRIGHT)
    print("Protected by Digital Watermark Technology")
    print("Unauthorized use or distribution is prohibited")
    print("=" * 60)
    
    # Initialize watermark protection
    try:
        initialize_watermark_protection()
    except RuntimeError as e:
        logger.error(f"Watermark verification failed: {e}")
        sys.exit(1)
    
    # Start the application
    logger.info(f"Starting server on {settings.API_HOST}:{settings.API_PORT}")
    
    uvicorn.run(
        "src.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False,
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()