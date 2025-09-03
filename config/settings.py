"""
Unified Configuration settings for RAG Document QA System.
Clean and readable configuration management.
"""

from pathlib import Path
from pydantic_settings import BaseSettings

from .llm_config import LLMConfig
from .vector_config import VectorConfig
from .api_config import APIConfig
from .comfyui_config import ComfyUIConfig


class LoggingConfig(BaseSettings):
    """Logging configuration."""

    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    log_rotation: str = "10 MB"
    log_retention: str = "7 days"
    log_format: str = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


class AppSettings(BaseSettings):
    """Main application settings."""

    # Application Identity
    app_name: str = "RAG Document QA System"
    app_version: str = "1.0.0"
    app_author: str = "BalenciCash"
    app_copyright: str = "Copyright (c) 2025 BalenciCash - All Rights Reserved"
    app_description: str = "RAG-based Document Question Answering System"

    # Environment
    environment: str = "development"
    debug: bool = False

    # Security & Watermark (simplified)
    enable_watermark: bool = True
    watermark_signature: str = "BC-RAG-2024"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment.lower() == "development"


class Settings:
    """Unified settings container."""

    def __init__(self):
        self.app = AppSettings()
        self.llm = LLMConfig()
        self.vector = VectorConfig()
        self.api = APIConfig()
        self.comfyui = ComfyUIConfig()
        self.logging = LoggingConfig()

        # Create necessary directories
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            self.api.upload_dir,
            self.vector.vector_store_path,
            Path("logs"),
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @property
    def is_fully_configured(self) -> bool:
        """Check if all required configurations are set."""
        return (
            self.llm.is_groq_configured or self.llm.is_openai_configured
        ) and self.llm.is_openai_configured  # Need OpenAI for embeddings

    def get_missing_config(self) -> list:
        """Get list of missing required configurations."""
        missing = []

        if not (self.llm.is_groq_configured or self.llm.is_openai_configured):
            missing.append("LLM API key (GROQ_API_KEY or OPENAI_API_KEY)")

        if not self.llm.is_openai_configured:
            missing.append("OpenAI API key for embeddings (OPENAI_API_KEY)")

        return missing


# Initialize global settings instance
settings = Settings()
