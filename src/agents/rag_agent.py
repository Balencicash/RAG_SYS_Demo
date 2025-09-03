"""
Clean RAG Agent with LangGraph.
Simplified workflow with clear separation of concerns.
"""

from typing import Dict, Any, List, Optional, Union, TypedDict
import uuid
import datetime

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.types import Command
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage
from langchain.schema import Document

from src.core.exceptions import handle_error
from src.services.vectorization import vector_store
from src.services.llm_service import llm_service
from src.utils.watermark import protect_class, watermark
from loguru import logger


class AgentState(TypedDict):
    """State for RAG agent workflow."""

    session_id: str
    query: str
    messages: List[Union[HumanMessage, AIMessage]]
    standalone_query: Optional[str]
    documents: Optional[List[Document]]
    answer: Optional[Dict[str, Any]]
    error: Optional[str]
    metadata: Optional[Dict[str, Any]]


@protect_class
class CleanRAGAgent:
    """Simplified RAG Agent with LangGraph workflow."""

    def __init__(self):
        self.graph = self._build_graph()
        logger.info("Clean RAG Agent initialized successfully")

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)

        # Create tool node
        tools = [self._retrieve_documents_tool, self._generate_standalone_tool]
        tool_node = ToolNode(tools, handle_tool_errors=True)

        # Add nodes
        workflow.add_node("initialize", self._initialize_node)
        workflow.add_node("process_query", self._process_query_node)
        workflow.add_node("tools", tool_node)
        workflow.add_node("generate_answer", self._generate_answer_node)
        workflow.add_node("finalize", self._finalize_node)

        # Define workflow
        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "process_query")
        workflow.add_conditional_edges(
            "process_query",
            self._should_continue,
            {"continue": "tools", "error": "finalize"},
        )
        workflow.add_conditional_edges(
            "tools",
            self._should_continue,
            {"continue": "generate_answer", "error": "finalize"},
        )
        workflow.add_edge("generate_answer", "finalize")
        workflow.add_edge("finalize", END)

        return workflow.compile()

    def _should_continue(self, state: AgentState) -> str:
        """Decide whether to continue or handle error."""
        return "error" if state.get("error") else "continue"

    def _initialize_node(self, state: AgentState) -> AgentState:
        """Initialize the agent state."""
        try:
            state["metadata"] = {
                "agent": "CleanRAGAgent",
                "timestamp": datetime.datetime.now().isoformat(),
                "watermark": watermark.get_metadata(),
            }
            return state
        except Exception as e:
            handle_error(e, "initialize_node")
            state["error"] = str(e)
            return state

    def _process_query_node(self, state: AgentState) -> AgentState:
        """Process the query and prepare for retrieval."""
        try:
            query = state["query"]
            messages = state.get("messages", [])

            # Add query to messages
            messages.append(HumanMessage(content=query))
            state["messages"] = messages

            # Generate standalone query if we have conversation history
            if len(messages) > 1:  # More than just current query
                standalone = self._generate_standalone_tool.invoke(
                    {"query": query, "session_id": state["session_id"]}
                )
                if standalone.get("success"):
                    state["standalone_query"] = standalone["standalone_query"]

            return state
        except Exception as e:
            handle_error(e, "process_query_node")
            state["error"] = str(e)
            return state

    def _generate_answer_node(self, state: AgentState) -> AgentState:
        """Generate answer using LLM."""
        try:
            documents = state.get("documents", [])
            if not documents:
                state["error"] = "No relevant documents found"
                return state

            # Generate answer
            answer = llm_service.generate_answer(
                query=state["query"],
                context_documents=documents,
                session_id=state.get("session_id"),
            )

            # Create AI message
            ai_message = AIMessage(
                content=answer["text"],
                additional_kwargs={
                    "sources": answer.get("sources", []),
                    "metadata": answer.get("metadata", {}),
                },
            )

            state["answer"] = answer
            state["messages"].append(ai_message)

            return state
        except Exception as e:
            handle_error(e, "generate_answer_node")
            state["error"] = str(e)
            return state

    def _finalize_node(self, state: AgentState) -> AgentState:
        """Finalize the response."""
        try:
            if state.get("error"):
                # Create error response
                error_message = AIMessage(
                    content="I apologize, but I encountered an error processing your request.",
                    additional_kwargs={
                        "error": state["error"],
                        "metadata": state.get("metadata", {}),
                    },
                )
                state["messages"].append(error_message)
            else:
                # Add final metadata
                if state.get("answer"):
                    state["answer"]["agent_metadata"] = {
                        "workflow_completed": True,
                        "document_count": len(state.get("documents", [])),
                        "has_standalone_query": bool(state.get("standalone_query")),
                        **state.get("metadata", {}),
                    }

            return state
        except Exception as e:
            handle_error(e, "finalize_node")
            state["error"] = str(e)
            return state

    @tool
    def _generate_standalone_tool(self, query: str, session_id: str) -> Dict[str, Any]:
        """Generate standalone question tool."""
        try:
            standalone = llm_service.generate_standalone_question(query, session_id)
            return {"success": True, "standalone_query": standalone}
        except Exception as e:
            handle_error(e, "generate_standalone_tool")
            return {"success": False, "error": str(e)}

    @tool
    def _retrieve_documents_tool(self, query: str) -> Dict[str, Any]:
        """Retrieve documents tool."""
        try:
            results = vector_store.similarity_search_with_score(query)
            documents = [doc for doc, score in results]

            return {"success": True, "documents": documents, "count": len(documents)}
        except Exception as e:
            handle_error(e, "retrieve_documents_tool")
            return {"success": False, "error": str(e)}

    def process_question(
        self,
        query: str,
        session_id: Optional[str] = None,
        previous_messages: Optional[List[Union[HumanMessage, AIMessage]]] = None,
    ) -> Dict[str, Any]:
        """Process a question through the RAG pipeline."""
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = str(uuid.uuid4())

            # Initialize state
            initial_state = AgentState(
                session_id=session_id, query=query, messages=previous_messages or []
            )

            # Execute graph
            final_state = self.graph.invoke(initial_state)

            # Format response
            response = {
                "success": not bool(final_state.get("error")),
                "session_id": session_id,
                "messages": final_state.get("messages", []),
            }

            if final_state.get("error"):
                response.update(
                    {"error": final_state["error"], "error_type": "workflow_error"}
                )
            else:
                response.update(
                    {
                        "answer": final_state.get("answer"),
                        "documents": [
                            {"content": doc.page_content, "metadata": doc.metadata}
                            for doc in final_state.get("documents", [])
                        ],
                    }
                )

            return response

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
            "name": "CleanRAGAgent",
            "author": watermark.author,
            "nodes": [
                "initialize",
                "process_query",
                "tools",
                "generate_answer",
                "finalize",
            ],
            "tools": ["generate_standalone_tool", "retrieve_documents_tool"],
        }


# Global instance
rag_agent = CleanRAGAgent()


# Convenience functions
def ask_question(query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to ask a question."""
    return rag_agent.process_question(query, session_id)
