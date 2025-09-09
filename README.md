# RAG Document QA System v2.0

> ⚠️ **技术展示项目** - 请查看 [LICENSE.md](LICENSE.md) 和 [NOTICE.md](NOTICE.md) 了解使用条款

一个基于现代AI技术的文档问答系统，提供智能文档分析和对话式问答体验。

## 🛡️ 项目声明

本项目为**技术能力展示**，包含完整的RAG系统实现和多层保护机制：

- ✅ **学习研究**：欢迎学习和研究代码实现
- ❌ **商业使用**：直接商业使用需要授权许可
- 🔒 **保护机制**：内置完整性验证和追踪系统
- 📧 **商业合作**：技术合作请通过 Issues 联系

## ✨ 主要特性

- 🚀 **现代化Web界面**：响应式设计，类ChatGPT用户体验
- 📄 **智能文档处理**：支持多种文档格式的自动解析和向量化
- 🤖 **先进RAG技术**：结合检索增强生成，提供准确的上下文相关答案
- � **LangSmith工作流追踪**：完整的RAG流程监控和性能分析 ⭐ **新功能**
- �🔒 **本地化部署**：数据安全，支持完全本地运行
- ⚡ **高性能API**：基于FastAPI的现代RESTful接口
- 🎨 **直观UI设计**：深色主题，现代化交互体验

## 🛠️ 技术栈

- **后端**：Python 3.12 + FastAPI + LangChain
- **前端**：HTML5 + CSS3 + JavaScript (原生)
- **AI模型**：Groq (llama-3.1-8b-instant) + Ollama (nomic-embed-text)
- **向量数据库**：FAISS
- **追踪监控**：LangSmith (可选)
- **文档处理**：LangChain Document Loaders

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/Balencicash/RAG_SYS_Demo.git
cd RAG_SYS_Demo

# 安装uv（Python包管理器）
pip install uv

# 安装项目依赖
uv sync

# 启动Ollama（用于嵌入模型）
ollama serve
ollama pull nomic-embed-text
```

### 2. 配置环境

创建`.env`文件：

```bash
# Groq API配置
GROQ_API_KEY=your_groq_api_key_here

# LangSmith配置（可选）
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=rag-document-qa
LANGCHAIN_TRACING_V2=true
```

### 3. 启动系统

```bash
# 方式1：使用启动脚本
chmod +x start_server.sh
./start_server.sh

# 方式2：直接使用uv运行
uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### 4. 访问系统

- **Web界面**：http://localhost:8000
- **API文档**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/health

## 💻 使用方法

### Web界面使用

1. **上传文档**：将TXT文件拖拽到上传区域或点击选择文件
2. **开始对话**：在聊天框中输入问题
3. **查看回答**：系统会基于文档内容提供准确回答
4. **管理文档**：通过文档管理页面查看和删除已上传文档

### API使用示例

```bash
# 上传文档
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.txt"

# 提问查询
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "文档的主要内容是什么？"}'

# 查看文档列表
curl -X GET "http://localhost:8000/api/v1/documents"
```

## 🛠️ 开发指南

### 使用uv进行开发

```bash
# 安装开发依赖
uv sync --dev

# 添加新依赖
uv add package-name

# 添加开发依赖
uv add --dev package-name

# 运行代码格式化
uv run black src/
uv run ruff check src/

# 运行类型检查
uv run mypy src/

# 运行测试
uv run pytest
```

### Docker开发

```bash
# 构建镜像
docker build -t rag-showcase .

# 运行容器
docker-compose up -d
```

## 📚 API文档

系统提供完整的RESTful API：

| 端点 | 方法 | 描述 |
|-----|------|------|
| `/` | GET | Web界面首页 |
| `/health` | GET | 系统健康检查 |
| `/api/v1/upload` | POST | 上传文档 |
| `/api/v1/query` | POST | RAG查询 |
| `/api/v1/documents` | GET | 文档列表 |
| `/api/v1/documents/clear` | DELETE | 清空所有文档 |

详细API文档请访问：http://localhost:8000/docs

## 🏗️ 项目结构

