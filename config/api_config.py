"""
API Configuration for RAG Document QA System.
"""

from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings


class APIConfig(BaseSettings):
    """API configuration settings."""

    # Server Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"

    # Application Info
    app_name: str = "RAG Document QA System"
    app_version: str = "1.0.0"
    app_description: str = "RAG-based Document Question Answering System"

    # File Upload Settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: List[str] = [".pdf", ".docx", ".md", ".txt"]
    upload_dir: Path = Path("./uploads")

    # CORS Settings
    cors_origins: List[str] = ["*"]
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]

    # Security Settings
    enable_auth: bool = False
    api_key_header: str = "X-API-Key"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }

    def __post_init__(self):
        """Ensure upload directory exists."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    @property
    def cors_config(self) -> dict:
        """Get CORS configuration as dict."""
        return {
            "allow_origins": self.cors_origins,
            "allow_credentials": True,
            "allow_methods": self.cors_methods,
            "allow_headers": self.cors_headers,
        }

    @property
    def file_upload_config(self) -> dict:
        """Get file upload configuration as dict."""
        return {
            "max_size": self.max_file_size,
            "allowed_extensions": self.allowed_extensions,
            "upload_dir": self.upload_dir,
        }
