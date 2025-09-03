"""
LLM Configuration for RAG Document QA System with Ollama support.
"""

from typing import Optional
from pydantic_settings import BaseSettings


class LLMConfig(BaseSettings):
    """LLM configuration settings."""

    # API Keys
    groq_api_key: Optional[str] = None

    # Ollama Configuration
    ollama_host: str = "http://localhost:11434"
    ollama_embedding_model: str = "nomic-embed-text"

    # Model Configuration
    llm_provider: str = "groq"  # groq only (removed openai)
    groq_model: str = "llama-3.1-8b-instant"

    # Generation Parameters
    max_tokens: int = 500
    temperature: float = 0.3

    # LangSmith Configuration
    langchain_tracing_v2: bool = True
    langchain_endpoint: str = "https://api.smith.langchain.com"
    langchain_api_key: Optional[str] = None
    langchain_project: str = "rag-document-qa"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }

    @property
    def is_groq_configured(self) -> bool:
        """Check if Groq is properly configured."""
        return bool(self.groq_api_key)

    @property
    def is_ollama_configured(self) -> bool:
        """Check if Ollama is properly configured."""
        return True  # Ollama runs locally, no API key needed

    @property
    def is_langsmith_configured(self) -> bool:
        """Check if LangSmith is properly configured."""
        return bool(self.langchain_api_key)
