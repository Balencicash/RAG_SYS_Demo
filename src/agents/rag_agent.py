"""
RAG Agent using LangGraph with Watermark Protection
Copyright (c) 2025 BalenciCash - All Rights Reserved
"""

from typing import Dict, Any, List, TypedDict, Annotated, Optional
from enum import Enum
import operator
import uuid

from langgraph.graph import StateGraph, END
from langchain.tools import tool
from langchain.schema import Document

from src.utils.logger import logger
from src.utils.watermark import protect, protect_class, watermark
from src.services.document_parser import document_parser_service
from src.services.vectorization import text_chunker, vector_store_service
from src.services.llm_service import llm_service


class AgentState(TypedDict):
    """State definition for RAG agent with watermark."""

    session_id: str
    query: str
    standalone_query: str
    documents: List[Document]
    answer: Dict[str, Any]
    error: str
    metadata: Dict[str, Any]
    watermark: str


@protect_class
class RAGAgent:
    """
    RAG Agent orchestrated with LangGraph.
    Copyright (c) 2024 Balenci Cash
    Protected by digital watermark.
    """

    def __init__(self):
        self.author = "Balenci Cash"
        self.agent_id = "BC-RAG-AGENT-2024"
        self.graph = None
        self._build_graph()
        logger.info(f"RAG Agent initialized - Author: {self.author}")

    def _build_graph(self):
        """Build the LangGraph workflow with watermark nodes."""

        # Create the graph
        workflow = StateGraph(AgentState)

        # Add nodes with watermark protection
        workflow.add_node("add_watermark", self.add_watermark_node)
        workflow.add_node("process_query", self.process_query_node)
        workflow.add_node("retrieve_documents", self.retrieve_documents_node)
        workflow.add_node("generate_answer", self.generate_answer_node)
        workflow.add_node("finalize_response", self.finalize_response_node)

        # Define edges
        workflow.set_entry_point("add_watermark")
        workflow.add_edge("add_watermark", "process_query")
        workflow.add_edge("process_query", "retrieve_documents")
        workflow.add_edge("retrieve_documents", "generate_answer")
        workflow.add_edge("generate_answer", "finalize_response")
        workflow.add_edge("finalize_response", END)

        # Compile the graph
        self.graph = workflow.compile()
        logger.info("LangGraph workflow compiled successfully")

    @protect
    def add_watermark_node(self, state: AgentState) -> AgentState:
        """Add watermark to the agent state."""
        state["watermark"] = f"{self.author}:{watermark._signature_hash[:16]}"
        state["metadata"] = {
            "agent_id": self.agent_id,
            "author": self.author,
            "protected": True,
        }
        logger.debug(f"Watermark added to state: {state['watermark']}")
        return state

    @protect
    def process_query_node(self, state: AgentState) -> AgentState:
        """Process query and generate standalone question if needed."""
        try:
            query = state["query"]
            session_id = state.get("session_id")

            if session_id:
                # Generate standalone question for better retrieval
                standalone = llm_service.generate_standalone_question(query, session_id)
                state["standalone_query"] = standalone
            else:
                state["standalone_query"] = query

            logger.info(f"Query processed: {state['standalone_query'][:50]}...")
            return state

        except Exception as e:
            state["error"] = str(e)
            logger.error(f"Error processing query: {e}")
            return state

    @protect
    def retrieve_documents_node(self, state: AgentState) -> AgentState:
        """Retrieve relevant documents from vector store."""
        try:
            query = state.get("standalone_query", state["query"])

            # Perform similarity search with scores
            results = vector_store_service.similarity_search_with_score(query)

            # Extract documents and add retrieval metadata
            documents = []
            for doc, score in results:
                doc.metadata["retrieval_score"] = score
                doc.metadata["retrieved_by"] = self.author
                documents.append(doc)

            state["documents"] = documents
            logger.info(f"Retrieved {len(documents)} documents")
            return state

        except Exception as e:
            state["error"] = str(e)
            logger.error(f"Error retrieving documents: {e}")
            return state

    @protect
    def generate_answer_node(self, state: AgentState) -> AgentState:
        """Generate answer using LLM with retrieved context."""
        try:
            if not state.get("documents"):
                state["error"] = "No documents retrieved"
                return state

            # Generate answer
            answer = llm_service.generate_answer(
                query=state["query"],
                context_documents=state["documents"],
                session_id=state.get("session_id"),
            )

            state["answer"] = answer
            logger.info("Answer generated successfully")
            return state

        except Exception as e:
            state["error"] = str(e)
            logger.error(f"Error generating answer: {e}")
            return state

    @protect
    def finalize_response_node(self, state: AgentState) -> AgentState:
        """Finalize response with watermark and metadata."""

        # Add final watermark to answer
        if state.get("answer"):
            state["answer"]["agent_metadata"] = {
                "agent_id": self.agent_id,
                "author": self.author,
                "watermark": state["watermark"],
                "graph_execution": "complete",
            }

        # Log execution summary
        logger.success(
            f"RAG Agent execution complete - Session: {state.get('session_id', 'none')}"
        )
        return state

    @protect
    def process_question(
        self, query: str, session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main entry point to process a question through the RAG pipeline.
        """

        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())

        # Initialize state
        initial_state = {
            "session_id": session_id,
            "query": query,
            "standalone_query": "",
            "documents": [],
            "answer": {},
            "error": "",
            "metadata": {},
            "watermark": "",
        }

        try:
            # Execute the graph
            logger.info(f"Starting RAG pipeline for query: {query[:50]}...")
            final_state = self.graph.invoke(initial_state)

            # Check for errors
            if final_state.get("error"):
                return {
                    "success": False,
                    "error": final_state["error"],
                    "session_id": session_id,
                    "watermark": final_state.get("watermark"),
                }

            # Return successful response
            return {
                "success": True,
                "answer": final_state["answer"],
                "session_id": session_id,
                "watermark": final_state.get("watermark"),
            }

        except Exception as e:
            logger.error(f"RAG pipeline failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "watermark": f"{self.author}:{watermark._signature_hash[:8]}",
            }

    @protect
    def visualize_graph(self) -> str:
        """Generate a visual representation of the graph."""
        try:
            # Get graph structure
            graph_repr = f"""
RAG Agent Graph Structure
Author: {self.author}
Agent ID: {self.agent_id}

Nodes:
1. add_watermark -> Add watermark protection
2. process_query -> Process and enhance query
3. retrieve_documents -> Vector similarity search
4. generate_answer -> LLM answer generation
5. finalize_response -> Add final metadata

Flow:
add_watermark -> process_query -> retrieve_documents -> generate_answer -> finalize_response -> END

Protected by: {watermark._signature_hash[:16]}
"""
            return graph_repr
        except Exception as e:
            logger.error(f"Failed to visualize graph: {e}")
            return "Graph visualization failed"


# Create agent instance
rag_agent = RAGAgent()


# Export convenience function
@protect
def ask_question(query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to ask a question through the RAG agent."""
    return rag_agent.process_question(query, session_id)
