# -*- coding: utf-8 -*-
"""
工具函数模块
"""

import logging
import json
import time
import hashlib
import base64
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def generate_client_id() -> str:
    """生成客户端ID"""
    timestamp = str(int(time.time() * 1000))
    random_suffix = hashlib.md5(timestamp.encode()).hexdigest()[:8]
    return f"client_{timestamp}_{random_suffix}"

def validate_json_message(message: str) -> Optional[Dict[str, Any]]:
    """验证JSON消息格式"""
    try:
        data = json.loads(message)
        if not isinstance(data, dict):
            return None
        return data
    except json.JSONDecodeError:
        return None

def encode_audio_data(audio_data: bytes) -> str:
    """编码音频数据为base64字符串"""
    try:
        return base64.b64encode(audio_data).decode('utf-8')
    except Exception as e:
        logger.error(f"音频编码失败: {e}")
        return ""

def decode_audio_data(encoded_data: str) -> bytes:
    """解码base64音频数据"""
    try:
        return base64.b64decode(encoded_data)
    except Exception as e:
        logger.error(f"音频解码失败: {e}")
        return b""

def format_timestamp(timestamp: float) -> str:
    """格式化时间戳"""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))

def calculate_audio_duration(audio_data: bytes, sample_rate: int = 16000, channels: int = 1, sample_width: int = 2) -> float:
    """计算音频时长"""
    try:
        bytes_per_sample = channels * sample_width
        total_samples = len(audio_data) / bytes_per_sample
        duration = total_samples / sample_rate
        return round(duration, 3)
    except Exception as e:
        logger.error(f"计算音频时长失败: {e}")
        return 0.0

def create_response_message(msg_type: str, data: Dict[str, Any]) -> str:
    """创建响应消息"""
    response = {
        "type": msg_type,
        "timestamp": time.time(),
        "data": data
    }
    return json.dumps(response, ensure_ascii=False)

def log_performance_metrics(operation: str, start_time: float, success: bool = True):
    """记录性能指标"""
    duration = time.time() - start_time
    status = "成功" if success else "失败"
    logger.info(f"性能指标 - {operation}: {status}, 耗时: {duration:.3f}秒")

def sanitize_filename(filename: str) -> str:
    """清理文件名"""
    import re
    # 移除或替换不合法的字符
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 限制长度
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    return sanitized

def create_error_response(error_code: str, error_message: str) -> str:
    """创建错误响应"""
    response = {
        "type": "error",
        "error_code": error_code,
        "error_message": error_message,
        "timestamp": time.time()
    }
    return json.dumps(response, ensure_ascii=False)
