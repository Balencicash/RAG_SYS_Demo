# 🚀 RAG Document QA System v2.0 - Quick Deploy Guide

## ⚡ Quick Start

1. **Clone & Setup**
   ```bash
   git clone <your-repo-url>
   cd <repo-name>
   pip install -r requirements.txt
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys:
   # - GROQ_API_KEY=your_groq_api_key
   # - OLLAMA_BASE_URL=http://localhost:11434
   ```

3. **Start Ollama** (for embeddings)
   ```bash
   ollama serve
   ollama pull nomic-embed-text
   ```

4. **Launch System**
   ```bash
   ./start_server.sh
   ```

5. **Access**: http://localhost:8000

## 🎯 Features

- ✅ **Document Upload**: TXT, MD, PDF, DOCX
- ✅ **RAG Q&A**: Intelligent document-based answers  
- ✅ **Web Interface**: Modern, responsive design
- ✅ **Document Management**: Upload, delete, clear all
- ✅ **Real-time Chat**: Instant responses

## 🔧 Tech Stack

- **Backend**: FastAPI + Python 3.12
- **Frontend**: Vanilla JS + Modern CSS
- **AI**: Groq (llama-3.1-8b-instant) + Ollama
- **Vector DB**: FAISS
- **Deployment**: Docker ready

## 📦 Production Ready

All components tested and optimized for production deployment.

---
*Built with ❤️ by BalenciCash*
