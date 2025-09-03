#!/bin/bash
# RAG Document QA System Startup Script
# Copyright (c) 2025 BalenciCash

echo "=============================================="
echo "RAG Document QA System v1.0"
echo "Copyright (c) 2025 BalenciCash"
echo "Protected by Digital Watermark Technology"
echo "=============================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating .env from template..."
    cp .env.example .env
    echo "Please edit .env file with your API keys before running."
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python $required_version or higher is required. Found: $python_version"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Create necessary directories
mkdir -p logs uploads vector_stores

# Set environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Start the application
echo "🚀 Starting RAG Document QA System..."
echo "📍 API will be available at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python src/api/main.py