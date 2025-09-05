"""
Unified Exception Handling for RAG Document QA System.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException
from loguru import logger


class RAGException(Exception):
    """Base exception for RAG system."""

    def __init__(
        self,
        message: str,
        code: str = "RAG_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class DocumentParsingError(RAGException):
    """Exception raised during document parsing."""

    def __init__(
        self,
        message: str,
        file_path: str = "",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, "DOCUMENT_PARSING_ERROR", details)
        self.file_path = file_path


class VectorStoreError(RAGException):
    """Exception raised during vector store operations."""

    def __init__(
        self,
        message: str,
        operation: str = "",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, "VECTOR_STORE_ERROR", details)
        self.operation = operation


class LLMServiceError(RAGException):
    """Exception raised during LLM operations."""

    def __init__(
        self, message: str, model: str = "", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "LLM_SERVICE_ERROR", details)
        self.model = model


class ConfigurationError(RAGException):
    """Exception raised for configuration issues."""

    def __init__(
        self,
        message: str,
        config_key: str = "",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, "CONFIGURATION_ERROR", details)
        self.config_key = config_key


class ErrorHandler:
    """Centralized error handler for the RAG system."""

    @staticmethod
    def log_error(error: Exception, context: str = "") -> None:
        """Log error with context."""
        if isinstance(error, RAGException):
            logger.error(f"[{error.code}] {context}: {error.message}")
            if error.details:
                logger.error(f"Error details: {error.details}")
        else:
            logger.error(f"{context}: {str(error)}")

    @staticmethod
    def to_http_exception(error: Exception) -> HTTPException:
        """Convert RAG exception to HTTP exception."""
        if isinstance(error, DocumentParsingError):
            return HTTPException(
                status_code=400,
                detail={
                    "error": error.code,
                    "message": error.message,
                    "file_path": error.file_path,
                },
            )
        elif isinstance(error, VectorStoreError):
            return HTTPException(
                status_code=500,
                detail={
                    "error": error.code,
                    "message": error.message,
                    "operation": error.operation,
                },
            )
        elif isinstance(error, LLMServiceError):
            return HTTPException(
                status_code=503,
                detail={
                    "error": error.code,
                    "message": error.message,
                    "model": error.model,
                },
            )
        elif isinstance(error, ConfigurationError):
            return HTTPException(
                status_code=500,
                detail={
                    "error": error.code,
                    "message": error.message,
                    "config_key": error.config_key,
                },
            )
        else:
            return HTTPException(
                status_code=500,
                detail={
                    "error": "INTERNAL_ERROR",
                    "message": str(error),
                },
            )

    @staticmethod
    def handle_and_raise_http(error: Exception, context: str = "") -> None:
        """Log error and raise as HTTP exception."""
        ErrorHandler.log_error(error, context)
        raise ErrorHandler.to_http_exception(error)


# Convenience functions
def handle_error(error: Exception, context: str = "") -> None:
    """Log error without raising."""
    ErrorHandler.log_error(error, context)


def handle_error_and_raise(error: Exception, context: str = "") -> None:
    """Log error and re-raise as HTTP exception."""
    ErrorHandler.handle_and_raise_http(error, context)
