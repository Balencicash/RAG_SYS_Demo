"""
Text Vectorization and Chunking Service
Copyright (c) 2024 Balenci Cash - Protected by Digital Watermark
"""

from typing import List, Dict, Any, Optional
import hashlib
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

from src.utils.logger import logger
from src.utils.watermark import protect, protect_class, watermark
from config.settings import settings


@protect_class
class TextChunker:
    """
    Text chunking service with watermark protection.
    Author: Balenci Cash
    """
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        self.author = "Balenci Cash"
        self.chunker_id = "BC-CHUNKER-2024"
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
        logger.info(f"Text Chunker initialized - Size: {self.chunk_size}, Overlap: {self.chunk_overlap}")
    
    @protect
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Document]:
        """
        Split text into chunks with metadata and watermark.
        """
        if not text:
            return []
        
        # Add watermark to metadata
        base_metadata = metadata or {}
        base_metadata.update({
            "chunked_by": self.author,
            "chunker_id": self.chunker_id,
            "watermark": watermark._signature_hash[:8]
        })
        
        # Create chunks
        chunks = self.text_splitter.split_text(text)
        
        # Create Document objects with metadata
        documents = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = base_metadata.copy()
            chunk_metadata.update({
                "chunk_index": i,
                "chunk_hash": hashlib.md5(chunk.encode()).hexdigest()[:8]
            })
            
            doc = Document(
                page_content=chunk,
                metadata=chunk_metadata
            )
            documents.append(doc)
        
        logger.info(f"Created {len(documents)} chunks from text")
        return documents


@protect_class
class VectorStoreService:
    """
    Vector store service using FAISS with watermark protection.
    Copyright (c) 2024 Balenci Cash
    """
    
    def __init__(self, embedding_model: str = None):
        self.embedding_model = embedding_model or settings.EMBEDDING_MODEL
        self.author = "Balenci Cash"
        self.service_id = "BC-VECTOR-2024"
        self.vector_store = None
        self.embeddings = None
        
        self._initialize_embeddings()
        logger.info(f"Vector Store Service initialized - Author: {self.author}")
    
    def _initialize_embeddings(self):
        """Initialize OpenAI embeddings with watermark."""
        try:
            self.embeddings = OpenAIEmbeddings(
                model=self.embedding_model,
                openai_api_key=settings.OPENAI_API_KEY
            )
            logger.info(f"Embeddings initialized with model: {self.embedding_model}")
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            raise
    
    @protect
    def create_vector_store(self, documents: List[Document]) -> FAISS:
        """
        Create FAISS vector store from documents with watermark.
        """
        if not documents:
            raise ValueError("No documents provided for vector store creation")
        
        # Add service watermark to all documents
        for doc in documents:
            doc.metadata.update({
                "vectorized_by": self.author,
                "vector_service": self.service_id,
                "vector_watermark": watermark._signature_hash[:12]
            })
        
        try:
            # Create FAISS index
            self.vector_store = FAISS.from_documents(
                documents=documents,
                embedding=self.embeddings
            )
            
            logger.success(f"Created vector store with {len(documents)} documents")
            return self.vector_store
            
        except Exception as e:
            logger.error(f"Failed to create vector store: {e}")
            raise
    
    @protect
    def add_documents(self, documents: List[Document]) -> None:
        """Add new documents to existing vector store."""
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Create it first.")
        
        # Add watermark to new documents
        for doc in documents:
            doc.metadata.update({
                "vectorized_by": self.author,
                "vector_service": self.service_id
            })
        
        self.vector_store.add_documents(documents)
        logger.info(f"Added {len(documents)} documents to vector store")
    
    @protect
    def similarity_search(self, query: str, k: int = None) -> List[Document]:
        """
        Perform similarity search with watermark tracking.
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        k = k or settings.TOP_K_RESULTS
        
        try:
            results = self.vector_store.similarity_search(query, k=k)
            
            # Add search watermark to results
            for result in results:
                result.metadata["search_watermark"] = f"{self.author}:{watermark._signature_hash[:6]}"
            
            logger.info(f"Similarity search completed - Found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            raise
    
    @protect
    def similarity_search_with_score(self, query: str, k: int = None) -> List[tuple]:
        """
        Perform similarity search with relevance scores.
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        k = k or settings.TOP_K_RESULTS
        
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            
            # Add watermark and format results
            watermarked_results = []
            for doc, score in results:
                doc.metadata["search_watermark"] = f"{self.author}:{watermark._signature_hash[:6]}"
                doc.metadata["relevance_score"] = float(score)
                watermarked_results.append((doc, score))
            
            logger.info(f"Similarity search with scores completed - {len(results)} results")
            return watermarked_results
            
        except Exception as e:
            logger.error(f"Similarity search with score failed: {e}")
            raise
    
    @protect
    def save_index(self, path: str) -> None:
        """Save FAISS index to disk with watermark."""
        if not self.vector_store:
            raise ValueError("No vector store to save")
        
        try:
            self.vector_store.save_local(path)
            
            # Save watermark file
            watermark_file = f"{path}/watermark.txt"
            with open(watermark_file, 'w') as f:
                f.write(f"Vector Index Protected by: {self.author}\n")
                f.write(f"Service ID: {self.service_id}\n")
                f.write(f"Watermark: {watermark._signature_hash}\n")
            
            logger.success(f"Vector index saved to {path}")
            
        except Exception as e:
            logger.error(f"Failed to save vector index: {e}")
            raise
    
    @protect
    def load_index(self, path: str) -> FAISS:
        """Load FAISS index from disk and verify watermark."""
        try:
            self.vector_store = FAISS.load_local(
                path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            
            # Verify watermark
            watermark_file = f"{path}/watermark.txt"
            if os.path.exists(watermark_file):
                with open(watermark_file, 'r') as f:
                    content = f.read()
                    if self.author in content:
                        logger.info(f"Watermark verified for index at {path}")
            
            logger.success(f"Vector index loaded from {path}")
            return self.vector_store
            
        except Exception as e:
            logger.error(f"Failed to load vector index: {e}")
            raise


# Create service instances
text_chunker = TextChunker()
vector_store_service = VectorStoreService()