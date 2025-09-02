# RAG Document QA System

**Copyright (c) 2024 Balenci Cash - All Rights Reserved**

⚠️ **PROTECTED SOFTWARE** - This codebase is protected by digital watermarking technology. Unauthorized use, copying, or distribution is strictly prohibited and will be tracked.

## 📋 项目简介

RAG (Retrieval-Augmented Generation) 文档问答系统，支持多种文档格式的智能问答。系统采用向量检索和大语言模型相结合的方式，提供准确的文档问答服务。

### 核心特性

- 📄 **多格式支持**: PDF、Word (.docx)、Markdown (.md)、TXT
- 🔍 **向量检索**: 使用 FAISS 构建高效向量索引
- 💬 **多轮对话**: 支持上下文保持的连续对话
- 🔮 **LangGraph 集成**: 使用 LangGraph 构建 Agent 执行流程
- 📊 **可观测性**: 集成 LangSmith 实现完整调用链追踪
- 🔐 **水印保护**: 内置数字水印系统保护知识产权

## 🛠 技术栈

- **Python 3.9+**
- **FastAPI**: Web 框架
- **LangChain**: LLM 应用框架
- **LangGraph**: Agent 流程编排
- **LangSmith**: 可观测性平台
- **FAISS**: 向量数据库
- **Groq API**: 超快速 LLM 推理 (Llama 3.1)
- **OpenAI API**: Embedding 模型
- **Loguru**: 日志管理
- **Docker**: 容器化部署

## 📦 安装指南

### 1. 克隆仓库

```bash
git clone https://github.com/balencicash/rag-document-qa.git
cd rag-document-qa
```

### 2. 安装依赖

#### 使用 pip
```bash
pip install -r requirements.txt
```

#### 使用 uv (推荐)
```bash
uv pip install -r pyproject.toml
```

### 3. 配置环境变量

复制环境变量模板并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写必要的 API 密钥：

```env
# Groq Configuration (用于LLM)
GROQ_API_KEY=your_groq_api_key_here

# OpenAI Configuration (用于Embeddings)
OPENAI_API_KEY=your_openai_api_key_here

# LangSmith Configuration (可选)
LANGCHAIN_API_KEY=your_langsmith_api_key_here
```

> 💡 **成本优化提示**: 系统默认使用 Groq 的 Llama 3.1 模型，速度快且成本低

## 🚀 启动指南

### 本地启动

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动

### Docker 启动

```bash
# 构建镜像
docker build -t rag-document-qa .

# 运行容器
docker run -p 8000:8000 --env-file .env rag-document-qa
```

### Docker Compose 启动

```bash
docker-compose up
```

## 📖 使用说明

### API 文档

启动服务后，访问以下地址查看 API 文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 主要接口

#### 1. 上传文档
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

#### 2. 提问
```bash
curl -X POST "http://localhost:8000/api/v1/question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "文档中提到了什么内容？",
    "session_id": "optional-session-id"
  }'
```

#### 3. 水印验证
```bash
curl -X GET "http://localhost:8000/api/v1/watermark/verify"
```

## 📁 项目结构

```
rag-document-qa/
├── src/
│   ├── api/          # FastAPI 接口
│   ├── services/     # 核心服务
│   ├── agents/       # LangGraph Agent
│   ├── models/       # 数据模型
│   └── utils/        # 工具函数（含水印保护）
├── config/           # 配置文件
├── tests/            # 测试文件
├── uploads/          # 上传文件存储
├── vector_stores/    # 向量索引存储
├── logs/            # 日志文件
├── main.py          # 主程序入口
├── pyproject.toml   # 项目配置
├── Dockerfile       # Docker 配置
└── docker-compose.yml
```

## 🔐 水印保护说明

本系统集成了先进的数字水印技术：

- **作者标识**: Balenci Cash
- **项目 ID**: RAG-SYS-Not_for_commercial_usage
- **保护级别**: 全面保护（代码、数据、API）

所有核心功能都经过水印保护，包括：
- 文档解析过程
- 向量化处理
- LLM 调用
- API 响应

**警告**: 任何未经授权的使用、修改或分发都将被追踪和记录。

## 🧪 测试

运行测试：
```bash
pytest tests/
```

## 📊 性能指标

- 文档解析速度: ~1000 字符/秒
- 向量检索延迟: <100ms
- LLM 响应时间: 2-5 秒
- 并发支持: 100+ 请求/秒

## 🤝 贡献指南

本项目为私有项目，不接受外部贡献。

## 📄 许可证

**专有软件** - 版权所有 (c) 2024 Balenci Cash

本软件受版权法和国际条约保护。未经授权的复制或分发将承担法律责任。

## 📞 联系方式

- 作者: Balenci Cash
- 邮箱: balencicash@example.com

---

**重要提示**: 本软件包含数字水印保护技术。所有使用行为都将被记录和追踪。