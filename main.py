#!/usr/bin/env python3
"""
Clean Main Entry Point for RAG Document QA System.
Simplified startup with proper configuration validation.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import uvicorn
from src.utils.watermark import initialize_watermark
from config.settings import settings
from loguru import logger


def validate_configuration():
    """Validate required configuration before startup."""
    if not settings.is_fully_configured:
        missing = settings.get_missing_config()
        logger.error("Missing required configuration:")
        for item in missing:
            logger.error(f"  - {item}")
        logger.error(
            "\nPlease check your .env file and ensure all required API keys are set."
        )
        logger.error("See README.md for configuration instructions.")
        return False
    return True


def display_startup_info():
    """Display startup information."""
    logger.info("=" * 60)
    logger.info(f"{settings.app.app_name} v{settings.app.app_version}")
    logger.info(f"{settings.app.app_copyright}")
    logger.info("Clean and Readable Implementation")
    logger.info("=" * 60)
    logger.info(f"LLM Provider: {settings.llm.llm_provider}")
    logger.info(
        f"Model: {settings.llm.groq_model if settings.llm.llm_provider == 'groq' else settings.llm.openai_model}"
    )
    logger.info(f"Vector Store: {settings.vector.vector_store_type}")
    logger.info(f"Server: http://{settings.api.api_host}:{settings.api.api_port}")
    logger.info("=" * 60)


def main():
    """Main entry point."""
    try:
        # Display startup info
        display_startup_info()

        # Initialize watermark protection
        initialize_watermark()

        # Validate configuration
        if not validate_configuration():
            logger.error("Configuration validation failed. Exiting.")
            sys.exit(1)

        # Start the application
        logger.info("Starting server...")

        uvicorn.run(
            "src.api.main:app",
            host=settings.api.api_host,
            port=settings.api.api_port,
            reload=settings.app.is_development,
            log_level=settings.logging.log_level.lower(),
            access_log=not settings.app.is_production,
        )

    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
        sys.exit(0)
    except (ImportError, RuntimeError, OSError) as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
