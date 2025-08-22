# 📦 WebRTC语音助手系统 - 安装说明

## 🎯 安装方式

本系统支持多种安装方式，用户可以根据需要选择：

### 1. **开发模式安装（推荐）**

```bash
# 克隆项目
git clone https://github.com/example/webrtc-voice-assistant.git
cd webrtc-voice-assistant

# 开发模式安装
pip install -e .
```

**优势**：
- 代码修改后立即生效
- 便于开发和调试
- 包含所有开发工具

### 2. **正式安装**

```bash
# 从源码安装
pip install .

# 或者从PyPI安装（如果已发布）
pip install webrtc-voice-assistant
```

**优势**：
- 安装到系统Python环境
- 全局可用
- 标准安装方式

### 3. **虚拟环境安装（推荐）**

```bash
# 创建虚拟环境
python -m venv webrtc_env

# 激活虚拟环境
# Windows
webrtc_env\Scripts\activate
# Linux/macOS
source webrtc_env/bin/activate

# 安装包
pip install -e .
```

**优势**：
- 环境隔离
- 避免依赖冲突
- 便于管理

## 🔧 依赖安装

### 核心依赖

```bash
# 安装核心依赖
pip install websockets requests

# 或者使用requirements.txt
pip install -r requirements.txt
```

### 可选依赖

```bash
# 安装完整功能依赖
pip install -e .[full]

# 安装开发依赖
pip install -e .[dev]
```

### 依赖说明

| 依赖包 | 版本 | 用途 | 必需性 |
|--------|------|------|--------|
| `websockets` | >=10.0 | WebSocket通信 | ✅ 必需 |
| `requests` | >=2.25.0 | HTTP API调用 | ✅ 必需 |
| `psutil` | >=5.8.0 | 系统监控 | 🔶 可选 |
| `numpy` | >=1.20.0 | 数值计算 | 🔶 可选 |
| `scipy` | >=1.7.0 | 科学计算 | 🔶 可选 |

## 🚀 快速验证

### 1. **检查安装**

```bash
# 检查包是否正确安装
python -c "import webrtc_voice_assistant; print('✅ 安装成功！')"

# 查看包信息
webrtc-voice-assistant info
```

### 2. **运行示例**

```bash
# 运行基本示例
python examples/basic_usage.py

# 运行高级示例
python examples/advanced_usage.py
```

### 3. **启动服务器**

```bash
# 使用命令行工具
webrtc-voice-assistant start

# 或者直接运行
python -m webrtc_voice_assistant.server
```

## 🌍 系统要求

### Python版本
- **最低版本**: Python 3.8
- **推荐版本**: Python 3.9+
- **测试版本**: Python 3.8, 3.9, 3.10, 3.11, 3.12

### 操作系统
- ✅ **Windows**: 10/11
- ✅ **macOS**: 10.15+
- ✅ **Linux**: Ubuntu 18.04+, CentOS 7+

### 硬件要求
- **内存**: 4GB+ (推荐8GB)
- **CPU**: 双核+ (推荐四核)
- **网络**: 稳定连接
- **存储**: 100MB+ 可用空间

## 🔍 故障排除

### 常见问题

#### 1. **导入错误**
```bash
# 错误: ModuleNotFoundError: No module named 'webrtc_voice_assistant'
# 解决: 确保在正确的目录下安装
cd webrtc_voice_assistant
pip install -e .
```

#### 2. **依赖冲突**
```bash
# 错误: ImportError: cannot import name 'xxx'
# 解决: 使用虚拟环境
python -m venv env
source env/bin/activate  # Linux/macOS
pip install -e .
```

#### 3. **权限问题**
```bash
# 错误: Permission denied
# 解决: 使用用户安装
pip install --user -e .
```

#### 4. **版本兼容性**
```bash
# 错误: Python version not supported
# 解决: 升级Python到3.8+
python --version
```

### 调试模式

```bash
# 启用详细日志
webrtc-voice-assistant start --verbose

# 或者设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m webrtc_voice_assistant.server
```

## 📚 开发环境设置

### 1. **克隆开发版本**

```bash
git clone https://github.com/example/webrtc-voice-assistant.git
cd webrtc-voice-assistant
git checkout develop  # 如果有开发分支
```

### 2. **安装开发依赖**

```bash
pip install -e .[dev]
```

### 3. **代码质量工具**

```bash
# 代码格式化
black webrtc_voice_assistant/

# 代码检查
flake8 webrtc_voice_assistant/

# 类型检查
mypy webrtc_voice_assistant/

# 运行测试
pytest
```

## 🔄 更新和升级

### 更新源码

```bash
git pull origin main
pip install -e . --upgrade
```

### 更新依赖

```bash
pip install --upgrade -r requirements.txt
```

### 清理安装

```bash
pip uninstall webrtc-voice-assistant
pip install -e .  # 重新安装
```

## 📞 获取帮助

如果遇到安装问题：

1. **查看日志**: 启用详细日志模式
2. **检查版本**: 确认Python和依赖版本
3. **搜索问题**: 在GitHub Issues中搜索
4. **提交问题**: 创建新的Issue描述问题
5. **联系支持**: 发送邮件到support@example.com

## 🎉 安装完成

恭喜！WebRTC语音助手系统已经成功安装。

现在你可以：
- 🚀 启动服务器: `webrtc-voice-assistant start`
- 📖 查看文档: 阅读README.md和示例代码
- 🧪 运行示例: 执行examples目录下的示例
- 🔧 开始开发: 修改代码并测试功能

祝你使用愉快！🎊
