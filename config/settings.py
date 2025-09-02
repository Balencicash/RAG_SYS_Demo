"""
Configuration settings for RAG Document QA System
Copyright (c) 2025 BalenciCash - Protected Software
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with watermark protection."""

    # Application Info (Watermarked)
    APP_NAME: str = "RAG Document QA System"
    APP_VERSION: str = "1.0.0"
    APP_AUTHOR: str = "BalenciCash"
    APP_COPYRIGHT: str = "Copyright (c) 2025 BalenciCash - All Rights Reserved"

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"

    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = None  # Still needed for embeddings
    GROQ_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "groq"  # groq or openai
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    MAX_TOKENS: int = 500  # Reduced to save costs
    TEMPERATURE: float = 0.3  # Lower for more consistent outputs

    # LangSmith Configuration
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "rag-document-qa"

    # Vector Store Settings
    VECTOR_STORE_TYPE: str = "faiss"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5

    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list = [".pdf", ".docx", ".md", ".txt"]
    UPLOAD_DIR: Path = Path("./uploads")

    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_ROTATION: str = "10 MB"
    LOG_RETENTION: str = "7 days"

    # Security & Watermark
    ENABLE_WATERMARK: bool = True
    WATERMARK_SIGNATURE: str = "BC-RAG-2024"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


# Initialize settings
settings = Settings()

# Create directories if they don't exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
Path("logs").mkdir(exist_ok=True)
