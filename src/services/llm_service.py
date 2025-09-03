"""
Clean LLM Service - Groq Only.
Simplified LLM operations with Groq support and proper error handling.
"""

from typing import List, Dict, Any, Optional
import hashlib
from datetime import datetime

from langchain_groq import ChatGroq
from langchain.schema import Document, HumanMessage, SystemMessage, AIMessage
from langchain.callbacks import LangChainTracer

from src.core.exceptions import LLMServiceError, ConfigurationError
from src.utils.metadata import protect_class
from config.settings import settings


@protect_class
class ConversationMemory:
    """Simple conversation memory management."""

    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add message to conversation history."""
        if session_id not in self.conversations:
            self.conversations[session_id] = []

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }

        self.conversations[session_id].append(message)

        # Trim history if too long
        if len(self.conversations[session_id]) > self.max_history * 2:
            self.conversations[session_id] = self.conversations[session_id][
                -self.max_history * 2 :
            ]

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for session."""
        return self.conversations.get(session_id, [])

    def clear_session(self, session_id: str) -> None:
        """Clear conversation history for session."""
        if session_id in self.conversations:
            del self.conversations[session_id]

    def get_recent_messages(
        self, session_id: str, count: int = 6
    ) -> List[Dict[str, Any]]:
        """Get recent messages for context."""
        history = self.get_history(session_id)
        return history[-count:] if history else []


@protect_class
class LLMService:
    """Clean LLM service for answer generation - Groq only."""

    def __init__(self):
        self.llm = self._initialize_llm()
        self.memory = ConversationMemory()
        self.tracer = self._initialize_tracer()

    def _initialize_llm(self):
        """Initialize Groq LLM."""
        llm_config = settings.llm

        if not llm_config.groq_api_key:
            raise ConfigurationError(
                "Groq API key is required",
                config_key="GROQ_API_KEY",
            )

        try:
            return ChatGroq(
                model=llm_config.groq_model,
                temperature=llm_config.temperature,
                groq_api_key=llm_config.groq_api_key,
                max_tokens=llm_config.max_tokens,
            )
        except Exception as e:
            raise LLMServiceError(
                f"Failed to initialize Groq LLM: {str(e)}",
                model=llm_config.groq_model,
            ) from e

    def _initialize_tracer(self) -> Optional[LangChainTracer]:
        """Initialize LangSmith tracer if configured."""
        llm_config = settings.llm

        if llm_config.langchain_tracing_v2 and llm_config.langchain_api_key:
            try:
                return LangChainTracer(project_name=llm_config.langchain_project)
            except Exception:
                # If tracer fails, continue without it
                return None
        return None

    def generate_answer(
        self,
        query: str,
        context_documents: List[Document],
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate answer based on query and context documents."""

        # Build context from documents
        context_parts = []
        sources = []

        for i, doc in enumerate(context_documents):
            context_parts.append(f"[Source {i+1}]: {doc.page_content}")
            sources.append(
                {
                    "index": i + 1,
                    "content": (
                        doc.page_content[:200] + "..."
                        if len(doc.page_content) > 200
                        else doc.page_content
                    ),
                    "metadata": doc.metadata,
                }
            )

        context = "\n\n".join(context_parts)

        # Create prompt
        system_prompt = self._create_system_prompt(context)
        messages = [SystemMessage(content=system_prompt)]

        # Add conversation history if available
        if session_id:
            recent_messages = self.memory.get_recent_messages(session_id, count=6)
            for msg in recent_messages:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))

        # Add current query
        messages.append(HumanMessage(content=query))

        try:
            # Generate response
            if self.tracer:
                response = self.llm.invoke(messages, callbacks=[self.tracer])
            else:
                response = self.llm.invoke(messages)
            answer = response.content

            # Store in memory
            if session_id:
                self.memory.add_message(session_id, "user", query)
                self.memory.add_message(session_id, "assistant", answer)

            return {
                "text": answer,
                "sources": sources,
                "metadata": {
                    "model": self._get_current_model(),
                    "provider": "groq",
                    "context_docs_count": len(context_documents),
                    "timestamp": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            raise LLMServiceError(
                f"Failed to generate answer: {str(e)}", model=self._get_current_model()
            ) from e

    def generate_standalone_question(self, query: str, session_id: str) -> str:
        """Generate standalone question from query with conversation context."""
        history = self.memory.get_recent_messages(session_id, count=4)

        if not history:
            return query

        # Build conversation context
        conv_context = []
        for msg in history:
            conv_context.append(f"{msg['role']}: {msg['content']}")

        prompt = f"""Given the conversation history, rewrite the user's latest question to be standalone and self-contained.
Include all necessary context from the conversation.

Conversation History:
{chr(10).join(conv_context)}

Latest Question: {query}

Standalone Question:"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content.strip()
        except Exception as e:
            # If standalone generation fails, return original query
            return query

    def _create_system_prompt(self, context: str) -> str:
        """Create system prompt for answer generation."""
        return f"""Answer the user's question based on the provided context documents. 
Follow these guidelines:
1. Use only information from the provided context
2. Cite sources using [Source X] notation
3. Be concise and accurate
4. If the context doesn't contain enough information, say so clearly

Context Documents:
{context}

Instructions: Answer based on the context above. Always cite your sources."""

    def _get_current_model(self) -> str:
        """Get the current model name."""
        return settings.llm.groq_model

    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the LLM service."""
        return {
            "provider": "groq",
            "model": self._get_current_model(),
            "max_tokens": settings.llm.max_tokens,
            "temperature": settings.llm.temperature,
            "tracer_enabled": self.tracer is not None,
            "active_sessions": len(self.memory.conversations),
        }


# Global instance
llm_service = LLMService()
