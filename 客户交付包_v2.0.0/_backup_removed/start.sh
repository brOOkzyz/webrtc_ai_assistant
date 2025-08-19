#!/bin/bash

# 🎯 ASR + LLM + TTS 语音对话系统启动脚本
# 客户交付版本

echo "🎯 ASR + LLM + TTS 语音对话系统"
echo "=================================="
echo "正在启动系统..."

# 检查Python版本
python_version=$(python3 --version 2>&1)
if [[ $? -ne 0 ]]; then
    echo "❌ 错误: 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

echo "✅ Python版本: $python_version"

# 检查依赖包
echo "🔍 检查依赖包..."
if ! python3 -c "import pyaudio, websocket, requests, speech_recognition" 2>/dev/null; then
    echo "⚠️ 检测到缺少依赖包，正在安装..."
    pip3 install -r requirements.txt
    if [[ $? -ne 0 ]]; then
        echo "❌ 依赖包安装失败，请手动运行: pip3 install -r requirements.txt"
        exit 1
    fi
    echo "✅ 依赖包安装完成"
else
    echo "✅ 依赖包检查通过"
fi

# 检查配置文件
echo "🔍 检查配置文件..."
if [[ ! -f "config.py" ]]; then
    echo "❌ 错误: 未找到config.py配置文件"
    echo "请先配置您的API密钥"
    exit 1
fi

if [[ ! -f "baidu_tts_config.py" ]]; then
    echo "❌ 错误: 未找到baidu_tts_config.py配置文件"
    echo "请先配置您的百度TTS服务"
    exit 1
fi

echo "✅ 配置文件检查通过"

# 启动主程序
echo "🚀 启动主程序..."
echo "=================================="
echo "💡 提示: 按Ctrl+C可以安全退出程序"
echo "=================================="

python3 asr_llm_working.py
