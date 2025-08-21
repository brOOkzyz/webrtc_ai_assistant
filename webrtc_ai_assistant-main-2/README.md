# WebRTC语音助手

基于WebRTC的实时语音交互系统，集成语音识别、智能对话和语音合成功能。

## 快速开始

### 安装依赖
```bash
cd webrtc_voice_assistant
pip install -r requirements.txt
```

### 配置API密钥
编辑 `webrtc_voice_assistant/config.py` 文件，配置您的API密钥。

### 启动服务
```bash
# Unix/Mac
./start.sh

# Windows
start.bat
```

### 使用客户端
在浏览器中打开 `webrtc_voice_assistant/webrtc_client.html`

## 项目结构
- `webrtc_voice_assistant/` - 核心代码目录
- `start.sh` - Unix/Mac启动脚本
- `start.bat` - Windows启动脚本

详细说明请查看 `webrtc_voice_assistant/项目说明.md`
