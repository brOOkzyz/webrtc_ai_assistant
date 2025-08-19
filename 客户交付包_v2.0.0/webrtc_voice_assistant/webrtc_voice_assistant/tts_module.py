#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTS语音合成模块
集成百度TTS API，提供文字转语音功能
"""

import logging
import requests
import base64
import time
import wave
import io
from typing import Optional

logger = logging.getLogger(__name__)

class TTSModule:
    """TTS语音合成模块"""
    
    def __init__(self):
        # 百度TTS配置
        self.API_KEY = "OjBAo0bZXmeOE76weLUPtKkj"
        self.SECRET_KEY = "dBF1UBMdxXb3nz4gOJrBLOADkANrFNQ3"
        self.APP_ID = "119399339"
        self.access_token = None
        self.token_expire_time = 0
        
    def get_access_token(self) -> Optional[str]:
        """获取百度TTS访问令牌"""
        try:
            # 检查令牌是否过期
            if self.access_token and time.time() < self.token_expire_time:
                return self.access_token
                
            # 生成访问令牌
            token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.API_KEY}&client_secret={self.SECRET_KEY}"
            
            try:
                # 优化：减少超时时间，更快响应
                token_response = requests.get(token_url, timeout=5)  # 从10秒减少到5秒
                token_data = token_response.json()
                
                if 'access_token' not in token_data:
                    logger.error(f"❌ 获取TTS访问令牌失败: {token_data}")
                    return None
                
                self.access_token = token_data['access_token']
                # 设置令牌过期时间（提前5分钟过期）
                self.token_expire_time = time.time() + token_data.get('expires_in', 2592000) - 300
                
                logger.info("✅ 已获取TTS访问令牌")
                return self.access_token
                
            except Exception as e:
                logger.error(f"❌ 获取TTS访问令牌异常: {e}")
                return None
                
        except Exception as e:
            logger.error(f"❌ TTS访问令牌处理异常: {e}")
            return None
    
    def synthesize_speech(self, text: str) -> Optional[bytes]:
        """执行TTS语音合成"""
        try:
            logger.info(f"🔊 执行TTS合成: {text}")
            
            # 获取访问令牌
            access_token = self.get_access_token()
            if not access_token:
                logger.error("❌ 无法获取TTS访问令牌")
                return self.generate_beep_sound()
            
            # 调用TTS API
            tts_url = f"https://tsn.baidu.com/text2audio?tok={access_token}"
            
            # TTS参数
            tts_params = {
                'tex': text,
                'tok': access_token,
                'cuid': 'webrtc_client',
                'ctp': '1',
                'lan': 'zh',
                'spd': '5',      # 语速：5-9，5为正常语速
                'pit': '5',      # 音调：5-9，5为正常音调
                'vol': '5',      # 音量：0-15，5为正常音量
                'per': '0',      # 发音人：0为女声，1为男声，3为情感合成-度逍遥，4为情感合成-度丫丫
                'aue': '6'       # 音频格式：3为mp3格式(默认)； 4为pcm-16k；5为pcm-8k；6为wav
            }
            
            # 发送TTS请求
            try:
                # 优化：减少超时时间，更快响应
                tts_response = requests.get(tts_url, params=tts_params, timeout=10)
                
                if tts_response.status_code == 200:
                    # 检查响应内容类型
                    content_type = tts_response.headers.get('Content-Type', '')
                    
                    if 'audio' in content_type or tts_response.content.startswith(b'RIFF'):
                        # 成功获取音频数据
                        audio_data = tts_response.content
                        logger.info(f"✅ TTS合成成功: {len(audio_data)} 字节")
                        return audio_data
                    else:
                        # 可能是错误响应
                        error_text = tts_response.text
                        if 'error' in error_text.lower():
                            logger.error(f"❌ TTS API返回错误: {error_text}")
                            return self.generate_beep_sound()
                        else:
                            logger.warning(f"⚠️ TTS响应格式异常: {content_type}")
                            return self.generate_beep_sound()
                else:
                    logger.error(f"❌ TTS API请求失败: HTTP状态码={tts_response.status_code}")
                    return self.generate_beep_sound()
                    
            except requests.exceptions.Timeout:
                logger.error("❌ TTS API请求超时")
                return self.generate_beep_sound()
            except Exception as e:
                logger.error(f"❌ TTS API请求异常: {e}")
                return self.generate_beep_sound()
                
        except Exception as e:
            logger.error(f"❌ TTS合成失败: {e}")
            return self.generate_beep_sound()
    
    def generate_beep_sound(self) -> bytes:
        """生成备用蜂鸣声"""
        try:
            # 生成一个简单的WAV格式蜂鸣声
            sample_rate = 16000
            duration = 0.5  # 0.5秒
            frequency = 800  # 800Hz
            
            # 生成音频数据
            num_samples = int(sample_rate * duration)
            audio_data = []
            
            for i in range(num_samples):
                # 生成正弦波
                sample = int(32767 * 0.3 * (i / num_samples) * (1 - i / num_samples))  # 淡入淡出效果
                audio_data.append(sample)
            
            # 创建WAV文件
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # 单声道
                wav_file.setsampwidth(2)   # 16位
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(bytes(audio_data))
            
            wav_data = wav_buffer.getvalue()
            wav_buffer.close()
            
            logger.info("🔊 生成备用蜂鸣声")
            return wav_data
            
        except Exception as e:
            logger.error(f"❌ 生成备用音频失败: {e}")
            # 返回一个最小的WAV文件
            return b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00@\x1f\x00\x00\x80>\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
