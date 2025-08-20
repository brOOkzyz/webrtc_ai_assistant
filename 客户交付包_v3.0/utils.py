#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
提供通用的辅助函数和常量

版本: 2.0.0
"""

import logging
import json
import time
import hashlib
import base64
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta

# 配置日志
logger = logging.getLogger(__name__)

# =============================================================================
# WebSocket消息处理函数
# =============================================================================

def create_message(message_type: str, data: Dict[str, Any] = None) -> str:
            """创建标准格式的WebSocket消息"""
    try:
        message = {
            'type': message_type,
            'timestamp': time.time(),
            'message_id': generate_message_id()
        }
        
        if data:
            message.update(data)
        
        return json.dumps(message, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"❌ 创建消息失败: {e}")
        # 返回错误消息
        return json.dumps({
            'type': 'error',
            'timestamp': time.time(),
            'error': '消息创建失败',
            'details': str(e)
        }, ensure_ascii=False)

def parse_message(message: str) -> Optional[Dict[str, Any]]:
            """解析WebSocket消息"""
    try:
        parsed = json.loads(message)
        
        # 验证必需字段
        if 'type' not in parsed:
            logger.warning("⚠️ 消息缺少type字段")
            return None
        
        return parsed
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ 消息JSON解析失败: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ 消息解析失败: {e}")
        return None

def validate_message(message: Dict[str, Any]) -> bool:
            """验证消息格式的有效性"""
    try:
        # 检查必需字段
        required_fields = ['type', 'timestamp']
        for field in required_fields:
            if field not in message:
                logger.warning(f"⚠️ 消息缺少必需字段: {field}")
                return False
        
        # 检查字段类型
        if not isinstance(message['type'], str):
            logger.warning("⚠️ 消息type字段类型错误")
            return False
        
        if not isinstance(message['timestamp'], (int, float)):
            logger.warning("⚠️ 消息timestamp字段类型错误")
            return False
        
        # 检查时间戳合理性
        current_time = time.time()
        message_time = message['timestamp']
        if abs(current_time - message_time) > 3600:  # 1小时内的消息
            logger.warning(f"⚠️ 消息时间戳异常: {message_time}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 消息验证失败: {e}")
        return False

def generate_message_id() -> str:
            """生成唯一的消息ID"""
    try:
        # 使用时间戳和随机数生成ID
        timestamp = str(int(time.time() * 1000))
        random_part = str(hash(str(time.time()))[-6:])
        return f"msg_{timestamp}_{random_part}"
        
    except Exception as e:
        logger.error(f"❌ 生成消息ID失败: {e}")
        return f"msg_{int(time.time())}"

# =============================================================================
# 时间处理函数
# =============================================================================

def format_timestamp(timestamp: float) -> str:
            """格式化时间戳为可读格式"""
    try:
        return time.strftime('%H:%M:%S', time.localtime(timestamp))
        
    except Exception as e:
        logger.error(f"❌ 时间戳格式化失败: {e}")
        return "00:00:00"

def format_datetime(timestamp: float, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
            """格式化时间戳为指定格式的日期时间字符串"""
    try:
        return time.strftime(format_str, time.localtime(timestamp))
        
    except Exception as e:
        logger.error(f"❌ 日期时间格式化失败: {e}")
        return "1970-01-01 00:00:00"

def get_time_difference(timestamp1: float, timestamp2: float) -> str:
            """计算两个时间戳之间的时间差"""
    try:
        diff_seconds = abs(timestamp2 - timestamp1)
        
        if diff_seconds < 60:
            return f"{diff_seconds:.1f}秒"
        elif diff_seconds < 3600:
            minutes = diff_seconds / 60
            return f"{minutes:.1f}分钟"
        elif diff_seconds < 86400:
            hours = diff_seconds / 3600
            return f"{hours:.1f}小时"
        else:
            days = diff_seconds / 86400
            return f"{days:.1f}天"
            
    except Exception as e:
        logger.error(f"❌ 计算时间差失败: {e}")
        return "未知"

def is_timestamp_recent(timestamp: float, max_age_seconds: int = 300) -> bool:
            """检查时间戳是否在最近的时间内"""
    try:
        current_time = time.time()
        age = current_time - timestamp
        return 0 <= age <= max_age_seconds
        
    except Exception as e:
        logger.error(f"❌ 检查时间戳年龄失败: {e}")
        return False

# =============================================================================
# 性能监控函数
# =============================================================================

def log_performance(operation: str, start_time: float, success: bool = True, 
                   additional_info: Dict[str, Any] = None):
            """记录性能日志"""
    try:
        duration = time.time() - start_time
        status = "✅" if success else "❌"
        
        log_message = f"{status} {operation} 耗时: {duration:.3f}秒"
        
        if additional_info:
            info_str = ", ".join([f"{k}: {v}" for k, v in additional_info.items()])
            log_message += f" | {info_str}"
        
        logger.info(log_message)
        
        # 记录慢操作
        if duration > 1.0:  # 超过1秒的操作
            logger.warning(f"🐌 慢操作检测: {operation} 耗时 {duration:.3f}秒")
            
    except Exception as e:
        logger.error(f"❌ 记录性能日志失败: {e}")

def measure_performance(func):
            """性能测量装饰器"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            log_performance(func.__name__, start_time, True)
            return result
        except Exception as e:
            log_performance(func.__name__, start_time, False, {'error': str(e)})
            raise
    return wrapper

