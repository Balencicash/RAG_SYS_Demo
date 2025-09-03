# RAG Document QA System - Modern Architecture with ComfyUI

A modern, clean i### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration:
# - Add your Groq API key
# - Configure Ollama settings
# - Enable ComfyUI if needed
```

### 5. Run the Application

```bash
python main.py
```

The application will be available at: `http://localhost:8000`

## 🔧 Configuration

### Modern Configuration System

The configuration system is modular and type-safe:AG (Retrieval-Augmented Generation) document question-answering system with Ollama embeddings and ComfyUI integration.

## 🚀 New Features in v2.0

### ✨ Latest Updates

- **🔥 OpenAI Dependencies Removed**: Switched from OpenAI to Ollama for embeddings
- **🎨 ComfyUI Integration**: Added AI image generation capabilities
- **🦾 Ollama Support**: Using `nomic-embed-text` model for embeddings
- **🎯 Groq Only**: Simplified to use only Groq for LLM operations
- **📦 Modular Architecture**: Clean separation of concerns

### 🛠️ Technology Stack

- **LLM**: Groq (Llama 3.1-8B-Instant)
- **Embeddings**: Ollama (nomic-embed-text)  
- **Vector Store**: FAISS
- **Framework**: FastAPI + LangChain + LangGraph
- **Image Generation**: ComfyUI (optional)
- **Validation**: Pydantic

### 📁 Project Structure

```
config/
├── __init__.py           # Configuration exports
├── settings.py           # Main settings container
├── api_config.py         # API configuration
├── llm_config.py         # LLM & Ollama configuration
├── vector_config.py      # Vector store configuration
└── comfyui_config.py     # ComfyUI configuration

src/
├── core/
│   └── exceptions.py     # Exception handling
├── services/
│   ├── document_parser.py       # Document parsing
│   ├── vectorization.py         # Ollama embeddings & FAISS
│   ├── llm_service.py           # Groq LLM service  
│   └── comfyui_service.py       # ComfyUI integration
├── agents/
│   └── rag_agent.py             # RAG workflow
├── api/
│   └── main.py                  # FastAPI application
└── utils/
    ├── logger.py                # Logging utilities
    └── watermark.py             # Protection system

workflows/
└── default.json          # Default ComfyUI workflow

main.py                   # Application entry point
```

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.8+**
- **Ollama** (for embeddings): [Install Ollama](https://ollama.ai/)
- **Groq API Key**: Get from [Groq Console](https://console.groq.com/)
- **ComfyUI** (optional): For image generation features

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Ollama

```bash
# Install and pull the embedding model
ollama pull nomic-embed-text
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run Clean Version

```bash
python clean_main.py
```

The clean version will be available at: `http://localhost:8000`

## 🔧 Configuration

### Clean Configuration System

The new configuration system is modular and type-safe:

```python
from config.settings import settings

# Access different configuration modules
settings.app.app_name       # Application settings
settings.api.api_host       # API configuration
settings.llm.groq_model     # LLM configuration
settings.vector.chunk_size  # Vector configuration
settings.logging.log_level  # Logging configuration
```

### Configuration Validation

The system validates configuration on startup:

```python
# Check if fully configured
if settings.is_fully_configured:
    print("Ready to go!")
else:
    missing = settings.get_missing_config()
    print(f"Missing: {missing}")
```

## 🏛️ Architecture Improvements

### 1. Clean Services

Services are now focused and testable:

```python
# Document parsing with clear error handling
from src.services.clean_document_parser import document_parser

result = document_parser.parse_document("document.pdf")
# Returns structured result with validation

# Vector operations with proper abstraction
from src.services.clean_vectorization import text_chunker, vector_store

chunks = text_chunker.chunk_text(text, metadata)
vector_store.add_documents(chunks)
```

### 2. Unified Error Handling

Centralized error management:

```python
from src.core.exceptions import DocumentParsingError, VectorStoreError

# All services use typed exceptions
# Automatic HTTP error conversion
# Consistent error logging
```

### 3. Simplified Agent

The RAG agent is now clean and maintainable:

```python
from src.agents.clean_rag_agent import rag_agent

result = rag_agent.process_question("What is this about?")
# Clear workflow: initialize → process → retrieve → generate → finalize
```

## 🔍 API Endpoints

### Core Endpoints

- `GET /` - Health check with system info
- `GET /health` - Basic health status  
- `GET /status` - Detailed system status
- `POST /api/v1/upload` - Upload and process documents
- `POST /api/v1/question` - Ask questions about documents
- `DELETE /api/v1/session/{session_id}` - Clear conversation history
- `GET /api/v1/watermark/verify` - Verify system protection

### Status Information

```bash
curl http://localhost:8000/status
```

Returns detailed information about:
- Configuration status
- Service health
- Missing configurations
- Active components

## 🧪 Testing

Run the clean test suite:

```bash
python test_clean.py
```

Or with pytest:

```bash
pytest test_clean.py -v
```

Tests cover:
- Document parsing
- Text chunking
- Vector operations
- Configuration validation
- Error handling

## 📊 Code Quality Improvements

### Before vs After

| Aspect | Original | Clean Version |
|--------|----------|---------------|
| Configuration | Single monolithic file | Modular, typed configuration |
| Error Handling | Scattered try/catch | Centralized exception system |
| Watermark | Intrusive throughout code | Minimal, non-intrusive |
| Services | Large, complex classes | Focused, single-responsibility |
| Testing | Basic test file | Comprehensive test suite |
| Type Safety | Minimal typing | Full type hints |

### Key Principles Applied

1. **Single Responsibility Principle**: Each class has one clear purpose
2. **Dependency Injection**: Clear service boundaries and dependencies
3. **Error Handling**: Consistent, typed exceptions throughout
4. **Configuration Management**: Centralized, validated configuration
5. **Testability**: All components are easily testable
6. **Readability**: Clean, self-documenting code

## 🔄 Migration Guide

### Using Clean Components

You can use the clean components alongside or instead of the original ones:

```python
# Use clean main entry point
python clean_main.py

# Import clean services
from src.services.clean_document_parser import document_parser
from src.services.clean_vectorization import vector_store
from src.agents.clean_rag_agent import rag_agent

# Access modular configuration
from config.settings import settings
```

### Testing Both Versions

```bash
# Original version
python main.py

# Clean version  
python clean_main.py
```

## 🎯 Benefits

### For Developers

- **Easier to understand**: Clear separation of concerns
- **Easier to test**: Focused, injectable components
- **Easier to extend**: Modular architecture
- **Better error messages**: Typed exceptions with context

### For Operations

- **Better monitoring**: Detailed status endpoints
- **Easier configuration**: Validation with helpful error messages
- **Better logging**: Structured, contextual logging
- **Easier debugging**: Clear error types and messages

## 📝 License

Copyright (c) 2025 BalenciCash - All Rights Reserved

This software is protected by digital watermarking technology.
Unauthorized use or distribution is prohibited and tracked.

---

**Note**: This clean architecture maintains all original functionality while significantly improving code quality, readability, and maintainability.
