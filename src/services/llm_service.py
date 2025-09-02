"""
LLM Service for Answer Generation with Watermark Protection
Copyright (c) 2024 Balenci Cash - All Rights Reserved
"""

from typing import List, Dict, Any, Optional
import json
import hashlib
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.schema import Document, HumanMessage, SystemMessage, AIMessage
from langchain.callbacks import LangChainTracer
from langchain.prompts import ChatPromptTemplate

from src.utils.logger import logger
from src.utils.watermark import protect, protect_class, watermark
from config.settings import settings


@protect_class
class ConversationMemory:
    """
    Conversation memory management with watermark protection.
    Author: Balenci Cash
    """
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.conversations = {}
        self.author = "Balenci Cash"
        self.memory_id = "BC-MEMORY-2024"
    
    @protect
    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add message to conversation history with watermark."""
        if session_id not in self.conversations:
            self.conversations[session_id] = {
                "messages": [],
                "created_at": datetime.now().isoformat(),
                "watermark": watermark._signature_hash[:8],
                "author": self.author
            }
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "message_hash": hashlib.md5(content.encode()).hexdigest()[:8]
        }
        
        self.conversations[session_id]["messages"].append(message)
        
        # Trim history if exceeds max
        if len(self.conversations[session_id]["messages"]) > self.max_history * 2:
            self.conversations[session_id]["messages"] = \
                self.conversations[session_id]["messages"][-self.max_history * 2:]
    
    @protect
    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a session."""
        if session_id not in self.conversations:
            return []
        return self.conversations[session_id]["messages"]
    
    @protect
    def clear_session(self, session_id: str) -> None:
        """Clear conversation history for a session."""
        if session_id in self.conversations:
            del self.conversations[session_id]
            logger.info(f"Cleared conversation history for session: {session_id}")


@protect_class
class LLMService:
    """
    LLM Service for generating answers with watermark protection.
    Copyright (c) 2024 Balenci Cash
    """
    
    def __init__(self):
        self.author = "Balenci Cash"
        self.service_id = "BC-LLM-2024"
        self.llm = None
        self.memory = ConversationMemory()
        self.tracer = None
        
        self._initialize_llm()
        self._initialize_tracer()
        logger.info(f"LLM Service initialized - Author: {self.author}")
    
    def _initialize_llm(self):
        """Initialize LLM with Groq or OpenAI based on configuration."""
        try:
            if settings.LLM_PROVIDER == "groq":
                self.llm = ChatGroq(
                    model=settings.GROQ_MODEL,
                    temperature=settings.TEMPERATURE,
                    groq_api_key=settings.GROQ_API_KEY,
                    max_tokens=settings.MAX_TOKENS
                )
                logger.info(f"Groq LLM initialized: {settings.GROQ_MODEL}")
            else:
                self.llm = ChatOpenAI(
                    model=settings.OPENAI_MODEL,
                    temperature=settings.TEMPERATURE,
                    openai_api_key=settings.OPENAI_API_KEY,
                    max_tokens=settings.MAX_TOKENS
                )
                logger.info(f"OpenAI LLM initialized: {settings.OPENAI_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
    
    def _initialize_tracer(self):
        """Initialize LangSmith tracer for observability."""
        if settings.LANGCHAIN_TRACING_V2 and settings.LANGCHAIN_API_KEY:
            try:
                self.tracer = LangChainTracer(
                    project_name=settings.LANGCHAIN_PROJECT
                )
                logger.info(f"LangSmith tracer initialized for project: {settings.LANGCHAIN_PROJECT}")
            except Exception as e:
                logger.warning(f"Failed to initialize LangSmith tracer: {e}")
    
    @protect
    def generate_answer(
        self,
        query: str,
        context_documents: List[Document],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate answer based on query and context documents.
        Includes watermark and source citations.
        """
        
        # Build context from documents
        context_texts = []
        sources = []
        
        for i, doc in enumerate(context_documents):
            context_texts.append(f"[Source {i+1}]: {doc.page_content}")
            sources.append({
                "index": i + 1,
                "content": doc.page_content[:200] + "...",
                "metadata": doc.metadata
            })
        
        context = "\n\n".join(context_texts)
        
        # Optimized prompt to reduce tokens
        system_prompt = f"""Answer based on context. Cite [Source X].
{context}

Rules: Use only context. Be concise."""

        user_prompt = f"Question: {query}"
        
        # Get conversation history if session exists
        messages = [SystemMessage(content=system_prompt)]
        
        if session_id:
            history = self.memory.get_history(session_id)
            for msg in history[-6:]:  # Last 3 exchanges
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
        
        messages.append(HumanMessage(content=user_prompt))
        
        try:
            # Generate response with tracing
            callbacks = [self.tracer] if self.tracer else []
            response = self.llm.invoke(messages, callbacks=callbacks)
            
            answer = response.content
            
            # Store in memory if session exists
            if session_id:
                self.memory.add_message(session_id, "user", query)
                self.memory.add_message(session_id, "assistant", answer)
            
            # Prepare watermarked result
            result = {
                "query": query,
                "answer": answer,
                "sources": sources,
                "session_id": session_id,
                "metadata": {
                    "generated_by": self.author,
                    "service": self.service_id,
                    "model": settings.GROQ_MODEL if settings.LLM_PROVIDER == "groq" else settings.OPENAI_MODEL,
                    "provider": settings.LLM_PROVIDER,
                    "timestamp": datetime.now().isoformat(),
                    "watermark": watermark._signature_hash[:16],
                    "context_docs_count": len(context_documents)
                }
            }
            
            logger.success(f"Answer generated successfully for query: {query[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            raise
    
    @protect
    def generate_standalone_question(
        self,
        query: str,
        session_id: str
    ) -> str:
        """
        Generate standalone question from query with conversation context.
        Used for better retrieval with conversation history.
        """
        history = self.memory.get_history(session_id)
        
        if not history:
            return query
        
        # Build conversation context
        conv_context = []
        for msg in history[-4:]:  # Last 2 exchanges
            conv_context.append(f"{msg['role']}: {msg['content']}")
        
        prompt = f"""Given the conversation history, rewrite the user's latest question to be standalone.
Include all necessary context from the conversation in the standalone question.

Conversation History:
{chr(10).join(conv_context)}

Latest Question: {query}

Standalone Question:"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            standalone = response.content.strip()
            logger.info(f"Generated standalone question: {standalone}")
            return standalone
        except Exception as e:
            logger.error(f"Failed to generate standalone question: {e}")
            return query


# Create service instance
llm_service = LLMService()