#!/bin/bash

# 启动简化版本的ASR+LLM+TTS系统
echo "🚀 启动简化版本的ASR+LLM+TTS系统..."
echo "=================================="

# 检查Python版本
echo "🔍 检查Python环境..."
python3 --version

# 检查依赖
echo "🔍 检查依赖模块..."
python3 -c "
try:
    import pyaudio
    import websocket
    import speech_recognition
    import numpy
    from aip import AipSpeech
    print('✅ 所有依赖模块导入成功')
except ImportError as e:
    print(f'❌ 依赖模块导入失败: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ 依赖检查失败，请先安装必要的模块"
    echo "💡 建议运行: pip3 install -r requirements.txt"
    exit 1
fi

# 检查配置文件
echo "🔍 检查配置文件..."
if [ ! -f "config.py" ]; then
    echo "❌ 配置文件 config.py 不存在"
    exit 1
fi

if [ ! -f "流式_副本2/const.py" ]; then
    echo "❌ 百度配置文件不存在"
    exit 1
fi

if [ ! -f "tts_streaming.py" ]; then
    echo "❌ TTS模块文件不存在"
    exit 1
fi

echo "✅ 配置文件检查通过"

# 运行测试
echo "🧪 运行系统测试..."
python3 test_quick_fix.py

if [ $? -ne 0 ]; then
    echo "❌ 系统测试失败，请检查问题"
    exit 1
fi

echo "✅ 系统测试通过"

# 启动主程序
echo "🎯 启动简化版本主程序..."
echo "💡 简化版本特点："
echo "   🔇 TTS不会被语音打断"
echo "   🔊 语音将完整播放"
echo "   ⏰ 请等待TTS播放完成后再说话"
echo "=================================="

# 启动主程序
python3 asr_llm_working.py
