#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频处理模块
管理音频缓冲、合并和处理逻辑
"""

import logging
import time
from collections import deque
from typing import List, Optional

logger = logging.getLogger(__name__)

class AudioProcessor:
    """音频处理模块"""
    
    def __init__(self, buffer_size: int = 50):
        self.buffer_size = buffer_size
        self.audio_buffers = {}  # 存储每个客户端的音频缓冲区
        self.last_audio_time = {}  # 最后音频时间
        self.asr_tasks = {}      # ASR任务
        
    def add_audio_data(self, client_id: str, audio_data: bytes) -> bool:
        """添加音频数据到缓冲区"""
        try:
            if client_id not in self.audio_buffers:
                self.audio_buffers[client_id] = deque(maxlen=self.buffer_size)
                self.last_audio_time[client_id] = time.time()
            
            # 添加音频数据
            self.audio_buffers[client_id].append(audio_data)
            self.last_audio_time[client_id] = time.time()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 添加音频数据失败: {e}")
            return False
    
    def get_audio_data(self, client_id: str) -> Optional[bytes]:
        """获取并清空音频缓冲区数据"""
        try:
            if client_id not in self.audio_buffers:
                return None
            
            audio_chunks = list(self.audio_buffers[client_id])
            self.audio_buffers[client_id].clear()
            
            if not audio_chunks:
                return None
            
            # 合并音频数据
            combined_audio = b''.join(audio_chunks)
            logger.info(f"📊 处理音频: {len(combined_audio)} 字节")
            
            return combined_audio
            
        except Exception as e:
            logger.error(f"❌ 获取音频数据失败: {e}")
            return None
    
    def has_sufficient_audio(self, client_id: str, threshold: int = 3) -> bool:
        """检查是否有足够的音频数据进行处理"""
        if client_id in self.audio_buffers:
            return len(self.audio_buffers[client_id]) >= threshold
        return False
    
    def get_audio_buffer_size(self, client_id: str) -> int:
        """获取音频缓冲区大小"""
        if client_id in self.audio_buffers:
            return len(self.audio_buffers[client_id])
        return 0
    
    def is_silent(self, client_id: str, silence_threshold: float = 1.0) -> bool:
        """检查是否已经静音足够长时间"""
        if client_id in self.last_audio_time:
            time_since_last_audio = time.time() - self.last_audio_time[client_id]
            return time_since_last_audio >= silence_threshold
        return True
    
    def clear_buffer(self, client_id: str):
        """清空指定客户端的音频缓冲区"""
        if client_id in self.audio_buffers:
            self.audio_buffers[client_id].clear()
            logger.info(f"🗑️ 已清空客户端 {client_id} 的音频缓冲区")
    
    def cleanup_client(self, client_id: str):
        """清理指定客户端的资源"""
        if client_id in self.audio_buffers:
            del self.audio_buffers[client_id]
        if client_id in self.last_audio_time:
            del self.last_audio_time[client_id]
        if client_id in self.asr_tasks:
            del self.asr_tasks[client_id]
        
        logger.info(f"🧹 已清理客户端 {client_id} 的音频处理资源")
    
    def get_client_stats(self, client_id: str) -> dict:
        """获取客户端音频处理统计信息"""
        stats = {
            'buffer_size': self.get_audio_buffer_size(client_id),
            'is_silent': self.is_silent(client_id),
            'last_audio_time': self.last_audio_time.get(client_id, 0)
        }
        return stats
