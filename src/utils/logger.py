"""
Logging configuration with watermark protection
Copyright (c) 2024 Balenci Cash
"""

import sys
from loguru import logger
from config.settings import settings
from src.utils.watermark import watermark, protect

# Remove default handler
logger.remove()

# Add console handler with custom format
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
    level=settings.LOG_LEVEL,
    colorize=True
)

# Add file handler with rotation
logger.add(
    settings.LOG_FILE,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message} | Author: Balenci Cash",
    level=settings.LOG_LEVEL,
    rotation=settings.LOG_ROTATION,
    retention=settings.LOG_RETENTION,
    compression="zip"
)

@protect
def log_with_watermark(level: str, message: str, **kwargs):
    """Log message with embedded watermark."""
    watermark_msg = f"{message} [WM:{watermark._signature_hash[:8]}]"
    getattr(logger, level)(watermark_msg, **kwargs)

# Initialize watermark protection on import
logger.info(f"Logging system initialized - {settings.APP_COPYRIGHT}")
logger.info(f"Watermark Protection Active - Signature: {settings.WATERMARK_SIGNATURE}")

__all__ = ['logger', 'log_with_watermark']