def get_performance_stats() -> Dict[str, Any]:
            """获取系统性能统计信息"""
    try:
        import psutil
        
        # CPU信息
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # 内存信息
        memory = psutil.virtual_memory()
        memory_info = {
            'total': memory.total / (1024**3),  # GB
            'available': memory.available / (1024**3),  # GB
            'percent': memory.percent
        }
        
        # 磁盘信息
        disk = psutil.disk_usage('/')
        disk_info = {
            'total': disk.total / (1024**3),  # GB
            'used': disk.used / (1024**3),    # GB
            'free': disk.free / (1024**3),    # GB
            'percent': (disk.used / disk.total) * 100
        }
        
        return {
            'cpu': {
                'percent': cpu_percent,
                'count': cpu_count
            },
            'memory': memory_info,
            'disk': disk_info,
            'timestamp': time.time()
        }
        
    except ImportError:
        logger.warning("⚠️ psutil模块未安装，无法获取系统性能信息")
        return {'error': 'psutil not available'}
    except Exception as e:
        logger.error(f"❌ 获取性能统计失败: {e}")
        return {'error': str(e)}

# =============================================================================
# 音频数据处理函数
# =============================================================================

def validate_audio_data(audio_data: bytes, min_size: int = 1000) -> bool:
            """验证音频数据有效性"""
    try:
        if not audio_data:
            logger.warning("⚠️ 音频数据为空")
            return False
        
        if len(audio_data) < min_size:
            logger.warning(f"⚠️ 音频数据过小: {len(audio_data)} < {min_size}")
            return False
        
        # 检查是否为有效的音频数据（简单检查）
        if len(audio_data) > 100 * 1024 * 1024:  # 100MB
            logger.warning(f"⚠️ 音频数据过大: {len(audio_data)} 字节")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 音频数据验证失败: {e}")
        return False

def encode_audio_to_base64(audio_data: bytes) -> str:
            """将音频数据编码为base64字符串"""
    try:
        return base64.b64encode(audio_data).decode('utf-8')
        
    except Exception as e:
        logger.error(f"❌ 音频base64编码失败: {e}")
        return ""

def decode_audio_from_base64(base64_string: str) -> Optional[bytes]:
            """将base64字符串解码为音频数据"""
    try:
        return base64.b64decode(base64_string)
        
    except Exception as e:
        logger.error(f"❌ 音频base64解码失败: {e}")
        return None

def calculate_audio_hash(audio_data: bytes) -> str:
            """计算音频数据的哈希值"""
    try:
        return hashlib.md5(audio_data).hexdigest()
        
    except Exception as e:
        logger.error(f"❌ 计算音频哈希失败: {e}")
        return ""

# =============================================================================
# 系统资源管理函数
# =============================================================================

def get_memory_usage() -> Dict[str, Any]:
            """获取内存使用情况"""
    try:
        import psutil
        
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,      # 物理内存使用（MB）
            'vms_mb': memory_info.vms / 1024 / 1024,      # 虚拟内存使用（MB）
            'percent': process.memory_percent(),            # 内存使用百分比
            'available_mb': psutil.virtual_memory().available / 1024 / 1024  # 系统可用内存（MB）
        }
        
    except ImportError:
        logger.warning("⚠️ psutil模块未安装，无法获取内存信息")
        return {'error': 'psutil not available'}
    except Exception as e:
        logger.error(f"❌ 获取内存使用信息失败: {e}")
        return {'error': str(e)}

