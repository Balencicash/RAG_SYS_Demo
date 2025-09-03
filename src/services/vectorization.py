"""
Clean Vectorization Service with Ollama Embeddings.
Simplified text chunking and vector store operations using Ollama.
"""

from typing import List, Dict, Any, Tuple, Optional
import hashlib
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

from src.core.exceptions import VectorStoreError, ConfigurationError
from src.utils.watermark import protect_class
from config.settings import settings


@protect_class
class TextChunker:
    """Clean text chunking service."""

    def __init__(
        self, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None
    ):
        config = settings.vector
        self.chunk_size = chunk_size or config.chunk_size
        self.chunk_overlap = chunk_overlap or config.chunk_overlap

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
        )

    def chunk_text(
        self, text: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """Split text into chunks with metadata."""
        if not text or not text.strip():
            return []

        base_metadata = metadata or {}
        chunks = self.text_splitter.split_text(text)

        documents = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = base_metadata.copy()
            chunk_metadata.update(
                {
                    "chunk_index": i,
                    "chunk_hash": hashlib.md5(chunk.encode()).hexdigest()[:8],
                    "chunk_size": len(chunk),
                }
            )

            documents.append(Document(page_content=chunk, metadata=chunk_metadata))

        return documents

    def get_chunk_stats(self, documents: List[Document]) -> Dict[str, Any]:
        """Get statistics about the chunks."""
        if not documents:
            return {"total_chunks": 0, "total_chars": 0, "avg_chunk_size": 0}

        total_chars = sum(len(doc.page_content) for doc in documents)
        return {
            "total_chunks": len(documents),
            "total_chars": total_chars,
            "avg_chunk_size": total_chars // len(documents),
            "min_chunk_size": min(len(doc.page_content) for doc in documents),
            "max_chunk_size": max(len(doc.page_content) for doc in documents),
        }


@protect_class
class VectorStoreManager:
    """Clean vector store management."""

    def __init__(self):
        self.vector_store: Optional[FAISS] = None
        self.embeddings = self._initialize_embeddings()
        self.config = settings.vector

    def _initialize_embeddings(self) -> OllamaEmbeddings:
        """Initialize Ollama embeddings."""
        try:
            return OllamaEmbeddings(
                model=settings.llm.ollama_embedding_model,
                base_url=settings.llm.ollama_host,
            )
        except Exception as e:
            raise VectorStoreError(
                f"Failed to initialize Ollama embeddings: {str(e)}",
                operation="initialize_embeddings",
            ) from e

    def create_vector_store(self, documents: List[Document]) -> None:
        """Create new FAISS vector store from documents."""
        if not documents:
            raise VectorStoreError(
                "No documents provided for vector store creation",
                operation="create_vector_store",
            )

        try:
            self.vector_store = FAISS.from_documents(
                documents=documents, embedding=self.embeddings
            )
        except Exception as e:
            raise VectorStoreError(
                f"Failed to create vector store: {str(e)}",
                operation="create_vector_store",
            ) from e

    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to existing vector store."""
        if not self.vector_store:
            self.create_vector_store(documents)
            return

        if not documents:
            return

        try:
            self.vector_store.add_documents(documents)
        except Exception as e:
            raise VectorStoreError(
                f"Failed to add documents: {str(e)}", operation="add_documents"
            ) from e

    def similarity_search(self, query: str, k: Optional[int] = None) -> List[Document]:
        """Perform similarity search."""
        if not self.vector_store:
            raise VectorStoreError(
                "Vector store not initialized", operation="similarity_search"
            )

        k = k or self.config.top_k_results

        try:
            return self.vector_store.similarity_search(query, k=k)
        except Exception as e:
            raise VectorStoreError(
                f"Similarity search failed: {str(e)}", operation="similarity_search"
            ) from e

    def similarity_search_with_score(
        self, query: str, k: Optional[int] = None
    ) -> List[Tuple[Document, float]]:
        """Perform similarity search with relevance scores."""
        if not self.vector_store:
            raise VectorStoreError(
                "Vector store not initialized", operation="similarity_search_with_score"
            )

        k = k or self.config.top_k_results

        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            # Add relevance score to metadata
            for doc, score in results:
                doc.metadata["relevance_score"] = float(score)
            return results
        except Exception as e:
            raise VectorStoreError(
                f"Similarity search with score failed: {str(e)}",
                operation="similarity_search_with_score",
            ) from e

    def save_index(self, path: str) -> None:
        """Save FAISS index to disk."""
        if not self.vector_store:
            raise VectorStoreError("No vector store to save", operation="save_index")

        try:
            index_path = Path(path)
            index_path.mkdir(parents=True, exist_ok=True)
            self.vector_store.save_local(str(index_path))
        except Exception as e:
            raise VectorStoreError(
                f"Failed to save vector index: {str(e)}", operation="save_index"
            ) from e

    def load_index(self, path: str) -> None:
        """Load FAISS index from disk."""
        try:
            self.vector_store = FAISS.load_local(
                path, self.embeddings, allow_dangerous_deserialization=True
            )
        except Exception as e:
            raise VectorStoreError(
                f"Failed to load vector index: {str(e)}", operation="load_index"
            ) from e

    def get_store_info(self) -> Dict[str, Any]:
        """Get information about the vector store."""
        if not self.vector_store:
            return {"initialized": False}

        # Get basic info (note: FAISS doesn't expose document count easily)
        return {
            "initialized": True,
            "embedding_model": settings.llm.embedding_model,
            "embedding_dimension": settings.vector.embedding_dimension,
        }

    def clear(self) -> None:
        """Clear the vector store."""
        self.vector_store = None


# Global instances
text_chunker = TextChunker()
vector_store = VectorStoreManager()
