#!/bin/bash

# RAG Document QA System - Stop Server Script
# 停止RAG文档问答系统服务

echo "🛑 正在停止 RAG Document QA System..."

# 查找uvicorn进程
PIDS=$(pgrep -f "uvicorn.*src.api.main")

if [ -z "$PIDS" ]; then
    echo "❌ 没有找到运行中的服务进程"
    exit 1
fi

echo "📍 找到运行中的进程: $PIDS"

# 温和地停止进程
for PID in $PIDS; do
    echo "🔄 正在停止进程 $PID..."
    kill -TERM $PID
done

# 等待进程停止
sleep 3

# 检查是否还有进程在运行
REMAINING=$(pgrep -f "uvicorn.*src.api.main")

if [ ! -z "$REMAINING" ]; then
    echo "⚠️  进程未完全停止，强制终止..."
    for PID in $REMAINING; do
        kill -9 $PID
        echo "💀 强制终止进程 $PID"
    done
fi

# 最终检查
FINAL_CHECK=$(pgrep -f "uvicorn.*src.api.main")

if [ -z "$FINAL_CHECK" ]; then
    echo "✅ RAG Document QA System 已成功停止"
    echo "🔌 端口 8000 现在可用"
else
    echo "❌ 停止失败，仍有进程在运行"
    exit 1
fi

echo ""
echo "📊 当前系统状态:"
echo "   - Web界面: http://localhost:8000 (已停止)"
echo "   - API文档: http://localhost:8000/docs (已停止)"
echo "   - 健康检查: http://localhost:8000/health (已停止)"
