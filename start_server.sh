#!/bin/bash

# RAG Document QA System v2.0 启动脚本

echo "🚀 启动 RAG Document QA System v2.0"
echo "Copyright (c) 2025 BalenciCash - All Rights Reserved"
echo "=" 

# 进入项目目录
cd "$(dirname "$0")"

# 检查uv环境
if ! command -v uv &> /dev/null; then
    echo "❌ uv未安装，请运行: pip install uv"
    exit 1
fi

# 检查虚拟环境
if [ ! -f "uv.lock" ]; then
    echo "❌ uv.lock不存在，请运行: uv sync"
    exit 1
fi

# 检查Ollama服务
echo "🔍 检查Ollama服务状态..."
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "⚠️  Ollama服务未运行，尝试启动..."
    ollama serve &
    OLLAMA_PID=$!
    sleep 3
    
    # 检查nomic-embed-text模型
    if ! curl -s http://localhost:11434/api/tags | grep -q "nomic-embed-text"; then
        echo "📦 下载nomic-embed-text模型..."
        ollama pull nomic-embed-text
    fi
else
    echo "✅ Ollama服务已运行"
fi

# 启动FastAPI服务器
echo "🌐 启动FastAPI服务器..."
echo "📍 服务地址: http://localhost:8000"
echo "📖 API文档: http://localhost:8000/docs"
echo "🧪 测试页面: file://$(pwd)/web/index.html"
echo ""
echo "按 Ctrl+C 停止服务"
echo "=" 

uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# 清理
if [ ! -z "$OLLAMA_PID" ]; then
    echo "🛑 停止Ollama服务..."
    kill $OLLAMA_PID 2>/dev/null
fi

echo "👋 服务已停止"
