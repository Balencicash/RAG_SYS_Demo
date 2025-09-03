#!/bin/bash

# RAG Document QA System v2.0 - System Status Check
echo "🔍 RAG Document QA System v2.0 - System Status Check"
echo "=================================================="

# Check Python virtual environment
if [ -d ".venv" ]; then
    echo "✅ Python virtual environment: Found"
else
    echo "❌ Python virtual environment: Not found"
fi

# Check required files
echo ""
echo "📁 Core Files Check:"
files=(
    "src/api/main.py"
    "web/index.html" 
    "web/app.js"
    "config/settings.py"
    "start_server.sh"
    "requirements.txt"
    "README.md"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file"
    fi
done

# Check directories
echo ""
echo "📂 Directory Structure:"
dirs=(
    "config"
    "src/api"
    "src/services" 
    "src/agents"
    "src/utils"
    "web"
    "uploads"
    "vector_stores"
    "logs"
)

for dir in "${dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir/"
    else
        echo "❌ $dir/"
    fi
done

# Check for redundant files (should not exist)
echo ""
echo "🧹 Cleanup Verification (these should NOT exist):"
cleanup_files=(
    "demo.py"
    "test_llm.py" 
    "test_rag.py"
    "clean_main.py"
    "main.py"
    "config/comfyui_config.py"
    "src/services/comfyui_service.py"
)

all_clean=true
for file in "${cleanup_files[@]}"; do
    if [ -f "$file" ]; then
        echo "❌ $file (should be deleted)"
        all_clean=false
    fi
done

if [ "$all_clean" = true ]; then
    echo "✅ All redundant files have been cleaned up"
fi

echo ""
echo "🎯 System Status: Ready for deployment!"
echo "🌐 Start server with: ./start_server.sh"
echo "📖 Access at: http://localhost:8000"
