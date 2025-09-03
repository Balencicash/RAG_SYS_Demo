"""
Logging configuration with system metadata tracking
Copyright (c) 2024 Balenci Cash
"""

import sys
from loguru import logger
from config.settings import settings
from src.utils.metadata import watermark as sys_meta, protect as sys_protect

# Remove default handler
logger.remove()

# Add console handler with custom format
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
    level=settings.logging.log_level,
    colorize=True,
)

# Add file handler with rotation
logger.add(
    settings.logging.log_file,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message} | Author: Balenci Cash",
    level=settings.logging.log_level,
    rotation=settings.logging.log_rotation,
    retention=settings.logging.log_retention,
    compression="zip",
)


@sys_protect
def log_with_sys_meta(level: str, message: str, **kwargs):
    """Log message with embedded sys_meta."""
    # Get sys_meta signature safely
    try:
        signature = getattr(sys_meta, "project_id", "WM")[:8]
        sys_meta_msg = f"{message} [WM:{signature}]"
    except Exception:
        sys_meta_msg = f"{message} [WM:protected]"
    getattr(logger, level)(sys_meta_msg, **kwargs)


@sys_protect
def get_logger(name: str = None):
    """Get logger instance with optional name."""
    if name:
        return logger.bind(name=name)
    return logger


# Initialize sys_meta protection on import
logger.info(f"Logging system initialized - {settings.app.app_copyright}")
logger.info(f"System Metadata Active - Signature: {settings.app.system_signature}")

__all__ = ["logger", "log_with_sys_meta", "get_logger"]
