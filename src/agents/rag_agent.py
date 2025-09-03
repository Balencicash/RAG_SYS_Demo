"""
Clean RAG Agent - Simplified without LangGraph.
Direct workflow implementation with clear separation of concerns.
"""

from typing import Dict, Any, List, Optional, Union
import uuid
import datetime

from langchain_core.messages import AIMessage, HumanMessage
from langchain.schema import Document

from src.core.exceptions import handle_error
from src.services.vectorization import vector_store
from src.services.llm_service import llm_service
from src.utils.metadata import protect_class, watermark as sys_meta
from loguru import logger


@protect_class
class CleanRAGAgent:
    """Simplified RAG Agent without LangGraph workflow."""

    def __init__(self):
        logger.info("Clean RAG Agent initialized successfully")

    def process_question(
        self,
        query: str,
        session_id: Optional[str] = None,
        previous_messages: Optional[List[Union[HumanMessage, AIMessage]]] = None,
    ) -> Dict[str, Any]:
        """Process a question through the RAG pipeline (simplified version)."""
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = str(uuid.uuid4())

            # Step 1: Retrieve documents
            try:
                results = vector_store.similarity_search_with_score(query)
                documents = [doc for doc, score in results]

                if not documents:
                    return {
                        "success": False,
                        "error": "No relevant documents found",
                        "session_id": session_id,
                        "messages": previous_messages or [],
                    }

                # Step 2: Generate answer
                answer = llm_service.generate_answer(
                    query=query,
                    context_documents=documents,
                    session_id=session_id,
                )

                # Format response
                return {
                    "success": True,
                    "session_id": session_id,
                    "answer": answer,
                    "documents": [
                        {"content": doc.page_content, "metadata": doc.metadata}
                        for doc in documents
                    ],
                    "messages": (previous_messages or [])
                    + [HumanMessage(content=query), AIMessage(content=answer["text"])],
                }

            except Exception as e:
                handle_error(e, "retrieve_or_generate")
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": "processing_error",
                    "session_id": session_id,
                    "messages": previous_messages or [],
                }

        except Exception as e:
            handle_error(e, "process_question")
            return {
                "success": False,
                "error": str(e),
                "error_type": "system_error",
                "session_id": session_id or str(uuid.uuid4()),
                "messages": previous_messages or [],
            }

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent."""
        return {
            "agent_type": "CleanRAGAgent",
            "version": "2.0",
            "simplified": True,
            "features": [
                "document_retrieval",
                "answer_generation",
                "session_management",
            ],
            "watermark": sys_meta.get_metadata(),
        }


# Global instance
rag_agent = CleanRAGAgent()


# Helper function for backward compatibility
def process_question(query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """Process a question using the global RAG agent instance."""
    return rag_agent.process_question(query, session_id)
