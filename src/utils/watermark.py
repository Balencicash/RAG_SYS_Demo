"""
Simplified Watermark Protection System.
Clean and minimal implementation that doesn't interfere with core logic.
"""

import hashlib
import datetime
import functools
from typing import Any, Callable, Dict
from loguru import logger


class SimpleWatermark:
    """Simplified watermark system for code protection."""

    def __init__(self):
        self.author = "BalenciCash"
        self.project_id = "RAG-SYS-Demo"
        self.creation_date = "2025-09-01"
        self._signature = self._generate_signature()

    def _generate_signature(self) -> str:
        """Generate unique signature hash."""
        data = f"{self.author}:{self.project_id}:{self.creation_date}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def get_metadata(self) -> Dict[str, str]:
        """Get watermark metadata."""
        return {
            "author": self.author,
            "project": self.project_id,
            "signature": self._signature,
            "timestamp": datetime.datetime.now().isoformat(),
        }

    def protect_function(self, func: Callable) -> Callable:
        """Simple function protection decorator."""

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            # Add watermark to dict results only
            if isinstance(result, dict) and not result.get("__watermark__"):
                result["__watermark__"] = self.get_metadata()

            return result

        # Add metadata to function
        wrapper.__author__ = self.author
        wrapper.__protected__ = True

        return wrapper

    def protect_class(self, cls: type) -> type:
        """Simple class protection."""
        cls.__author__ = self.author
        cls.__project__ = self.project_id
        cls.__protected__ = True

        return cls

    def initialize(self) -> bool:
        """Initialize watermark system."""
        logger.info(f"RAG System initialized - Author: {self.author}")
        logger.info(f"Project: {self.project_id} | Signature: {self._signature}")
        return True


# Global instance
watermark = SimpleWatermark()

# Export decorators
protect = watermark.protect_function
protect_class = watermark.protect_class


# Initialize function
def initialize_watermark() -> bool:
    """Initialize watermark protection."""
    return watermark.initialize()
