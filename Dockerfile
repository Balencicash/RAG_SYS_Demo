# RAG Document QA System - Technical Showcase
# Copyright (c) 2025 BalenciCash - All Rights Reserved
# Learning and Research Purpose Only

FROM python:3.12-slim

# Set metadata
LABEL maintainer="BalenciCash"
LABEL description="RAG Document QA System - Technical Showcase"
LABEL version="2.0.0"
LABEL license="Custom Technical Showcase License"

# Set environment for system metadata
ENV PYTHONPATH=/app
ENV AUTHOR="BalenciCash"
ENV PROJECT_VERSION="v2.0.0"
ENV BUILD_TYPE="production"

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy uv configuration files
COPY pyproject.toml uv.lock ./

# Install dependencies with uv
RUN uv sync --frozen --no-install-project

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY web/ ./web/

# Create necessary directories
RUN mkdir -p logs uploads vector_stores

# Set proper permissions
RUN chmod -R 755 /app

# Set environment variables
ENV API_HOST=0.0.0.0
ENV API_PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application using uv
CMD ["uv", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]