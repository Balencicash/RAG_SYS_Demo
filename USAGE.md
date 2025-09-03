# RAG Document QA System v2.0 - Usage Guide

## 🚀 Quick Start Guide

### Prerequisites Setup

1. **Install Ollama**
   ```bash
   # On macOS
   brew install ollama
   
   # Start Ollama service  
   ollama serve
   
   # Pull the embedding model
   ollama pull nomic-embed-text
   ```

2. **Get Groq API Key**
   - Visit [Groq Console](https://console.groq.com/)
   - Create an account and get your API key

3. **Setup ComfyUI** (Optional - for image generation)
   - Install ComfyUI following [official guide](https://github.com/comfyanonymous/ComfyUI)
   - Make sure it's running on `http://127.0.0.1:8188`

### Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Essential Configuration
GROQ_API_KEY=your_groq_api_key_here
OLLAMA_HOST=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# ComfyUI (Optional)
COMFYUI_ENABLED=false  # Set to true to enable image generation
COMFYUI_HOST=127.0.0.1
COMFYUI_PORT=8188
```

## 📚 Core Features

### 1. Document Processing & QA
- Upload documents (PDF, Word, Markdown, TXT)
- Ask questions about document content
- Get contextual answers with source references

### 2. Ollama Embeddings
- No OpenAI dependency required
- Local embedding generation using `nomic-embed-text`
- Fast and efficient vector operations

### 3. ComfyUI Integration (New!)
- Generate images based on text prompts
- Customizable generation parameters
- Async image generation with status tracking

## 🎯 API Endpoints

### Document Management
```
POST /api/v1/upload          # Upload document
POST /api/v1/ask             # Ask question
DELETE /api/v1/session/{id}  # Clear session
```

### ComfyUI Integration (New!)
```
POST /api/v1/generate-image     # Generate image
GET /api/v1/comfyui/status      # Check ComfyUI status
```

### System
```
GET /                        # Health check
GET /health                  # Detailed health info
GET /api/v1/status          # System status
```

## 🖼️ Image Generation Examples

### Basic Image Generation
```bash
curl -X POST "http://localhost:8000/api/v1/generate-image" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful sunset over mountains, digital art",
    "negative_prompt": "low quality, blurry",
    "width": 512,
    "height": 512,
    "steps": 20
  }'
```

### Response Format
```json
{
  "success": true,
  "prompt": "A beautiful sunset over mountains, digital art",
  "prompt_id": "abc123",
  "images": [
    {
      "filename": "rag_generated_abc123_00001_.png",
      "url": "http://127.0.0.1:8188/view",
      "params": {...}
    }
  ],
  "timestamp": "2024-12-20T10:30:00Z"
}
```

## 🔧 Advanced Configuration

### Ollama Configuration
```env
# Custom Ollama settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

### ComfyUI Configuration
```env
# ComfyUI settings
COMFYUI_ENABLED=true
COMFYUI_HOST=127.0.0.1
COMFYUI_PORT=8188
DEFAULT_WORKFLOW_PATH=workflows/default.json
OUTPUT_DIRECTORY=outputs/comfyui

# Generation defaults
DEFAULT_WIDTH=512
DEFAULT_HEIGHT=512
DEFAULT_STEPS=20
DEFAULT_CFG=7.0
```

### Vector Store Settings
```env
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
```

## 🚨 Troubleshooting

### Ollama Issues
- Ensure Ollama is running: `ollama serve`
- Check model is available: `ollama list`
- Pull model if missing: `ollama pull nomic-embed-text`

### ComfyUI Issues
- Verify ComfyUI is running on correct port
- Check workflow JSON format
- Ensure required models are downloaded

### API Issues
- Check logs in `logs/app.log`
- Verify environment variables
- Test with `/health` endpoint

## 🔄 Migration from v1.x

### Key Changes
1. **OpenAI Removed**: No longer needed for embeddings
2. **Ollama Added**: Local embeddings with nomic-embed-text
3. **ComfyUI Added**: Optional image generation
4. **Groq Only**: Simplified LLM provider setup

### Migration Steps
1. Update environment variables
2. Install Ollama and pull models
3. Update API client code (if any)
4. Test functionality

## 📖 Examples

### Document QA Workflow
```python
import requests

# Upload document
files = {'file': open('document.pdf', 'rb')}
response = requests.post('http://localhost:8000/api/v1/upload', files=files)

# Ask question
data = {
    "question": "What is the main topic of this document?",
    "session_id": "my-session"
}
response = requests.post('http://localhost:8000/api/v1/ask', json=data)
print(response.json()['answer'])
```

### Image Generation Workflow
```python
import requests

# Generate image
data = {
    "prompt": "A futuristic city with flying cars",
    "width": 768,
    "height": 768,
    "steps": 25
}
response = requests.post('http://localhost:8000/api/v1/generate-image', json=data)
print(f"Generated: {response.json()['images'][0]['filename']}")
```

## 🎯 Best Practices

1. **Performance**: Keep document chunks small (1000 chars)
2. **Memory**: Clear sessions regularly for long conversations
3. **ComfyUI**: Use reasonable image sizes to avoid timeouts
4. **Monitoring**: Check `/health` endpoint regularly

## 🆘 Support

- Check logs in `logs/app.log`
- Review configuration in `.env`
- Test with simple documents first
- Use `/health` endpoint for diagnostics

---

**Copyright (c) 2024 Balenci Cash - All Rights Reserved**