```
RAG-Document-QA-System-v2.0/
├── web/                     # Web前端
│   ├── index.html          # 主页面
│   └── app.js              # JavaScript客户端
├── src/                     # 源代码
│   ├── agents/             # RAG代理
│   ├── api/                # FastAPI路由
│   ├── services/           # 核心服务
│   └── utils/              # 工具函数
├── config/                  # 配置文件
├── uploads/                 # 文档存储
├── vector_stores/           # 向量数据库
├── requirements.txt         # Python依赖
├── start_server.sh         # 启动脚本
└── README.md               # 项目文档
```

## 🔧 配置说明

### LLM配置 (config/llm_config.py)
- **Groq API**：用于文本生成
- **Ollama**：用于文档嵌入
- **模型参数**：温度、最大令牌等

### LangSmith 追踪配置 ⭐ **新功能**
项目集成了完整的 LangSmith 工作流追踪功能：

**环境变量设置：**
```bash
LANGCHAIN_API_KEY=your_langsmith_api_key_here  # 必需
LANGCHAIN_PROJECT=rag-document-qa              # 项目名称
LANGCHAIN_TRACING_V2=true                      # 启用追踪
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com  # 可选，默认端点
```

**功能特性：**
- 🔍 **RAG工作流追踪**：完整记录文档检索→答案生成流程
- 📊 **性能监控**：查询响应时间、检索准确性统计
- 🏷️ **智能标签**：自动标记工作流类型和系统组件
- 🎯 **错误追踪**：详细记录异常和失败原因
- 📈 **对话追踪**：会话级别的多轮对话历史

**监控端点：**
- `GET /api/v1/system/langsmith` - 查看追踪配置状态

### 向量存储配置 (config/vector_config.py)
- **FAISS**：本地向量数据库
- **嵌入维度**：1536维
- **相似性搜索**：余弦相似度

### API配置 (config/api_config.py)
- **服务器端口**：8000
- **CORS设置**：支持跨域请求
- **文件上传**：大小限制和格式验证

## 🛡️ 安全特性

- **元数据追踪**：完整的系统日志和监控
- **本地处理**：文档数据不离开本地环境
- **输入验证**：严格的API参数验证
- **错误处理**：完善的异常处理机制

## 📈 性能特点

- **快速启动**：优化的启动流程，几秒内可用
- **高效检索**：FAISS向量搜索，毫秒级响应
- **内存优化**：智能文档分块，降低内存使用
- **并发支持**：异步API，支持多用户同时使用

## 🔍 故障排除

### 常见问题

1. **Ollama连接失败**
   ```bash
   # 确保Ollama正在运行
   ollama serve
   ```

2. **Groq API错误**
   ```bash
   # 检查API密钥是否正确配置
   echo $GROQ_API_KEY
   ```

3. **端口被占用**
   ```bash
   # 修改config/api_config.py中的端口设置
   api_port: int = 8001  # 改为其他端口
   ```

### 日志查看

```bash
# 查看服务器日志
tail -f server.log

# 查看详细错误
tail -f logs/app.log
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证与法律声明

### 🔒 知识产权保护
Copyright (c) 2025 BalenciCash - All Rights Reserved

本项目采用**自定义技术展示许可证**，详情请查看：
- [LICENSE.md](LICENSE.md) - 完整许可条款
- [NOTICE.md](NOTICE.md) - 使用须知

### ⚖️ 使用条款
- **个人学习**：✅ 允许用于学习和研究
- **技术参考**：✅ 允许参考实现思路  
- **商业使用**：❌ 需要明确授权许可
- **二次分发**：❌ 禁止重新打包分发
- **保护移除**：❌ 禁止移除内置保护机制

### 🤝 商业合作
如需商业授权或技术合作：
- 📧 通过 GitHub Issues 联系
- 💼 提供详细的使用场景说明
- 🤝 我们将提供定制化授权方案

### 🛡️ 技术保护说明
本系统包含多层保护机制：
- 代码完整性验证
- 运行环境检测
- 使用行为追踪
- 数字签名验证

**请尊重开发者的知识产权，合规使用本项目。**

---

## 🎯 更新日志

### v2.0 (2025-09-03)
- ✅ 全新Web界面设计
- ✅ 简化架构，移除LangGraph依赖
- ✅ 优化RAG流程和错误处理
- ✅ 增加文档管理功能
- ✅ 完善API文档和测试

### v1.0
- 基础RAG功能
- 命令行界面
- 基础API接口
