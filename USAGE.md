# 使用指南 - RAG Document QA System

**版权所有 (c) 2024 Balenci Cash - 保留所有权利**

## 🔐 重要提示

本系统包含**数字水印保护技术**，所有核心功能都经过加密和签名保护。任何未经授权的使用、修改或分发都将被追踪和记录。

## 🚀 快速开始

### 1. 环境准备

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件，填入您的 API 密钥
# 必须配置：OPENAI_API_KEY
# 可选配置：LANGCHAIN_API_KEY (用于 LangSmith 追踪)
```

### 2. 启动系统

#### 方法一：使用启动脚本
```bash
./start.sh
```

#### 方法二：手动启动
```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

#### 方法三：Docker 启动
```bash
docker-compose up
```

### 3. 访问服务

- **API 地址**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 📚 API 使用示例

### 1. 上传文档

```python
import requests

# 上传 PDF 文件
with open("document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/upload",
        files={"file": f}
    )
    print(response.json())
```

### 2. 提问

```python
# 提问并获取答案
response = requests.post(
    "http://localhost:8000/api/v1/question",
    json={
        "question": "文档中提到了什么关键内容？",
        "session_id": "optional-session-id"  # 可选，用于多轮对话
    }
)
print(response.json())
```

### 3. 验证水印

```python
# 验证系统水印保护状态
response = requests.get("http://localhost:8000/api/v1/watermark/verify")
print(response.json())
```

## 🔍 水印保护功能

系统在以下层面实施水印保护：

1. **代码执行层**
   - 所有核心函数都被 `@protect` 装饰器保护
   - 每次函数执行都会记录水印信息

2. **数据处理层**
   - 解析的文档包含不可见水印
   - 向量索引带有作者签名
   - API 响应包含水印元数据

3. **API 层**
   - 每个请求都验证水印
   - 响应包含水印签名
   - 支持水印状态查询

## 📊 监控与调试

### 查看日志

日志文件位于 `logs/app.log`，包含：
- 请求处理记录
- 水印验证信息
- 错误追踪
- 性能指标

### LangSmith 追踪

如果配置了 LangSmith API 密钥，可以在 [LangSmith 平台](https://smith.langchain.com) 查看：
- 完整调用链
- LLM 输入输出
- 响应时间分析
- 相似度分数

## ⚠️ 注意事项

1. **API 密钥安全**
   - 不要将 `.env` 文件提交到版本控制
   - 定期轮换 API 密钥
   - 使用环境变量管理敏感信息

2. **水印保护**
   - 不要尝试移除或绕过水印
   - 所有修改都会被记录
   - 未授权使用将承担法律责任

3. **性能优化**
   - 大文档建议分批上传
   - 合理设置 chunk_size 参数
   - 使用会话 ID 优化多轮对话

## 🐛 故障排除

### 常见问题

1. **ImportError: No module named 'xxx'**
   ```bash
   pip install -r requirements.txt
   ```

2. **OpenAI API 错误**
   - 检查 API 密钥是否正确
   - 确认账户有足够额度
   - 检查网络连接

3. **水印验证失败**
   - 不要修改 `src/utils/watermark.py`
   - 确保所有文件完整
   - 联系作者获取授权

## 📧 技术支持

- 作者：Balenci Cash
- 邮箱：balencicash@example.com

---

**免责声明**：本软件受版权法保护，未经授权的使用将承担法律责任。