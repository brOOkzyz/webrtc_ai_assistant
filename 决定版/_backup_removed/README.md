# SiliconFlow LLM 聊天机器人 + 语音识别

这是一个功能完整的Python项目，包含：
- 🤖 LLM聊天机器人（支持打字机效果）
- 🎤 实时语音识别功能
- 📡 流式API响应

## 功能特点

### LLM聊天机器人
- 🤖 支持多种LLM模型（默认使用Qwen/QwQ-32B）
- 📡 流式API响应，实时显示生成内容
- ⌨️ 打字机效果，逐字符显示文本
- 💬 支持多轮对话，保持对话历史
- 🔑 使用您提供的API密钥进行身份验证

### 语音识别功能
- 🎤 实时麦克风音频捕获
- 🔄 流式语音识别
- 🌐 基于百度语音识别API
- ⚡ 低延迟实时处理

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. LLM聊天机器人

#### 快速启动（推荐）
```bash
./start.sh
```

#### 手动启动
```bash
# 测试API连接
python3 test_api.py

# 运行聊天机器人
python3 run_chat.py

# 查看打字机效果演示
python3 src/simple_demo.py
```

### 2. 语音识别

```bash
cd 流式_副本2
python realtime_asr2.py
```

**注意**: 语音识别需要麦克风权限，按 `Ctrl+C` 停止录音。

## 配置选项

### LLM配置 (`config.py`)
- `API_KEY`: 您的SiliconFlow API密钥
- `MODEL`: 使用的LLM模型名称
- `temperature`: 控制回复的创造性（0.0-1.0）
- `max_tokens`: 单次回复的最大token数量

### 语音识别配置 (`流式_副本2/const.py`)
- `APPID`: 百度语音识别应用ID
- `APPKEY`: 百度语音识别应用密钥
- `DEV_PID`: 识别模型ID
- `URI`: WebSocket连接地址

## 项目结构

```
project/
├── README.md                 # 项目说明文档
├── requirements.txt          # Python依赖包列表
├── config.py                # LLM配置文件
├── run_chat.py              # LLM聊天启动脚本
├── test_api.py              # API连接测试脚本
├── start.sh                 # 快速启动脚本
├── src/                     # LLM源代码目录
│   ├── llm_chat.py          # 主要的聊天机器人脚本
│   └── simple_demo.py       # 打字机效果演示脚本
└── 流式_副本2/              # 语音识别目录
    ├── realtime_asr2.py     # 实时语音识别脚本
    └── const.py             # 语音识别配置
```

## API文档

- **LLM API**: [SiliconFlow API文档](https://docs.siliconflow.cn/cn/api-reference/chat-completions/chat-completions)
- **语音识别**: 基于百度语音识别服务

## 注意事项

- 请确保您的API密钥有效且有足够的配额
- 流式响应需要稳定的网络连接
- 支持Ctrl+C中断程序
- 语音识别需要麦克风权限和稳定的网络连接
- 语音识别使用百度服务，需要相应的账号和配置
