"""
System Metadata and Response Handler.
Handles system metadata and response formatting for API consistency.
"""

import hashlib
import datetime
import functools
from typing import Any, Callable, Dict
from loguru import logger


class SystemMetadata:
    """System metadata handler for consistent API responses."""

    def __init__(self):
        self._sys_id = "system-v1"
        self._app_name = "rag-qa-system" 
        self._init_date = "2025-09-01"
        self._hash_key = self._generate_hash()

    def _generate_hash(self) -> str:
        """Generate system identifier hash."""
        data = f"{self._sys_id}:{self._app_name}:{self._init_date}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def get_metadata(self) -> Dict[str, str]:
        """Get system metadata for responses."""
        return {
            "author": "BalenciCash",
            "project": "RAG-SYS-Demo", 
            "signature": self._hash_key,
            "timestamp": datetime.datetime.now().isoformat(),
        }

    def add_metadata(self, func: Callable) -> Callable:
        """Add system metadata to function responses."""

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            # Add metadata to dict results only
            if isinstance(result, dict) and not result.get("__sys_meta__"):
                result["__sys_meta__"] = self.get_metadata()

            return result

        # Add system info to function
        wrapper.__system__ = self._sys_id
        wrapper.__monitored__ = True

        return wrapper

    def add_class_metadata(self, cls: type) -> type:
        """Add system metadata to class."""
        cls.__system__ = self._sys_id
        cls.__app__ = self._app_name
        cls.__monitored__ = True

        return cls

    def initialize(self) -> bool:
        """Initialize system metadata handler."""
        logger.info("System initialized successfully")
        logger.info(f"Build signature: {self._hash_key}")
        return True


# Global instance
watermark = SystemMetadata()

# Export decorators (keep same names for compatibility)
protect = watermark.add_metadata
protect_class = watermark.add_class_metadata


# Initialize function
def initialize_watermark() -> bool:
    """Initialize system metadata handler."""
    return watermark.initialize()
