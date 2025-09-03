"""
Clean FastAPI Application.
Simplified and readable API with proper error handling and validation.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
from pathlib import Path

from src.core.exceptions import handle_error_and_raise
from src.services.document_parser import document_parser
from src.services.vectorization import text_chunker, vector_store
from src.services.llm_service import llm_service
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

# Mount static files for web interface
web_dir = Path(__file__).parent.parent.parent / "web"
if web_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")


# Request/Response Models
class QuestionRequest(BaseModel):
    question: str
    session_id: Optional[str] = None


class QueryRequest(BaseModel):
    query: str
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


# Root route - serve web interface
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the web interface."""
    web_interface_dir = Path(__file__).parent.parent.parent / "web"
    index_file = web_interface_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse(
        """
    <html>
        <head><title>RAG Document QA System v2.0</title></head>
        <body>
            <h1>RAG Document QA System v2.0</h1>
            <p>Web interface not found. Please check installation.</p>
            <p><a href="/docs">API Documentation</a></p>
        </body>
    </html>
    """
    )


@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app.app_version,
        "author": settings.app.app_author,
        "watermark": watermark.get_metadata(),
    }


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


# Additional API endpoints for web interface compatibility
@app.post(f"{settings.api.api_prefix}/query", response_model=QuestionResponse)
async def query_documents(request: QueryRequest):
    """Query documents - RAG endpoint with query parameter."""
    # Convert QueryRequest to QuestionRequest
    question_request = QuestionRequest(
        question=request.query, session_id=request.session_id
    )
    return await ask_question(question_request)


@app.get(f"{settings.api.api_prefix}/documents")
async def list_documents() -> dict:
    """List uploaded documents."""
    try:
        # Get document count and metadata from vector store
        store_info = vector_store.get_store_info()

        # Get actual document files from uploads directory
        uploads_dir = Path(__file__).parent.parent.parent / "uploads"
        document_files = []

        if uploads_dir.exists():
            for file_path in uploads_dir.glob("*"):
                if file_path.is_file() and file_path.suffix in [
                    ".md",
                    ".txt",
                    ".pdf",
                    ".docx",
                ]:
                    try:
                        # Determine document type
                        doc_type = "text"
                        if file_path.suffix == ".md":
                            doc_type = "markdown"
                        elif file_path.suffix == ".pdf":
                            doc_type = "pdf"
                        elif file_path.suffix in [".doc", ".docx"]:
                            doc_type = "word"

                        # Read file for title (for text/markdown files)
                        title = file_path.stem
                        if doc_type in ["markdown", "text"]:
                            try:
                                with open(file_path, "r", encoding="utf-8") as f:
                                    content = f.read()
                                    lines = content.split("\n")
                                    if lines and lines[0].startswith("#"):
                                        title = lines[0].lstrip("#").strip()
                            except:
                                pass

                        file_stat = file_path.stat()
                        document_files.append(
                            {
                                "id": file_path.stem,
                                "filename": file_path.name,
                                "title": title,
                                "type": doc_type,
                                "upload_time": file_stat.st_mtime
                                * 1000,  # Convert to milliseconds
                                "size": file_stat.st_size,
                                "chunks": 0,  # We don't track chunks per document currently
                            }
                        )
                    except Exception as e:
                        logger.warning(f"Failed to read document {file_path}: {e}")

        return {
            "success": True,
            "documents": document_files,
            "document_count": len(document_files),
            "total_chunks": store_info.get("total_vectors", 0),
            "store_info": store_info,
            "watermark": watermark.get_metadata(),
        }
    except Exception as e:
        handle_error_and_raise(e, "list_documents")


@app.delete(f"{settings.api.api_prefix}/documents/clear")
async def clear_documents() -> dict:
    """Clear all uploaded documents."""
    try:
        # Clear vector store
        vector_store.clear()

        # Delete all uploaded files
        uploads_dir = Path(__file__).parent.parent.parent / "uploads"
        deleted_count = 0

        if uploads_dir.exists():
            for file_path in uploads_dir.glob("*"):
                if file_path.is_file() and file_path.suffix in [
                    ".md",
                    ".txt",
                    ".pdf",
                    ".docx",
                ]:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        logger.info(f"Deleted file: {file_path}")
                    except Exception as e:
                        logger.warning(f"Failed to delete file {file_path}: {e}")

        return {
            "success": True,
            "message": f"All documents cleared successfully. Deleted {deleted_count} files.",
            "watermark": watermark.get_metadata(),
        }
    except Exception as e:
        logger.error(f"Clear documents failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to clear documents: {str(e)}"
        )


@app.delete(f"{settings.api.api_prefix}/documents/" + "{document_id}")
async def delete_document(document_id: str) -> dict:
    """Delete a specific document."""
    try:
        # Delete the physical file
        uploads_dir = Path(__file__).parent.parent.parent / "uploads"
        file_patterns = [
            f"{document_id}.md",
            f"{document_id}.txt",
            f"{document_id}.pdf",
            f"{document_id}.docx",
        ]

        deleted = False
        for pattern in file_patterns:
            file_path = uploads_dir / pattern
            if file_path.exists():
                file_path.unlink()
                deleted = True
                logger.info(f"Deleted document file: {file_path}")
                break

        if not deleted:
            raise HTTPException(status_code=404, detail="Document not found")

        # Note: For a complete implementation, we would need to rebuild the vector store
        # without the deleted document's chunks. For now, we'll just delete the file.
        # The vector store will still contain the document's embeddings until cleared.

        return {
            "success": True,
            "message": f"Document {document_id} deleted successfully",
            "watermark": watermark.get_metadata(),
        }
    except HTTPException:
        raise
    except Exception as e:
        handle_error_and_raise(e, "delete_document")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host=settings.api.api_host,
        port=settings.api.api_port,
        reload=settings.app.is_development,
    )
