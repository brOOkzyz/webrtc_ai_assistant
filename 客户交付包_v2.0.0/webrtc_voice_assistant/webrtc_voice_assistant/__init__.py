#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebRTC语音助手系统 - Python包

一个完整的语音助手系统，集成ASR语音识别、LLM智能对话、TTS语音合成功能。
支持WebRTC实时通信，提供低延迟的语音交互体验。

主要功能:
- 🎤 实时语音识别 (ASR)
- 🤖 智能对话系统 (LLM)  
- 🔊 语音合成播放 (TTS)
- 🛑 用户打断功能
- 🌐 WebRTC实时通信

作者: AI Assistant
版本: 2.0.0
许可证: MIT
"""

from .server import WebRTCServer
from .asr_module import ASRModule
from .llm_module import LLMModule
from .tts_module import TTSModule
from .audio_processor import AudioProcessor
from .config import BASE_URL, DEFAULT_MODEL

__version__ = "2.0.0"
__author__ = "AI Assistant"
__license__ = "MIT"

__all__ = [
    'WebRTCServer',
    'ASRModule', 
    'LLMModule',
    'TTSModule',
    'AudioProcessor',
    'BASE_URL',
    'DEFAULT_MODEL'
]

# 包信息
PACKAGE_INFO = {
    'name': 'webrtc_voice_assistant',
    'version': __version__,
    'description': 'WebRTC语音助手系统 - 集成ASR+LLM+TTS的完整解决方案',
    'author': __author__,
    'license': __license__,
    'keywords': ['webrtc', 'asr', 'llm', 'tts', 'voice', 'assistant', 'speech'],
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Multimedia :: Sound/Audio :: Speech',
        'Topic :: Communications :: Conferencing',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ]
}

def get_info():
    """获取包信息"""
    return PACKAGE_INFO.copy()

def create_server(host='localhost', port=8765):
    """快速创建WebRTC服务器实例"""
    return WebRTCServer(host=host, port=port)

def create_asr():
    """快速创建ASR模块实例"""
    return ASRModule()

def create_llm():
    """快速创建LLM模块实例"""
    return LLMModule()

def create_tts():
    """快速创建TTS模块实例"""
    return TTSModule()

def create_audio_processor(buffer_size=50):
    """快速创建音频处理器实例"""
    return AudioProcessor(buffer_size=buffer_size)
