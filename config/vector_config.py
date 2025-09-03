"""
Vector Store Configuration for RAG Document QA System.
"""

from pathlib import Path
from pydantic_settings import BaseSettings


class VectorConfig(BaseSettings):
    """Vector store configuration settings."""

    # Vector Store Settings
    vector_store_type: str = "faiss"
    vector_store_path: Path = Path("./vector_stores")

    # Text Chunking Parameters
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Retrieval Parameters
    top_k_results: int = 5
    similarity_threshold: float = 0.7

    # Embedding Configuration
    embedding_dimension: int = 1536  # For text-embedding-ada-002

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }

    def __post_init__(self):
        """Ensure vector store directory exists."""
        self.vector_store_path.mkdir(parents=True, exist_ok=True)

    @property
    def chunk_settings(self) -> dict:
        """Get chunking configuration as dict."""
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
        }

    @property
    def retrieval_settings(self) -> dict:
        """Get retrieval configuration as dict."""
        return {
            "k": self.top_k_results,
            "score_threshold": self.similarity_threshold,
        }
