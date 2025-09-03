"""
Clean FastAPI Application.
Simplified and readable API with proper error handling and validation.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
from pathlib import Path

from src.core.exceptions import handle_error_and_raise
from src.services.document_parser import document_parser
from src.services.vectorization import text_chunker, vector_store
from src.services.llm_service import llm_service
from src.services.comfyui_service import comfyui_service
from src.agents.rag_agent import rag_agent
from src.utils.watermark import watermark, initialize_watermark
from config.settings import settings
from loguru import logger


# Initialize watermark
initialize_watermark()

# Create FastAPI app
app = FastAPI(
    title=settings.app.app_name,
    version=settings.app.app_version,
    description=settings.app.app_description,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(CORSMiddleware, **settings.api.cors_config)


# Request/Response Models
class QuestionRequest(BaseModel):
    question: str
    session_id: Optional[str] = None


class UploadResponse(BaseModel):
    success: bool
    message: str
    file_id: str
    metadata: Dict[str, Any]


class QuestionResponse(BaseModel):
    success: bool
    answer: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None
    session_id: str
    metadata: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    version: str
    author: str
    watermark: Dict[str, Any]


class StatusResponse(BaseModel):
    api_status: str
    configuration: Dict[str, Any]
    services: Dict[str, Any]


class ImageGenerationRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    steps: Optional[int] = None
    cfg: Optional[float] = None
    sampler_name: Optional[str] = None
    scheduler: Optional[str] = None


class ImageGenerationResponse(BaseModel):
    success: bool
    prompt: str
    prompt_id: Optional[str] = None
    images: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    timestamp: str


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info(f"Starting {settings.app.app_name} v{settings.app.app_version}")
    logger.info(f"{settings.app.app_copyright}")

    # Check configuration
    if not settings.is_fully_configured:
        missing = settings.get_missing_config()
        logger.warning(f"Missing configuration: {missing}")
        logger.warning("Some features may not work properly")


# Health check endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.app.app_version,
        author=settings.app.app_author,
        watermark=watermark.get_metadata(),
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.app.app_version,
        author=settings.app.app_author,
        watermark=watermark.get_metadata(),
    )


@app.get("/status", response_model=StatusResponse)
async def status_check():
    """Detailed status endpoint."""
    return StatusResponse(
        api_status="healthy",
        configuration={
            "is_fully_configured": settings.is_fully_configured,
            "missing_config": settings.get_missing_config(),
            "llm_provider": settings.llm.llm_provider,
            "vector_store": settings.vector.vector_store_type,
        },
        services={
            "llm_service": llm_service.get_service_info(),
            "vector_store": vector_store.get_store_info(),
            "rag_agent": rag_agent.get_agent_info(),
        },
    )


# File upload endpoint
@app.post(f"{settings.api.api_prefix}/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document."""
    try:
        # Validate file
        if not document_parser.is_supported(file.filename):
            supported = ", ".join(document_parser.get_supported_extensions())
            raise HTTPException(
                status_code=400, detail=f"Unsupported file type. Supported: {supported}"
            )

        # Generate unique file ID and path
        file_id = str(uuid.uuid4())
        file_ext = Path(file.filename).suffix.lower()
        file_path = settings.api.upload_dir / f"{file_id}{file_ext}"

        # Read and validate file content
        content = await file.read()
        if len(content) > settings.api.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.api.max_file_size} bytes",
            )

        # Save file
        with open(file_path, "wb") as f:
            f.write(content)

        # Parse document
        parsed_doc = document_parser.parse_document(str(file_path))

        # Create text chunks
        chunks = text_chunker.chunk_text(
            parsed_doc["content"],
            metadata={
                "file_id": file_id,
                "file_name": file.filename,
                "file_type": file_ext,
            },
        )

        # Add to vector store
        vector_store.add_documents(chunks)

        # Get chunk statistics
        chunk_stats = text_chunker.get_chunk_stats(chunks)

        return UploadResponse(
            success=True,
            message=f"Document processed successfully: {file.filename}",
            file_id=file_id,
            metadata={
                "file_info": {
                    "name": file.filename,
                    "size": len(content),
                    "type": file_ext,
                    "char_count": parsed_doc["char_count"],
                },
                "processing": {
                    **chunk_stats,
                    "content_hash": parsed_doc["content_hash"][:8],
                },
                "watermark": watermark.get_metadata(),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        # Clean up file if processing failed
        if "file_path" in locals() and file_path.exists():
            file_path.unlink()
        handle_error_and_raise(e, "upload_document")


# Question answering endpoint
@app.post(f"{settings.api.api_prefix}/question", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question and get an answer from the RAG system."""
    try:
        # Check if vector store is initialized
        if not vector_store.vector_store:
            raise HTTPException(
                status_code=400,
                detail="No documents uploaded. Please upload documents first.",
            )

        # Process question through RAG agent
        result = rag_agent.process_question(
            query=request.question, session_id=request.session_id
        )

        if not result["success"]:
            raise HTTPException(
                status_code=500, detail=result.get("error", "Unknown error occurred")
            )

        answer_data = result.get("answer", {})
        session_id = result["session_id"]

        return QuestionResponse(
            success=True,
            answer=answer_data.get("text"),
            sources=answer_data.get("sources"),
            session_id=session_id,
            metadata={
                "model_info": answer_data.get("metadata", {}),
                "agent_metadata": answer_data.get("agent_metadata", {}),
                "watermark": watermark.get_metadata(),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        handle_error_and_raise(e, "ask_question")


# Session management
@app.delete(f"{settings.api.api_prefix}/session/{{session_id}}")
async def clear_session(session_id: str) -> dict:
    """Clear conversation history for a session."""
    try:
        llm_service.memory.clear_session(session_id)

        return {
            "success": True,
            "message": f"Session {session_id} cleared",
            "watermark": watermark.get_metadata(),
        }
    except Exception as e:
        handle_error_and_raise(e, "clear_session")


# ComfyUI Endpoints
@app.post(
    f"{settings.api.api_prefix}/generate-image", response_model=ImageGenerationResponse
)
async def generate_image(request: ImageGenerationRequest):
    """Generate an image using ComfyUI."""
    try:
        if not settings.comfyui.is_enabled:
            raise HTTPException(
                status_code=503, detail="ComfyUI service is not enabled"
            )

        # Prepare generation parameters
        kwargs = {}
        if request.width:
            kwargs["width"] = request.width
        if request.height:
            kwargs["height"] = request.height
        if request.steps:
            kwargs["steps"] = request.steps
        if request.cfg:
            kwargs["cfg"] = request.cfg
        if request.sampler_name:
            kwargs["sampler_name"] = request.sampler_name
        if request.scheduler:
            kwargs["scheduler"] = request.scheduler

        # Generate image
        result = await comfyui_service.generate_image(
            prompt=request.prompt, negative_prompt=request.negative_prompt, **kwargs
        )

        return ImageGenerationResponse(**result)

    except Exception as e:
        handle_error_and_raise(e, "Image generation")


@app.get(f"{settings.api.api_prefix}/comfyui/status")
async def get_comfyui_status():
    """Get ComfyUI service status."""
    try:
        status = await comfyui_service.get_status()
        return {
            "comfyui_status": status,
            "watermark": watermark.get_metadata(),
        }
    except Exception as e:
        handle_error_and_raise(e, "ComfyUI status check")


# Watermark verification
@app.get(f"{settings.api.api_prefix}/watermark/verify")
async def verify_watermark() -> dict:
    """Verify watermark protection status."""
    return {
        "protected": True,
        "author": watermark.author,
        "project_id": watermark.project_id,
        "signature": watermark.get_metadata()["signature"],
        "copyright": settings.app.app_copyright,
        "message": "This software is protected by digital watermarking",
        "watermark": watermark.get_metadata(),
    }


# Import llm_service for session management
from src.services.llm_service import llm_service


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host=settings.api.api_host,
        port=settings.api.api_port,
        reload=settings.app.is_development,
    )
