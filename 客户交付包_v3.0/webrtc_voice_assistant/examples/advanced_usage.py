#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebRTC语音助手系统 - 高级使用示例
"""

import asyncio
import sys
import os
import time

# 添加包路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from webrtc_voice_assistant import (
    create_server, create_asr, create_llm, create_tts, 
    create_audio_processor, get_info
)

async def advanced_example():
    """高级使用示例"""
    print("🚀 WebRTC语音助手系统 - 高级使用示例")
    print("=" * 60)
    
    # 显示包信息
    info = get_info()
    print(f"📦 包名称: {info['name']}")
    print(f"📋 版本: {info['version']}")
    print(f"👨‍💻 作者: {info['author']}")
    print(f"📄 许可证: {info['license']}")
    
    # 使用快速创建函数
    print("\n🔧 使用快速创建函数...")
    asr = create_asr()
    llm = create_llm()
    tts = create_tts()
    audio_processor = create_audio_processor(buffer_size=100)
    
    print("✅ 所有模块创建成功")
    
    # 创建自定义服务器
    print("\n🌐 创建自定义服务器...")
    server = create_server(host='0.0.0.0', port=8888)
    print("✅ 服务器创建成功")
    
    # 模拟一些操作
    print("\n🧪 模拟模块操作...")
    
    # 模拟ASR操作
    print("🎤 测试ASR模块...")
    test_audio = b'\x00' * 2000  # 模拟音频数据
    # result = asr.recognize_speech(test_audio)  # 实际调用需要网络
    
    # 模拟LLM操作
    print("🤖 测试LLM模块...")
    # response = llm.ask_question("你好", "test_client")  # 实际调用需要API密钥
    
    # 模拟TTS操作
    print("🔊 测试TTS模块...")
    # audio = tts.synthesize_speech("测试语音")  # 实际调用需要网络
    
    print("✅ 所有模块测试完成")
    
    # 启动服务器
    print("\n🚀 启动服务器...")
    print("📍 地址: 0.0.0.0:8888")
    print("💡 使用 webrtc_client.html 连接")
    print("按 Ctrl+C 停止服务器")
    print("-" * 60)
    
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n🛑 服务器被用户中断")
    except Exception as e:
        print(f"\n❌ 服务器启动失败: {e}")

def show_module_info():
    """显示模块信息"""
    print("\n📊 模块信息:")
    print("  🎤 ASR模块: 百度语音识别API")
    print("  🤖 LLM模块: SiliconFlow GLM-4-9B")
    print("  🔊 TTS模块: 百度语音合成API")
    print("  🎵 音频处理: 智能缓冲和静音检测")
    print("  🌐 WebRTC: 实时音频通信")

if __name__ == "__main__":
    show_module_info()
    asyncio.run(advanced_example())
