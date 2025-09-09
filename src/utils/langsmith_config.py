"""
LangSmith Configuration Utilities.
Helper functions for setting up LangSmith tracing.
"""

import os
from typing import Optional
from loguru import logger
from config.settings import settings


def setup_langsmith_environment() -> bool:
    """
    Setup LangSmith environment variables from settings.
    Returns True if successfully configured, False otherwise.
    """
    llm_config = settings.llm

    if not llm_config.is_langsmith_configured:
        logger.info("LangSmith not configured - tracing disabled")
        return False

    try:
        # Set required environment variables
        os.environ["LANGCHAIN_TRACING_V2"] = str(
            llm_config.langchain_tracing_v2
        ).lower()
        os.environ["LANGCHAIN_ENDPOINT"] = llm_config.langchain_endpoint
        os.environ["LANGCHAIN_API_KEY"] = llm_config.langchain_api_key
        os.environ["LANGCHAIN_PROJECT"] = llm_config.langchain_project

        # Optional: Set additional metadata
        os.environ["LANGCHAIN_TAGS"] = "rag-system,groq,production"

        logger.info(
            f"LangSmith tracing configured for project: {llm_config.langchain_project}"
        )
        return True

    except (KeyError, ValueError, OSError) as e:
        logger.error(f"Failed to setup LangSmith environment: {e}")
        return False


def get_langsmith_status() -> dict:
    """Get current LangSmith configuration status."""
    llm_config = settings.llm

    return {
        "configured": llm_config.is_langsmith_configured,
        "tracing_enabled": llm_config.langchain_tracing_v2,
        "project": llm_config.langchain_project,
        "endpoint": llm_config.langchain_endpoint,
        "api_key_present": bool(llm_config.langchain_api_key),
        "env_vars_set": {
            "LANGCHAIN_TRACING_V2": os.getenv("LANGCHAIN_TRACING_V2"),
            "LANGCHAIN_ENDPOINT": os.getenv("LANGCHAIN_ENDPOINT"),
            "LANGCHAIN_API_KEY": bool(os.getenv("LANGCHAIN_API_KEY")),
            "LANGCHAIN_PROJECT": os.getenv("LANGCHAIN_PROJECT"),
        },
    }


def create_langsmith_run_metadata(
    query: str, session_id: str, additional_tags: Optional[list] = None
) -> dict:
    """Create standardized metadata for LangSmith runs."""
    base_tags = ["rag-system", "document-qa"]

    if additional_tags:
        base_tags.extend(additional_tags)

    return {
        "tags": base_tags,
        "metadata": {
            "query": query,
            "session_id": session_id,
            "system": "rag-document-qa",
            "version": "2.0",
            "author": "BalenciCash",
        },
    }
