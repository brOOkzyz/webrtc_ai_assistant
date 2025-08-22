#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频处理模块
管理音频缓冲、合并和处理逻辑

版本: 2.0.0
"""

import logging
import time
from collections import deque
from typing import List, Optional, Dict, Any

# 配置日志
logger = logging.getLogger(__name__)

class AudioProcessor:
    """音频处理模块类"""
    
    def __init__(self, buffer_size: int = 50):
        """初始化音频处理模块"""
        self.buffer_size = buffer_size
        
        # 客户端音频数据管理
        self.audio_buffers: Dict[str, deque] = {}
        self.last_audio_time: Dict[str, float] = {}
        self.asr_tasks: Dict[str, Any] = {}
        
        # 音频处理统计
        self.processing_stats: Dict[str, Dict[str, Any]] = {}
        
    def add_audio_data(self, client_id: str, audio_data: bytes) -> bool:
        """添加音频数据到缓冲区"""
        try:
            # 验证输入参数
            if not client_id or not audio_data:
                logger.warning("⚠️ 无效的输入参数")
                return False
            
            # 初始化客户端缓冲区（如果不存在）
            if client_id not in self.audio_buffers:
                self.audio_buffers[client_id] = deque(maxlen=self.buffer_size)
                self.last_audio_time[client_id] = time.time()
                self.processing_stats[client_id] = {
                    'total_audio_chunks': 0,
                    'total_audio_bytes': 0,
                    'first_audio_time': time.time(),
                    'last_audio_time': time.time()
                }
                logger.debug(f"🔧 为客户端 {client_id} 初始化音频缓冲区")
            
            # 添加音频数据到缓冲区
            self.audio_buffers[client_id].append(audio_data)
            self.last_audio_time[client_id] = time.time()
            
            # 更新统计信息
            self.processing_stats[client_id]['total_audio_chunks'] += 1
            self.processing_stats[client_id]['total_audio_bytes'] += len(audio_data)
            self.processing_stats[client_id]['last_audio_time'] = time.time()
            
            logger.debug(f"🎵 客户端 {client_id} 音频数据已添加: {len(audio_data)} 字节")
            return True
            
        except Exception as e:
            logger.error(f"❌ 添加音频数据失败: {e}")
            return False
    
    def get_audio_data(self, client_id: str) -> Optional[bytes]:
        """获取并清空音频缓冲区数据"""
        try:
            if client_id not in self.audio_buffers:
                logger.warning(f"⚠️ 客户端 {client_id} 的音频缓冲区不存在")
                return None
            
            # 获取所有音频数据
            audio_chunks = list(self.audio_buffers[client_id])
            
            # 清空缓冲区
            self.audio_buffers[client_id].clear()
            
            if not audio_chunks:
                logger.debug(f"📝 客户端 {client_id} 的音频缓冲区为空")
                return None
            
            # 合并音频数据
            combined_audio = b''.join(audio_chunks)
            
            # 更新统计信息
            if client_id in self.processing_stats:
                self.processing_stats[client_id]['processed_chunks'] = len(audio_chunks)
                self.processing_stats[client_id]['processed_bytes'] = len(combined_audio)
            
            logger.info(f"📊 处理音频数据: 客户端 {client_id}, {len(audio_chunks)} 块, {len(combined_audio)} 字节")
            return combined_audio
            
        except Exception as e:
            logger.error(f"❌ 获取音频数据失败: {e}")
            return None
    
    def has_sufficient_audio(self, client_id: str, threshold: int = 1) -> bool:
        """检查是否有足够的音频数据进行处理"""
        try:
            if client_id in self.audio_buffers:
                buffer_size = len(self.audio_buffers[client_id])
                
                # 计算总音频数据大小（字节）
                total_bytes = sum(len(chunk) for chunk in self.audio_buffers[client_id])
                
                # 使用配置文件中的参数
                from config import ASR_PROCESSING_CONFIG
                min_bytes = ASR_PROCESSING_CONFIG['MIN_AUDIO_BYTES']
                
                # 只要有音频数据就可以处理，或者音频数据总大小超过配置的字节数
                has_sufficient = buffer_size >= threshold or total_bytes >= min_bytes
                
                if has_sufficient:
                    logger.debug(f"✅ 客户端 {client_id} 音频数据充足: {buffer_size}块/{total_bytes}字节")
                else:
                    logger.debug(f"⏳ 客户端 {client_id} 音频数据不足: {buffer_size}块/{total_bytes}字节")
                
                return has_sufficient
            else:
                logger.debug(f"📝 客户端 {client_id} 没有音频缓冲区")
                return False
                
        except Exception as e:
            logger.error(f"❌ 检查音频数据充足性失败: {e}")
            return False
    
    def get_audio_buffer_size(self, client_id: str) -> int:
        """获取音频缓冲区大小"""
        try:
            if client_id in self.audio_buffers:
                return len(self.audio_buffers[client_id])
            else:
                return 0
                
        except Exception as e:
            logger.error(f"❌ 获取音频缓冲区大小失败: {e}")
            return 0
    
    def is_silent(self, client_id: str, silence_threshold: float = 1.0) -> bool:
        """检查是否已经静音足够长时间"""
        try:
            if client_id in self.last_audio_time:
                time_since_last_audio = time.time() - self.last_audio_time[client_id]
                is_silent = time_since_last_audio >= silence_threshold
                
                if is_silent:
                    logger.debug(f"🔇 客户端 {client_id} 已静音 {time_since_last_audio:.1f} 秒")
                else:
                    logger.debug(f"🎤 客户端 {client_id} 最后音频 {time_since_last_audio:.1f} 秒前")
                
                return is_silent
            else:
                logger.debug(f"📝 客户端 {client_id} 没有音频时间记录")
                return True
                
        except Exception as e:
            logger.error(f"❌ 检查静音状态失败: {e}")
            return True
    
    def clear_buffer(self, client_id: str):
        """清空指定客户端的音频缓冲区"""
        try:
            if client_id in self.audio_buffers:
                buffer_size = len(self.audio_buffers[client_id])
                self.audio_buffers[client_id].clear()
                
                # 重置最后音频时间
                if client_id in self.last_audio_time:
                    self.last_audio_time[client_id] = 0
                
                logger.info(f"🗑️ 已清空客户端 {client_id} 的音频缓冲区 ({buffer_size} 块)")
            else:
                logger.debug(f"📝 客户端 {client_id} 没有音频缓冲区需要清空")
                
        except Exception as e:
            logger.error(f"❌ 清空音频缓冲区失败: {e}")
    
    def cleanup_client(self, client_id: str):
        """清理指定客户端的资源"""
        try:
            # 清理音频缓冲区
            if client_id in self.audio_buffers:
                buffer_size = len(self.audio_buffers[client_id])
                del self.audio_buffers[client_id]
                logger.debug(f"🗑️ 已清理客户端 {client_id} 的音频缓冲区 ({buffer_size} 块)")
            
            # 清理时间记录
            if client_id in self.last_audio_time:
                del self.last_audio_time[client_id]
            
            # 清理ASR任务
            if client_id in self.asr_tasks:
                del self.asr_tasks[client_id]
            
            # 清理统计信息
            if client_id in self.processing_stats:
                del self.processing_stats[client_id]
            
            logger.info(f"🧹 已清理客户端 {client_id} 的所有音频处理资源")
            
        except Exception as e:
            logger.error(f"❌ 清理客户端资源失败: {e}")
    
    def get_client_stats(self, client_id: str) -> Dict[str, Any]:
        """获取客户端音频处理统计信息"""
        try:
            stats = {
                'buffer_size': self.get_audio_buffer_size(client_id),
                'is_silent': self.is_silent(client_id),
                'last_audio_time': self.last_audio_time.get(client_id, 0)
            }
            
            # 添加详细统计信息
            if client_id in self.processing_stats:
                stats.update(self.processing_stats[client_id])
                
                # 计算处理速率
                if stats['first_audio_time'] > 0:
                    duration = time.time() - stats['first_audio_time']
                    if duration > 0:
                        stats['audio_rate_chunks_per_sec'] = stats['total_audio_chunks'] / duration
                        stats['audio_rate_bytes_per_sec'] = stats['total_audio_bytes'] / duration
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ 获取客户端统计信息失败: {e}")
            return {'error': str(e)}
    
    def get_all_clients_summary(self) -> Dict[str, Any]:
        """获取所有客户端的音频处理摘要"""
        try:
            summary = {
                'total_clients': len(self.audio_buffers),
                'active_clients': 0,
                'total_audio_chunks': 0,
                'total_audio_bytes': 0,
                'clients_info': {}
            }
            
            for client_id in self.audio_buffers:
                client_stats = self.get_client_stats(client_id)
                summary['clients_info'][client_id] = client_stats
                
                # 统计总量
                summary['total_audio_chunks'] += client_stats.get('total_audio_chunks', 0)
                summary['total_audio_bytes'] += client_stats.get('total_audio_bytes', 0)
                
                # 检查活跃状态
                if not client_stats.get('is_silent', True):
                    summary['active_clients'] += 1
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ 获取所有客户端摘要失败: {e}")
            return {'error': str(e)}
    
    def get_module_status(self) -> Dict[str, Any]:
        """获取模块状态信息"""
        try:
            return {
                'module': 'AudioProcessor',
                'status': 'active',
                'buffer_size': self.buffer_size,
                'total_clients': len(self.audio_buffers),
                'active_clients': len([c for c in self.audio_buffers if not self.is_silent(c)]),
                'total_audio_chunks': sum(len(buf) for buf in self.audio_buffers.values())
            }
            
        except Exception as e:
            logger.error(f"❌ 获取模块状态失败: {e}")
            return {'error': str(e)}
    
    def reset_client_stats(self, client_id: str):
        """重置指定客户端的统计信息"""
        try:
            if client_id in self.processing_stats:
                self.processing_stats[client_id] = {
                    'total_audio_chunks': 0,
                    'total_audio_bytes': 0,
                    'first_audio_time': time.time(),
                    'last_audio_time': time.time()
                }
                logger.info(f"🔄 已重置客户端 {client_id} 的统计信息")
            else:
                logger.debug(f"📝 客户端 {client_id} 没有统计信息需要重置")
                
        except Exception as e:
            logger.error(f"❌ 重置客户端统计信息失败: {e}")
    
    def get_audio_quality_metrics(self, client_id: str) -> Dict[str, Any]:
        """获取音频质量指标"""
        try:
            if client_id not in self.processing_stats:
                return {'error': '客户端不存在'}
            
            stats = self.processing_stats[client_id]
            
            # 计算音频质量指标
            metrics = {
                'total_chunks': stats.get('total_audio_chunks', 0),
                'total_bytes': stats.get('total_audio_bytes', 0),
                'average_chunk_size': 0,
                'processing_efficiency': 0
            }
            
            # 计算平均块大小
            if metrics['total_chunks'] > 0:
                metrics['average_chunk_size'] = metrics['total_bytes'] / metrics['total_chunks']
            
            # 计算处理效率（基于时间）
            if stats.get('first_audio_time', 0) > 0:
                duration = time.time() - stats['first_audio_time']
                if duration > 0:
                    metrics['processing_efficiency'] = metrics['total_bytes'] / duration
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ 获取音频质量指标失败: {e}")
            return {'error': str(e)}
