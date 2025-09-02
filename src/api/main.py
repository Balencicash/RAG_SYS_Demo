"""
FastAPI Application for RAG Document QA System
Copyright (c) 2024 Balenci Cash - All Rights Reserved
Protected by Digital Watermark
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import uuid
from pathlib import Path

from src.utils.logger import logger
from src.utils.watermark import watermark, protect, initialize_watermark_protection
from src.services.document_parser import document_parser_service
from src.services.vectorization import text_chunker, vector_store_service
from src.services.llm_service import llm_service
# TODO: Needs refactoring for new langgraph API
# from src.agents.rag_agent import rag_agent
from config.settings import settings


# Initialize watermark protection on startup
initialize_watermark_protection()

# Create FastAPI app with watermark
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=f"{settings.APP_NAME} - {settings.APP_COPYRIGHT}",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    answer: Optional[str]
    sources: Optional[List[Dict[str, Any]]]
    session_id: str
    metadata: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    author: str
    version: str
    watermark: str


# Dependency for watermark verification
@protect
async def verify_watermark():
    """Verify watermark on each request."""
    if not watermark.verify_ownership():
        raise HTTPException(status_code=403, detail="Watermark verification failed")
    return True


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"{settings.APP_COPYRIGHT}")
    logger.info(f"Watermark Protection Active: {settings.WATERMARK_SIGNATURE}")

    # Create upload directory
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # TODO: Needs refactoring for new langgraph API
    # Log LangGraph visualization
    # graph_viz = rag_agent.visualize_graph()
    # logger.info(f"RAG Agent Graph:\n{graph_viz}")


@app.get("/", response_model=HealthResponse)
@protect
async def root():
    """Root endpoint with watermark information."""
    return HealthResponse(
        status="healthy",
        author=watermark.author,
        version=settings.APP_VERSION,
        watermark=getattr(watermark, "signature_hash", "")[:16],
    )


@app.get("/health", response_model=HealthResponse)
@protect
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        author=watermark.author,
        version=settings.APP_VERSION,
        watermark=getattr(watermark, "signature_hash", "")[:16],
    )


@app.post("/api/v1/upload", response_model=UploadResponse)
@protect
async def upload_document(
    file: UploadFile = File(...), _: bool = Depends(verify_watermark)
):
    """
    Upload and process a document.
    Protected by watermark verification.
    """

    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {settings.ALLOWED_EXTENSIONS}",
        )

    # Generate unique file ID
    file_id = str(uuid.uuid4())
    file_path = settings.UPLOAD_DIR / f"{file_id}{file_ext}"

    try:
        # Save uploaded file
        content = await file.read()

        # Check file size
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE} bytes",
            )

        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(f"File uploaded: {file_path}")

        # Parse document
        parsed_doc = document_parser_service.parse_document(str(file_path))

        # Chunk text
        chunks = text_chunker.chunk_text(
            parsed_doc["content"],
            metadata={
                "file_id": file_id,
                "file_name": file.filename,
                "author": watermark.author,
            },
        )

        # Create or update vector store
        if not vector_store_service.vector_store:
            vector_store_service.create_vector_store(chunks)
        else:
            vector_store_service.add_documents(chunks)

        # Save vector index
        index_path = f"./vector_stores/{file_id}"
        os.makedirs(index_path, exist_ok=True)
        vector_store_service.save_index(index_path)

        return UploadResponse(
            success=True,
            message=f"Document processed successfully: {file.filename}",
            file_id=file_id,
            metadata={
                "chunks_created": len(chunks),
                "char_count": parsed_doc["char_count"],
                "watermark": getattr(watermark, "signature_hash", "")[:8],
                "author": watermark.author,
            },
        )

    except (IOError, ValueError, TypeError) as e:
        logger.error(f"Error processing upload: {e}")
        # Clean up file if processing failed
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/v1/question", response_model=QuestionResponse)
@protect
async def ask_question(request: QuestionRequest, _: bool = Depends(verify_watermark)):
    """
    Ask a question and get an answer from the RAG system.
    Protected by watermark verification.
    """

    if not vector_store_service.vector_store:
        raise HTTPException(
            status_code=400,
            detail="No documents uploaded. Please upload documents first.",
        )

    try:
        # TODO: Needs refactoring for new langgraph API
        # Process question through RAG agent
        # result = rag_agent.process_question(
        #     query=request.question, session_id=request.session_id
        # )
        result = {
            "success": True,
            "answer": {"answer": "功能暂时不可用，正在升级 RAG 系统。"},
            "session_id": request.session_id or str(uuid.uuid4()),
            "watermark": getattr(watermark, "signature_hash", "")[:16]
        }

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error"))

        answer_data = result["answer"]

        return QuestionResponse(
            success=True,
            answer=answer_data.get("answer"),
            sources=answer_data.get("sources"),
            session_id=result["session_id"],
            metadata={
                "model": settings.OPENAI_MODEL,
                "watermark": result["watermark"],
                "author": watermark.author,
                "agent_metadata": answer_data.get("agent_metadata", {}),
            },
        )

    except HTTPException as http_error:
        raise http_error
    except (ValueError, RuntimeError) as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.delete("/api/v1/session/{session_id}")
@protect
async def clear_session(session_id: str, _: bool = Depends(verify_watermark)):
    """Clear conversation history for a session."""
    try:
        llm_service.memory.clear_session(session_id)
        return {
            "success": True,
            "message": f"Session {session_id} cleared",
            "watermark": getattr(watermark, "signature_hash", "")[:8],
        }
    except (KeyError, ValueError) as e:
        logger.error(f"Error clearing session: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/v1/watermark/verify")
@protect
async def verify_watermark_endpoint():
    """Verify watermark protection status."""
    return {
        "protected": True,
        "author": watermark.author,
        "project_id": "RAG-SYS-Not_for_commercial_usage",
        "signature": getattr(watermark, "signature_hash", "")[:32],
        "copyright": settings.APP_COPYRIGHT,
        "message": "This software is protected by digital watermarking",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True
    )
