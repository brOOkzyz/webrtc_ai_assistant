# -*- coding: utf-8 -*-
"""
音频处理模块
"""

import logging
import numpy as np
import wave
import io
from collections import deque
from config import AUDIO_SAMPLE_RATE, AUDIO_CHANNELS, AUDIO_SAMPLE_WIDTH, AUDIO_BUFFER_SIZE

logger = logging.getLogger(__name__)

class AudioProcessor:
    """音频处理模块"""
    
    def __init__(self, buffer_size=50):
        self.buffer_size = buffer_size
        self.audio_buffer = deque(maxlen=buffer_size)
        self.sample_rate = AUDIO_SAMPLE_RATE
        self.channels = AUDIO_CHANNELS
        self.sample_width = AUDIO_SAMPLE_WIDTH
        
    async def process_audio(self, audio_data):
        """处理音频数据"""
        try:
            # 将音频数据添加到缓冲区
            self.audio_buffer.append(audio_data)
            
            # 检查是否有足够的音频数据进行处理
            if len(self.audio_buffer) < 3:
                return None
                
            # 合并音频数据
            combined_audio = self.combine_audio_chunks()
            
            # 音频预处理
            processed_audio = self.preprocess_audio(combined_audio)
            
            return processed_audio
            
        except Exception as e:
            logger.error(f"音频处理时出错: {e}")
            return None
    
    def combine_audio_chunks(self):
        """合并音频块"""
        if not self.audio_buffer:
            return b""
            
        combined = b""
        for chunk in self.audio_buffer:
            combined += chunk
            
        return combined
    
    def preprocess_audio(self, audio_data):
        """音频预处理"""
        try:
            # 转换为numpy数组
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # 音量归一化
            if len(audio_array) > 0:
                max_amplitude = np.max(np.abs(audio_array))
                if max_amplitude > 0:
                    normalized_audio = (audio_array / max_amplitude * 32767).astype(np.int16)
                else:
                    normalized_audio = audio_array
            else:
                normalized_audio = audio_array
            
            # 转换回字节
            return normalized_audio.tobytes()
            
        except Exception as e:
            logger.error(f"音频预处理时出错: {e}")
            return audio_data
    
    def detect_silence(self, audio_data, threshold=0.01):
        """检测静音"""
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            if len(audio_array) == 0:
                return True
                
            # 计算RMS值
            rms = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
            normalized_rms = rms / 32767.0
            
            return normalized_rms < threshold
            
        except Exception as e:
            logger.error(f"静音检测时出错: {e}")
            return False
    
    def detect_voice_activity(self, audio_data, threshold=0.012):
        """检测语音活动"""
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            if len(audio_array) == 0:
                return False
                
            # 计算音量
            volume = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
            normalized_volume = volume / 32767.0
            
            return normalized_volume > threshold
            
        except Exception as e:
            logger.error(f"语音活动检测时出错: {e}")
            return False
    
    def save_audio_to_wav(self, audio_data, filename):
        """保存音频为WAV文件"""
        try:
            with wave.open(filename, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(self.sample_width)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_data)
            logger.info(f"音频已保存到: {filename}")
            return True
        except Exception as e:
            logger.error(f"保存音频文件时出错: {e}")
            return False
    
    def clear_buffer(self):
        """清空音频缓冲区"""
        self.audio_buffer.clear()
        logger.info("音频缓冲区已清空")