def cleanup_resources():
            """清理系统资源"""
    try:
        import gc
        
        # 执行垃圾回收
        collected = gc.collect()
        
        # 清理内存
        import sys
        if hasattr(sys, 'exc_clear'):
            sys.exc_clear()
        
        logger.info(f"🧹 已执行资源清理，回收对象: {collected}")
        
    except Exception as e:
        logger.error(f"❌ 资源清理失败: {e}")

def check_disk_space(path: str = "/", min_free_gb: float = 1.0) -> bool:
            """检查磁盘空间是否充足"""
    try:
        import psutil
        
        disk_usage = psutil.disk_usage(path)
        free_gb = disk_usage.free / (1024**3)
        
        if free_gb < min_free_gb:
            logger.warning(f"⚠️ 磁盘空间不足: {path} 可用 {free_gb:.2f}GB < {min_free_gb}GB")
            return False
        
        logger.debug(f"✅ 磁盘空间充足: {path} 可用 {free_gb:.2f}GB")
        return True
        
    except ImportError:
        logger.warning("⚠️ psutil模块未安装，无法检查磁盘空间")
        return True
    except Exception as e:
        logger.error(f"❌ 检查磁盘空间失败: {e}")
        return True

# =============================================================================
# 常量定义
# =============================================================================

# WebSocket消息类型常量
WEBSOCKET_MESSAGE_TYPES = {
    'CONNECTION_ESTABLISHED': 'connection_established',
    'AUDIO_DATA': 'audio_data',
    'ASR_RESULT': 'asr_result',
    'ASR_ERROR': 'asr_error',
    'LLM_RESPONSE': 'llm_response',
    'TTS_AUDIO': 'tts_audio',
    'INTERRUPT_TTS': 'interrupt_tts',
    'INTERRUPTION_CONFIRMED': 'interruption_confirmed',
    'ERROR': 'error',
    'PING': 'ping',
    'PONG': 'pong'
}

# 音频配置常量
AUDIO_CONFIG = {
    'SAMPLE_RATE': 16000,          # 采样率：16kHz
    'CHANNELS': 1,                 # 声道数：单声道
    'SAMPLE_WIDTH': 2,             # 采样位宽：16位
    'BUFFER_SIZE': 1024,           # 缓冲区大小
    'SILENCE_THRESHOLD': 1.0,      # 静音阈值（秒）
    'MAX_AUDIO_SIZE': 100 * 1024 * 1024  # 最大音频大小：100MB
}

# API超时常量
API_TIMEOUTS = {
    'ASR_TOKEN': 5,        # ASR令牌获取超时（秒）
    'ASR_REQUEST': 8,      # ASR请求超时（秒）
    'LLM_REQUEST': 15,     # LLM请求超时（秒）
    'TTS_TOKEN': 5,        # TTS令牌获取超时（秒）
    'TTS_REQUEST': 10,     # TTS请求超时（秒）
    'WEBSOCKET': 30        # WebSocket操作超时（秒）
}

# 错误代码常量
ERROR_CODES = {
    'SUCCESS': 0,
    'INVALID_INPUT': 1001,
    'API_ERROR': 2001,
    'NETWORK_ERROR': 3001,
    'TIMEOUT_ERROR': 4001,
    'INTERNAL_ERROR': 5001
}

# =============================================================================
# 工具函数测试
# =============================================================================

def test_utils():
            """测试工具函数的基本功能"""
    try:
        print("🧪 开始测试工具函数...")
        
        # 测试消息创建
        test_message = create_message('test', {'data': 'test_value'})
        print(f"✅ 消息创建测试: {test_message}")
        
        # 测试消息解析
        parsed = parse_message(test_message)
        print(f"✅ 消息解析测试: {parsed}")
        
        # 测试时间格式化
        current_time = time.time()
        formatted = format_timestamp(current_time)
        print(f"✅ 时间格式化测试: {formatted}")
        
        # 测试性能统计
        stats = get_performance_stats()
        print(f"✅ 性能统计测试: {stats}")
        
        print("🎉 工具函数测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 工具函数测试失败: {e}")
        return False

if __name__ == "__main__":
    # 运行工具函数测试
    test_utils()
