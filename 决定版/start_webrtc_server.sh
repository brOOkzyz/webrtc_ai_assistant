#!/bin/bash

echo "🚀 启动WebRTC语音助手服务器"
echo "=================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3"
    echo "请先安装Python3"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
python3 -c "import websockets" 2>/dev/null || {
    echo "❌ 缺少websockets依赖，正在安装..."
    pip3 install websockets
}

python3 -c "import requests" 2>/dev/null || {
    echo "❌ 缺少requests依赖，正在安装..."
    pip3 install requests
}

# 检查配置文件
if [ ! -f "config.py" ]; then
    echo "❌ 错误: 未找到config.py配置文件"
    echo "请先配置API密钥等信息"
    exit 1
fi

# 启动服务器
echo "✅ 依赖检查完成"
echo "🌐 启动WebRTC服务器..."
echo "💡 服务器将在 http://localhost:8765 启动"
echo "💡 客户端可以通过 webrtc_client.html 连接"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "=================================="

python3 server.py
