"""
Clean RAG Agent - Simplified without LangGraph.
Direct workflow implementation with clear separation of concerns.
"""

import os
from typing import Dict, Any, List, Optional, Union
import uuid
import datetime

from langchain_core.messages import AIMessage, HumanMessage
from langchain.callbacks.tracers import LangChainTracer as LangSmithTracer

from src.core.exceptions import handle_error
from src.services.vectorization import vector_store
from src.services.llm_service import llm_service
from src.utils.metadata import protect_class, watermark as sys_meta
from config.settings import settings
from loguru import logger


@protect_class
class CleanRAGAgent:
    """Simplified RAG Agent without LangGraph workflow."""

    def __init__(self):
        self.tracer = self._initialize_tracer()
        logger.info("Clean RAG Agent initialized successfully")
        if self.tracer:
            logger.info("LangSmith tracing enabled for RAG workflow")

    def _initialize_tracer(self) -> Optional[LangSmithTracer]:
        """Initialize LangSmith tracer for RAG workflow tracking."""
        llm_config = settings.llm

        if llm_config.langchain_tracing_v2 and llm_config.langchain_api_key:
            try:
                # Set environment variables for LangSmith
                os.environ["LANGCHAIN_TRACING_V2"] = "true"
                os.environ["LANGCHAIN_ENDPOINT"] = llm_config.langchain_endpoint
                os.environ["LANGCHAIN_API_KEY"] = llm_config.langchain_api_key
                os.environ["LANGCHAIN_PROJECT"] = llm_config.langchain_project

                # Initialize tracer for RAG workflow
                tracer = LangSmithTracer(
                    project_name=llm_config.langchain_project,
                    tags=["rag-workflow", "document-qa", "production"],
                )
                return tracer
            except Exception as e:
                logger.warning(f"Failed to initialize LangSmith tracer: {e}")
                return None
        return None

    def process_question(
        self,
        query: str,
        session_id: Optional[str] = None,
        previous_messages: Optional[List[Union[HumanMessage, AIMessage]]] = None,
    ) -> Dict[str, Any]:
        """Process a question through the RAG pipeline (simplified version)."""
        # Start RAG workflow tracing
        run_id = str(uuid.uuid4())

        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = str(uuid.uuid4())

            # Log RAG workflow start
            if self.tracer:
                self.tracer.on_chain_start(
                    {
                        "name": "rag_workflow",
                        "type": "rag_agent",
                        "tags": [
                            "rag-pipeline",
                            "document-retrieval",
                            "answer-generation",
                        ],
                    },
                    inputs={
                        "query": query,
                        "session_id": session_id,
                        "timestamp": datetime.datetime.now().isoformat(),
                    },
                    run_id=run_id,
                )

            # Step 1: Retrieve documents
            try:
                logger.info(f"Starting document retrieval for query: {query[:50]}...")
                results = vector_store.similarity_search_with_score(query)
                documents = [doc for doc, score in results]

                # Log retrieval results
                if self.tracer:
                    retrieval_metadata = {
                        "documents_found": len(documents),
                        "query": query,
                        "scores": [
                            float(score) for doc, score in results[:3]
                        ],  # Top 3 scores
                    }
                    self.tracer.on_retriever_end(
                        documents, run_id=run_id, metadata=retrieval_metadata
                    )

                if not documents:
                    error_msg = "No relevant documents found"
                    if self.tracer:
                        self.tracer.on_chain_error(
                            {"error": error_msg, "type": "retrieval_error"},
                            run_id=run_id,
                        )
                    return {
                        "success": False,
                        "error": error_msg,
                        "session_id": session_id,
                        "messages": previous_messages or [],
                    }

                # Step 2: Generate answer
                logger.info(
                    f"Generating answer with {len(documents)} retrieved documents"
                )
                answer = llm_service.generate_answer(
                    query=query,
                    context_documents=documents,
                    session_id=session_id,
                )

                # Log successful completion
                if self.tracer:
                    self.tracer.on_chain_end(
                        outputs={
                            "answer": answer["text"],
                            "sources_count": len(documents),
                            "session_id": session_id,
                        },
                        run_id=run_id,
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
                # Log processing error
                if self.tracer:
                    self.tracer.on_chain_error(
                        {"error": str(e), "type": "processing_error"}, run_id=run_id
                    )
                handle_error(e, "retrieve_or_generate")
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": "processing_error",
                    "session_id": session_id,
                    "messages": previous_messages or [],
                }

        except Exception as e:
            # Log workflow error
            if self.tracer:
                self.tracer.on_chain_error(
                    {"error": str(e), "type": "workflow_error"}, run_id=run_id
                )
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
