# RAG Document QA System Docker Image
# Copyright (c) 2024 Balenci Cash - All Rights Reserved
# Protected by Digital Watermark

FROM python:3.11-slim

# Set metadata
LABEL maintainer="Balenci Cash <balencicash@example.com>"
LABEL description="RAG Document QA System with Watermark Protection"
LABEL version="1.0.0"

# Set watermark environment variables
ENV AUTHOR="Balenci Cash"
ENV PROJECT_ID="RAG-SYS-Not_for_commercial_usage"
ENV WATERMARK_ENABLED=true

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY main.py .
COPY src/ ./src/
COPY config/ ./config/

# Create necessary directories
RUN mkdir -p logs uploads vector_stores

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi \
    uvicorn \
    langchain \
    langchain-community \
    langgraph \
    langsmith \
    openai \
    faiss-cpu \
    pypdf \
    python-docx \
    python-multipart \
    markdown \
    loguru \
    pydantic \
    pydantic-settings \
    python-dotenv \
    tiktoken \
    numpy \
    cryptography

# Create watermark verification file
RUN echo "Protected Software - Copyright (c) 2024 Balenci Cash" > /app/WATERMARK.txt && \
    echo "Project ID: RAG-SYS-Not_for_commercial_usage" >> /app/WATERMARK.txt && \
    echo "This software is protected by digital watermarking" >> /app/WATERMARK.txt

# Set environment variables
ENV PYTHONPATH=/app
ENV API_HOST=0.0.0.0
ENV API_PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["python", "main.py"]