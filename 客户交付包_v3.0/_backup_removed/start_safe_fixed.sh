#!/bin/bash

echo "🎯 启动修复版 ASR + LLM + TTS 系统"
echo "=================================="
echo "🛡️ 此版本修复了段错误问题"
echo "🔧 改进了音频处理和错误处理"
echo "=================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查必要的依赖
echo "🔍 检查依赖..."
python3 -c "import pyaudio" 2>/dev/null || {
    echo "❌ PyAudio未安装，正在安装..."
    pip3 install pyaudio
}

python3 -c "import speech_recognition" 2>/dev/null || {
    echo "❌ SpeechRecognition未安装，正在安装..."
    pip3 install SpeechRecognition
}

python3 -c "import websocket" 2>/dev/null || {
    echo "❌ websocket-client未安装，正在安装..."
    pip3 install websocket-client
}

python3 -c "import aip" 2>/dev/null || {
    echo "❌ 百度ASR库未安装，正在安装..."
    pip3 install baidu-aip
}

echo "✅ 依赖检查完成"

# 启动系统
echo "🚀 启动修复版系统..."
python3 asr_llm_safe_fixed.py
