#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
提供通用的辅助函数和常量
"""

import logging
import json
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

def create_message(message_type: str, data: Dict[str, Any] = None) -> str:
    """创建标准格式的WebSocket消息"""
    message = {
        'type': message_type,
        'timestamp': time.time()
    }
    
    if data:
        message.update(data)
    
    return json.dumps(message, ensure_ascii=False)

def parse_message(message: str) -> Optional[Dict[str, Any]]:
    """解析WebSocket消息"""
    try:
        return json.loads(message)
    except json.JSONDecodeError as e:
        logger.error(f"❌ 消息解析失败: {e}")
        return None

def format_timestamp(timestamp: float) -> str:
    """格式化时间戳"""
    return time.strftime('%H:%M:%S', time.localtime(timestamp))

def log_performance(operation: str, start_time: float, success: bool = True):
    """记录性能日志"""
    duration = time.time() - start_time
    status = "✅" if success else "❌"
    logger.info(f"{status} {operation} 耗时: {duration:.3f}秒")

def validate_audio_data(audio_data: bytes, min_size: int = 1000) -> bool:
    """验证音频数据有效性"""
    if not audio_data:
        return False
    
    if len(audio_data) < min_size:
        return False
    
    return True

def get_memory_usage() -> Dict[str, Any]:
    """获取内存使用情况（简化版）"""
    import psutil
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        return {
            'rss': memory_info.rss / 1024 / 1024,  # MB
            'vms': memory_info.vms / 1024 / 1024,  # MB
            'percent': process.memory_percent()
        }
    except ImportError:
        return {'error': 'psutil not available'}

def cleanup_resources():
    """清理系统资源"""
    import gc
    gc.collect()
    logger.info("🧹 已执行垃圾回收")

# 常量定义
WEBSOCKET_MESSAGE_TYPES = {
    'CONNECTION_ESTABLISHED': 'connection_established',
    'AUDIO_DATA': 'audio_data',
    'ASR_RESULT': 'asr_result',
    'ASR_ERROR': 'asr_error',
    'LLM_RESPONSE': 'llm_response',
    'TTS_AUDIO': 'tts_audio',
    'INTERRUPT_TTS': 'interrupt_tts',
    'INTERRUPTION_CONFIRMED': 'interruption_confirmed',
    'ERROR': 'error'
}

AUDIO_CONFIG = {
    'SAMPLE_RATE': 16000,
    'CHANNELS': 1,
    'SAMPLE_WIDTH': 2,  # 16位
    'BUFFER_SIZE': 1024,
    'SILENCE_THRESHOLD': 1.0
}

API_TIMEOUTS = {
    'ASR_TOKEN': 5,
    'ASR_REQUEST': 8,
    'LLM_REQUEST': 15,
    'TTS_TOKEN': 5,
    'TTS_REQUEST': 10
}
