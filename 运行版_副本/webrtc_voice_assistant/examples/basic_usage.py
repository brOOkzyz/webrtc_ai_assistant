#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebRTC语音助手系统 - 基本使用示例
"""

import asyncio
import sys
import os

# 添加包路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from webrtc_voice_assistant import WebRTCServer, ASRModule, LLMModule, TTSModule

async def basic_example():
    """基本使用示例"""
    print("🚀 WebRTC语音助手系统 - 基本使用示例")
    print("=" * 50)
    
    # 创建功能模块
    print("📦 创建功能模块...")
    asr = ASRModule()
    llm = LLMModule()
    tts = TTSModule()
    
    print("✅ ASR模块创建成功")
    print("✅ LLM模块创建成功") 
    print("✅ TTS模块创建成功")
    
    # 创建服务器
    print("\n🌐 创建WebRTC服务器...")
    server = WebRTCServer(host='localhost', port=8765)
    print("✅ 服务器创建成功")
    
    # 启动服务器
    print("\n🚀 启动服务器...")
    print("📍 地址: localhost:8765")
    print("💡 使用 webrtc_client.html 连接")
    print("按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n🛑 服务器被用户中断")
    except Exception as e:
        print(f"\n❌ 服务器启动失败: {e}")

if __name__ == "__main__":
    asyncio.run(basic_example())
