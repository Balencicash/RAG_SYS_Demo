// RAG Document QA System - Web Interface JavaScript

class RAGClient {
    constructor() {
        this.baseURL = window.location.origin;
        this.apiURL = `${this.baseURL}/api/v1`;
        this.documents = [];
        this.queryCount = 0;
        this.init();
    }

    async init() {
        await this.checkSystemStatus();
        await this.loadDocuments();
        this.updateStats();
        this.setupEventListeners();
        this.setWelcomeTime();
    }

    setupEventListeners() {
        // 文件上传拖拽功能
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            this.handleFiles(files);
        });

        fileInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });
    }

    async checkSystemStatus() {
        try {
            const response = await fetch(`${this.baseURL}/health`);
            const data = await response.json();

            if (response.ok) {
                document.getElementById('systemStatus').className = 'status-indicator status-online';
                document.getElementById('statusText').textContent = '正常';
            } else {
                throw new Error('System not healthy');
            }
        } catch (error) {
            document.getElementById('systemStatus').className = 'status-indicator status-offline';
            document.getElementById('statusText').textContent = '异常';
            console.error('System status check failed:', error);
        }
    }

    async loadDocuments() {
        try {
            const response = await fetch(`${this.apiURL}/documents`);
            if (response.ok) {
                const data = await response.json();
                this.documents = data.documents || [];
                this.renderDocuments();
            }
        } catch (error) {
            console.error('Failed to load documents:', error);
            this.showAlert('加载文档列表失败', 'error');
        }
    }

    updateStats() {
        document.getElementById('docCount').textContent = this.documents.length;
        document.getElementById('queryCount').textContent = this.queryCount;
    }

    setWelcomeTime() {
        const now = new Date();
        document.getElementById('welcomeTime').textContent = now.toLocaleString('zh-CN');
    }

    async handleFiles(files) {
        const statusDiv = document.getElementById('uploadStatus');
        statusDiv.innerHTML = '';

        for (let file of files) {
            if (this.validateFile(file)) {
                await this.uploadFile(file);
            }
        }

        await this.loadDocuments();
        this.updateStats();
    }

    validateFile(file) {
        const allowedTypes = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'text/markdown'
        ];

        const allowedExtensions = ['.pdf', '.doc', '.docx', '.txt', '.md'];
        const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));

        if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
            this.showAlert(`不支持的文件格式: ${file.name}`, 'error');
            return false;
        }

        if (file.size > 50 * 1024 * 1024) { // 50MB limit
            this.showAlert(`文件太大: ${file.name} (最大支持50MB)`, 'error');
            return false;
        }

        return true;
    }

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            this.showAlert(`正在上传: ${file.name}...`, 'info');

            const response = await fetch(`${this.apiURL}/upload`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                this.showAlert(`✅ ${file.name} 上传成功`, 'success');
            } else {
                throw new Error(data.detail || '上传失败');
            }
        } catch (error) {
            console.error('Upload failed:', error);
            this.showAlert(`❌ ${file.name} 上传失败: ${error.message}`, 'error');
        }
    }

    renderDocuments() {
        const grid = document.getElementById('documentsGrid');

        if (this.documents.length === 0) {
            grid.innerHTML = '<p style="text-align: center; color: #666; grid-column: 1/-1;">暂无文档，请先上传文档。</p>';
            return;
        }

        grid.innerHTML = this.documents.map(doc => `
            <div class="document-card">
                <div class="document-icon ${this.getDocumentIconClass(doc.type)}">
                    ${this.getDocumentIcon(doc.type)}
                </div>
                <div class="document-title">${doc.filename}</div>
                <div class="document-meta">
                    类型: ${doc.type}<br>
                    上传时间: ${new Date(doc.upload_time).toLocaleString('zh-CN')}<br>
                    分块数: ${doc.chunks || 0}
                </div>
                <div class="document-actions">
                    <button class="btn btn-small btn-danger" onclick="ragClient.deleteDocument('${doc.id}')">
                        删除
                    </button>
                </div>
            </div>
        `).join('');
    }

    getDocumentIconClass(type) {
        const iconMap = {
            'pdf': 'doc-pdf',
            'word': 'doc-word',
            'text': 'doc-text',
            'markdown': 'doc-markdown'
        };
        return iconMap[type] || 'doc-text';
    }

    getDocumentIcon(type) {
        const iconMap = {
            'pdf': '📄',
            'word': '📃',
            'text': '📝',
            'markdown': '📋'
        };
        return iconMap[type] || '📄';
    }

    async deleteDocument(docId) {
        if (!confirm('确定要删除这个文档吗？')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiURL}/documents/${docId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showAlert('文档删除成功', 'success');
                await this.loadDocuments();
                this.updateStats();
            } else {
                throw new Error('删除失败');
            }
        } catch (error) {
            console.error('Delete failed:', error);
            this.showAlert('文档删除失败', 'error');
        }
    }

    async clearAllDocuments() {
        if (!confirm('确定要清空所有文档吗？此操作不可恢复！')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiURL}/documents/clear`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (response.ok) {
                this.showAlert('所有文档已清空', 'success');
                await this.loadDocuments();
                this.updateStats();
            } else {
                throw new Error(data.detail || '清空失败');
            }
        } catch (error) {
            console.error('Clear all failed:', error);
            this.showAlert(`清空文档失败: ${error.message}`, 'error');
        }
    }

    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();

        if (!message) {
            return;
        }

        if (this.documents.length === 0) {
            this.showAlert('请先上传文档再进行问答', 'error');
            return;
        }

        // 添加用户消息
        this.addMessage('user', message);
        input.value = '';

        // 显示加载状态
        const sendIcon = document.getElementById('sendIcon');
        const originalText = sendIcon.innerHTML;
        sendIcon.innerHTML = '<div class="loading"></div>';

        try {
            const response = await fetch(`${this.apiURL}/question`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: message })
            });

            const data = await response.json();

            if (response.ok) {
                // 确保有有效的回答
                if (data && data.answer && typeof data.answer === 'string') {
                    this.addMessage('assistant', data.answer);
                    this.queryCount++;
                    this.updateStats();
                } else if (data && data.success === true && data.answer) {
                    this.addMessage('assistant', String(data.answer));
                    this.queryCount++;
                    this.updateStats();
                } else {
                    console.error('Invalid response format:', data);
                    throw new Error('服务器返回了无效的响应格式');
                }
            } else {
                throw new Error(data.detail || data.message || '查询失败');
            }
        } catch (error) {
            console.error('Query failed:', error);
            console.error('Error type:', typeof error);
            console.error('Error details:', JSON.stringify(error, null, 2));

            // 多种方式处理错误信息
            let errorMessage = '未知错误';

            if (error.message && typeof error.message === 'string') {
                errorMessage = error.message;
            } else if (typeof error === 'string') {
                errorMessage = error;
            } else if (error.toString && typeof error.toString === 'function') {
                const errorStr = error.toString();
                if (errorStr !== '[object Object]') {
                    errorMessage = errorStr;
                }
            }

            // 如果还是[object Object]，尝试其他方法
            if (errorMessage === '[object Object]' || errorMessage === '未知错误') {
                if (error.name || error.code || error.status) {
                    errorMessage = `错误类型: ${error.name || 'Unknown'}, 状态: ${error.code || error.status || 'N/A'}`;
                } else {
                    errorMessage = '网络请求失败，请检查连接或稍后重试';
                }
            }

            this.addMessage('assistant', `抱歉，查询失败：${errorMessage}`);
        } finally {
            sendIcon.innerHTML = originalText;
        }
    }

    addMessage(sender, content) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        const avatar = sender === 'user' ? '👤' : '🤖';
        const time = new Date().toLocaleString('zh-CN');

        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <div>${content}</div>
                <div class="message-time">${time}</div>
            </div>
        `;

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showAlert(message, type = 'info') {
        const statusDiv = document.getElementById('uploadStatus');
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;

        statusDiv.appendChild(alertDiv);

        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// 页面切换功能
function showPage(pageId, element) {
    // 隐藏所有页面
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });

    // 显示选中页面
    document.getElementById(pageId).classList.add('active');

    // 更新导航链接
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });

    // 如果提供了element，则激活它；否则查找对应的导航链接
    if (element) {
        element.classList.add('active');
    } else {
        // 查找对应的导航链接并激活
        const navLink = document.querySelector(`.nav-link[onclick*="'${pageId}'"]`);
        if (navLink) {
            navLink.classList.add('active');
        }
    }
}

// 键盘事件处理
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        ragClient.sendMessage();
    }
}

// 发送消息
function sendMessage() {
    ragClient.sendMessage();
}

// 清空所有文档
function clearAllDocuments() {
    ragClient.clearAllDocuments();
}

// 初始化应用
let ragClient;
document.addEventListener('DOMContentLoaded', () => {
    ragClient = new RAGClient();
});
