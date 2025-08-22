# WebRTC语音助手系统 v2.0.0

一个基于WebRTC的实时语音交互系统，集成了ASR语音识别、LLM智能对话和TTS语音合成功能。

## 🌟 主要特性

- **实时语音交互**: 基于WebRTC技术，支持低延迟的语音通信
- **智能语音识别**: 集成百度ASR API，提供高精度语音转文字服务
- **智能对话**: 基于SiliconFlow LLM API，支持自然语言交互
- **自然语音合成**: 集成百度TTS API，生成自然流畅的语音回复
- **模块化架构**: 清晰的代码结构，易于维护和扩展
- **多客户端支持**: 支持多个客户端同时连接
- **实时监控**: 提供详细的日志和性能监控

## 🏗️ 系统架构

```
┌─────────────────┐    WebSocket    ┌─────────────────┐
│   Web客户端     │ ◄──────────────► │   服务器端       │
│  (HTML/JS)     │                 │                 │
└─────────────────┘                 │  ┌─────────────┐ │
                                    │  │  ASR模块    │ │
                                    │  │ (语音识别)   │ │
                                    │  └─────────────┘ │
                                    │                 │
                                    │  ┌─────────────┐ │
                                    │  │  LLM模块    │ │
                                    │  │ (智能对话)   │ │
                                    │  └─────────────┘ │
                                    │                 │
                                    │  ┌─────────────┐ │
                                    │  │  TTS模块    │ │
                                    │  │ (语音合成)   │ │
                                    │  └─────────────┘ │
                                    └─────────────────┘
```

## 📋 系统要求

- **Python**: 3.7+
- **操作系统**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **内存**: 至少2GB可用内存
- **网络**: 稳定的互联网连接（用于API调用）

## 🚀 快速开始

### 1. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd webrtc-voice-assistant

# 安装Python依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

编辑 `config.py` 文件，配置您的API密钥：

```python
# LLM API配置
API_KEY = "your-siliconflow-api-key"

# ASR API配置
ASR_API_KEY = "your-baidu-asr-api-key"
ASR_SECRET_KEY = "your-baidu-asr-secret-key"

# TTS API配置
TTS_API_KEY = "your-baidu-tts-api-key"
TTS_SECRET_KEY = "your-baidu-tts-secret-key"
```

### 3. 启动服务器

```bash
# 使用启动脚本（推荐）
python start_server.py

# 或直接启动
python server.py
```

### 4. 连接客户端

在浏览器中打开 `webrtc_client.html`，点击"连接服务器"开始使用。

## 📁 项目结构

```
webrtc-voice-assistant/
├── server.py                 # 主服务器文件
├── start_server.py           # 启动脚本
├── config.py                 # 配置文件
├── asr_module.py             # 语音识别模块
├── llm_module.py             # 智能对话模块
├── tts_module.py             # 语音合成模块
├── audio_processor.py        # 音频处理模块
├── utils.py                  # 工具函数
├── webrtc_client.html        # Web客户端
├── requirements.txt          # Python依赖
├── README.md                 # 项目说明
└── logs/                     # 日志目录
```

## 🔧 配置说明

### 服务器配置

```python
# 服务器监听配置
SERVER_HOST = "localhost"      # 监听地址
SERVER_PORT = 8765             # 监听端口

# 线程池配置
THREAD_POOL_MAX_WORKERS = 20   # 最大工作线程数
```

### 音频配置

```python
# 音频格式参数
AUDIO_SAMPLE_RATE = 16000      # 采样率：16kHz
AUDIO_CHANNELS = 1             # 声道数：单声道
AUDIO_BUFFER_SIZE = 1024       # 音频缓冲区大小

# 语音检测参数
SILENCE_THRESHOLD = 1.0        # 静音检测阈值（秒）
```

### API超时配置

