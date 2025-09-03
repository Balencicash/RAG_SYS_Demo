#!/usr/bin/env python3
"""
RAG Document QA System v2.0 演示脚本
用于展示系统的主要功能和运行状态
"""
import asyncio
import json
import time
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import settings


def print_header():
    """打印系统头部信息"""
    print("=" * 80)
    print("🚀 RAG Document QA System v2.0 - 系统演示")
    print("Copyright (c) 2025 BalenciCash - All Rights Reserved")
    print("🛡️ Watermark Protection Active - Signature: BC-RAG-2024")
    print("=" * 80)


def print_system_info():
    """打印系统信息"""
    print("\n📋 系统配置信息:")
    print(f"   🤖 LLM模型: {settings.llm.groq_model}")
    print(
        f"   🔗 Groq API: {'✅ 配置完成' if settings.llm.groq_api_key and settings.llm.groq_api_key != 'your-groq-api-key-here' else '❌ 需要配置'}"
    )
    print(f"   🧠 嵌入模型: {settings.llm.ollama_embedding_model}")
    print(f"   🌐 Ollama服务: {settings.llm.ollama_host}")
    print(f"   � Web界面: http://localhost:8000")
    print(f"   📊 向量维度: FAISS + Ollama")
    print(
        f"   🔧 文本分块: {settings.vector.chunk_size}字符，重叠{settings.vector.chunk_overlap}"
    )


async def check_services():
    """检查服务状态"""
    print("\n🔍 服务状态检查:")

    # 检查Ollama
    try:
        import requests

        response = requests.get(f"{settings.llm.ollama_host}/api/tags", timeout=5)
        if response.status_code == 200:
            print("   ✅ Ollama服务: 运行正常")
            tags = response.json()
            models = [model["name"] for model in tags.get("models", [])]
            if "nomic-embed-text:latest" in models:
                print("   ✅ nomic-embed-text模型: 已安装")
            else:
                print("   ⚠️  nomic-embed-text模型: 未安装")
        else:
            print("   ❌ Ollama服务: 连接失败")
    except Exception:
        print("   ❌ Ollama服务: 无法连接")

    # 检查模块导入
    try:
        from src.services.vectorization import VectorStoreManager
        from src.services.llm_service import LLMService
        from src.agents.rag_agent import CleanRAGAgent

        print("   ✅ 核心模块: 导入成功")
    except Exception as e:
        print(f"   ❌ 核心模块: 导入失败 - {e}")


def show_api_endpoints():
    """显示API端点"""
    print("\n🌐 可用的API端点:")
    endpoints = [
        ("GET", "/", "Web界面"),
        ("GET", "/health", "系统健康检查"),
        ("GET", "/docs", "Swagger API文档"),
        ("GET", "/api/v1/documents", "文档列表"),
        ("POST", "/api/v1/upload", "文档上传"),
        ("POST", "/api/v1/query", "RAG查询"),
        ("DELETE", "/api/v1/documents/clear", "清空文档"),
    ]

    for method, endpoint, description in endpoints:
        method_color = "🟢" if method == "GET" else "🔵"
        print(f"   {method_color} {method:4} {endpoint:25} - {description}")


def show_usage_examples():
    """显示使用示例"""
    print("\n📖 使用示例:")
    print("   1. 启动服务器:")
    print("      ./start_server.sh")
    print()
    print("   2. 打开Web界面:")
    print("      http://localhost:8000")
    print()
    print("   3. 查看API文档:")
    print("      http://localhost:8000/docs")
    print()
    print("   4. 健康检查:")
    print("      curl http://localhost:8000/health")


def show_project_structure():
    """显示项目结构"""
    print("\n📁 项目结构:")
    structure = [
        "📦 RAG-Document-QA-System-v2.0",
        "├── 🔧 config/          # 配置模块",
        "├── 📄 src/             # 核心源代码",
        "│   ├── 🤖 agents/      # RAG代理",
        "│   ├── 🌐 api/         # FastAPI接口",
        "│   ├── 🛠️ services/    # 核心服务",
        "│   └── 🔧 utils/       # 工具函数",
        "├── 📋 workflows/       # ComfyUI工作流",
        "├── 📚 docs/            # 文档文件",
        "├── 🚀 start_server.sh  # 启动脚本",
        "├── 🧪 test_ui.html     # 测试界面",
        "└── 📄 requirements.txt # Python依赖",
    ]

    for line in structure:
        print(f"   {line}")


async def main():
    """主函数"""
    print_header()
    print_system_info()
    await check_services()
    show_api_endpoints()
    show_usage_examples()
    show_project_structure()

    print("\n" + "=" * 80)
    print("🎉 系统演示完成！")
    print("💡 提示: 运行 './start_server.sh' 启动完整系统")
    print("📖 文档: 查看 README.md 和 USAGE.md 获取详细信息")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