```python
# API超时设置
API_TIMEOUTS = {
    'ASR_TOKEN': 5,            # ASR令牌获取超时（秒）
    'ASR_REQUEST': 8,          # ASR请求超时（秒）
    'LLM_REQUEST': 15,         # LLM请求超时（秒）
    'TTS_TOKEN': 5,            # TTS令牌获取超时（秒）
    'TTS_REQUEST': 10,         # TTS请求超时（秒）
}
```

## 📖 使用说明

### 基本操作流程

1. **连接服务器**: 点击"连接服务器"按钮
2. **开始录音**: 点击"开始录音"按钮，允许麦克风权限
3. **语音输入**: 对着麦克风说话
4. **智能处理**: 系统自动进行语音识别、智能对话和语音合成
5. **语音回复**: 听到系统的语音回复

### 高级功能

- **TTS打断**: 在系统回复时说话，系统会自动停止TTS并处理新的语音输入
- **文本输入**: 支持直接输入文字进行对话
- **连接状态**: 实时显示连接状态和音频质量

### 故障排除

#### 常见问题

1. **无法连接服务器**
   - 检查服务器是否启动
   - 确认端口8765未被占用
   - 检查防火墙设置

2. **麦克风权限问题**
   - 确保浏览器允许麦克风访问
   - 检查系统麦克风设置
   - 尝试刷新页面

3. **语音识别失败**
   - 检查ASR API配置
   - 确认网络连接正常
   - 检查音频输入质量

4. **智能回复异常**
   - 检查LLM API配置
   - 确认API密钥有效
   - 检查网络连接

## 🔍 监控和日志

### 日志级别

- **INFO**: 一般信息
- **WARNING**: 警告信息
- **ERROR**: 错误信息
- **DEBUG**: 调试信息

### 性能监控

系统提供以下监控指标：

- 音频处理统计
- API调用性能
- 内存使用情况
- 客户端连接状态

### 日志文件

- `server.log`: 服务器运行日志
- `startup.log`: 启动过程日志

## 🛠️ 开发指南

### 添加新功能

1. **创建新模块**: 在相应目录下创建新的Python文件
2. **注册模块**: 在服务器中注册新模块
3. **更新配置**: 在config.py中添加相关配置
4. **编写测试**: 为新功能编写测试代码

### 代码规范

- 使用中文注释说明功能
- 遵循PEP 8代码风格
- 添加类型注解
- 编写详细的文档字符串

### 错误处理

- 使用try-catch包装所有外部调用
- 记录详细的错误日志
- 提供用户友好的错误信息
- 实现优雅的降级策略

## 📊 性能优化

### 已实现的优化

- 音频缓冲区管理
- 异步处理架构
- 线程池优化
- 超时控制
- 错误重试机制

### 进一步优化建议

- 实现音频压缩
- 添加缓存机制
- 优化网络传输
- 实现负载均衡

## 🔒 安全考虑

### 当前安全措施

- API密钥管理
- 输入验证
- 错误信息过滤
- 超时控制

### 建议的安全增强

- 添加身份认证
- 实现访问控制
- 加密通信
- 审计日志

## 📈 扩展计划

### 短期目标

- [ ] 支持更多ASR服务
- [ ] 添加语音情感识别
- [ ] 实现多语言支持
- [ ] 优化音频质量

### 长期目标

- [ ] 支持视频通话
- [ ] 实现群组对话
- [ ] 添加语音命令
- [ ] 集成更多AI服务

## 🤝 贡献指南

欢迎贡献代码和提出建议！

### 贡献方式

1. Fork项目
2. 创建功能分支
3. 提交代码更改
4. 创建Pull Request

### 代码审查

- 所有代码更改需要经过审查
- 确保代码质量和测试覆盖
- 遵循项目的编码规范



## 🙏 致谢

感谢以下开源项目和服务：

- [WebSocket](https://websockets.readthedocs.io/) - WebSocket通信
- [百度AI开放平台](https://ai.baidu.com/) - ASR和TTS服务
- [SiliconFlow](https://siliconflow.cn/) - LLM服务
- [Python](https://www.python.org/) - 编程语言

---

**注意**: 使用本系统前请确保您已获得相关API服务的授权，并遵守其使用条款。
