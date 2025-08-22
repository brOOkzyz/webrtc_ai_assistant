#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTS语音合成模块
集成百度TTS API，提供文字转语音功能

版本: 2.0.0
"""

import logging
import requests
import base64
import time
import wave
import io
from typing import Optional

# 配置日志
logger = logging.getLogger(__name__)

class TTSModule:
    """TTS语音合成模块类"""
    
    def __init__(self):
        """初始化TTS模块"""
        # 百度TTS配置信息
        self.API_KEY = "YOUR API KEY"
        self.SECRET_KEY = "YOUR SECRET KEY"
        self.APP_ID = "YOUR APP ID"
        
        # 访问令牌管理
        self.access_token = None
        self.token_expire_time = 0
        
        # TTS参数配置
        self.default_params = {
            'spd': '5',      # 语速：5-9，5为正常语速
            'pit': '5',      # 音调：5-9，5为正常音调
            'vol': '5',      # 音量：0-15，5为正常音量
            'per': '0',      # 发音人：0为女声，1为男声，3为情感合成-度逍遥，4为情感合成-度丫丫
            'aue': '6'       # 音频格式：3为mp3格式(默认)； 4为pcm-16k；5为pcm-8k；6为wav
        }
        
    def get_access_token(self) -> Optional[str]:
        """获取百度TTS访问令牌"""
        try:
            # 检查当前令牌是否仍然有效（提前5分钟过期）
            if self.access_token and time.time() < self.token_expire_time:
                logger.debug("✅ 使用现有TTS访问令牌")
                return self.access_token
                
            # 获取新的访问令牌
            logger.info("🔑 正在获取百度TTS访问令牌...")
            
            # 构建令牌请求URL
            token_url = (
                f"https://aip.baidubce.com/oauth/2.0/token?"
                f"grant_type=client_credentials&"
                f"client_id={self.API_KEY}&"
                f"client_secret={self.SECRET_KEY}"
            )
            
            # 发送令牌请求（优化超时时间）
            token_response = requests.get(token_url, timeout=5)
            
            # 检查响应状态
            if token_response.status_code != 200:
                logger.error(f"❌ 获取TTS访问令牌失败: HTTP {token_response.status_code}")
                return None
            
            # 解析响应数据
            token_data = token_response.json()
            if 'access_token' not in token_data:
                logger.error(f"❌ TTS访问令牌响应异常: {token_data}")
                return None
            
            # 更新令牌信息
            self.access_token = token_data['access_token']
            
            # 设置令牌过期时间（提前5分钟过期，避免边界情况）
            expires_in = token_data.get('expires_in', 2592000)  # 默认30天
            self.token_expire_time = time.time() + expires_in - 300
            
            logger.info("✅ 已成功获取TTS访问令牌")
            return self.access_token
            
        except requests.exceptions.Timeout:
            logger.error("❌ 获取TTS访问令牌超时")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 获取TTS访问令牌请求异常: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ 获取TTS访问令牌时发生未知错误: {e}")
            return None
    
    def synthesize_speech(self, text: str) -> Optional[bytes]:
        """执行TTS语音合成"""
        try:
            logger.info(f"🔊 开始TTS语音合成: {text[:50]}...")
            
            # 验证输入文本
            if not self._validate_input_text(text):
                return self.generate_beep_sound()
            
            # 获取访问令牌
            access_token = self.get_access_token()
            if not access_token:
                logger.error("❌ 无法获取TTS访问令牌")
                return self.generate_beep_sound()
            
            # 执行TTS合成
            return self._execute_tts_request(text, access_token)
            
        except Exception as e:
            logger.error(f"❌ TTS语音合成过程中发生未知错误: {e}")
            return self.generate_beep_sound()
    
    def _validate_input_text(self, text: str) -> bool:
        """验证输入文本有效性"""
        if not text or not text.strip():
            logger.warning("⚠️ 输入文本为空")
            return False
        
        # 检查文本长度（避免过长文本）
        if len(text) > 1000:
            logger.warning(f"⚠️ 输入文本过长: {len(text)} 字符，最大支持1000字符")
            return False
        
        logger.debug(f"✅ 输入文本验证通过: {len(text)} 字符")
        return True
    
    def _execute_tts_request(self, text: str, access_token: str) -> Optional[bytes]:
        """执行TTS API请求"""
        try:
            # 构建TTS API URL
            tts_url = f"https://tsn.baidu.com/text2audio?tok={access_token}"
            
            # 构建请求参数
            tts_params = self._build_tts_params(text, access_token)
            
            logger.info(f"📤 发送TTS合成请求: {len(text)} 字符")
            
            # 发送TTS请求
            tts_response = requests.get(tts_url, params=tts_params, timeout=10)
            
            # 处理响应
            return self._process_tts_response(tts_response)
            
        except requests.exceptions.Timeout:
            logger.error("❌ TTS API请求超时")
            return self.generate_beep_sound()
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ TTS API请求异常: {e}")
            return self.generate_beep_sound()
        except Exception as e:
            logger.error(f"❌ 执行TTS请求时发生未知错误: {e}")
            return self.generate_beep_sound()
    
    def _build_tts_params(self, text: str, access_token: str) -> dict:
        """构建TTS请求参数"""
        params = {
            'tex': text,                    # 要合成的文本
            'tok': access_token,            # 访问令牌
            'cuid': 'webrtc_client',        # 用户唯一标识
            'ctp': '1',                     # 客户端类型
            'lan': 'zh'                     # 语言：中文
        }
        
        # 添加默认参数
        params.update(self.default_params)
        
        return params
    
    def _process_tts_response(self, response: requests.Response) -> Optional[bytes]:
        """处理TTS API响应"""
        try:
            if response.status_code == 200:
                # 检查响应内容类型
                content_type = response.headers.get('Content-Type', '')
                
                # 检查是否为音频数据
                if self._is_audio_response(response.content, content_type):
                    audio_data = response.content
                    logger.info(f"✅ TTS合成成功: {len(audio_data)} 字节")
                    return audio_data
                else:
                    # 可能是错误响应
                    error_text = response.text
                    if 'error' in error_text.lower():
                        logger.error(f"❌ TTS API返回错误: {error_text}")
                    else:
                        logger.warning(f"⚠️ TTS响应格式异常: {content_type}")
                    return self.generate_beep_sound()
            else:
                logger.error(f"❌ TTS API请求失败: HTTP {response.status_code}")
                return self.generate_beep_sound()
                
        except Exception as e:
            logger.error(f"❌ 处理TTS响应失败: {e}")
            return self.generate_beep_sound()
    
    def _is_audio_response(self, content: bytes, content_type: str) -> bool:
        """检查响应是否为音频数据"""
        # 检查内容类型
        if 'audio' in content_type.lower():
            return True
        
        # 检查内容特征（WAV文件以RIFF开头）
        if content.startswith(b'RIFF'):
            return True
        
        # 检查内容长度（音频文件通常较大）
        if len(content) > 1000:
            return True
        
        return False
    
    def generate_beep_sound(self) -> bytes:
        """生成备用蜂鸣声"""
        try:
            logger.info("🔊 生成备用蜂鸣声")
            
            # 音频参数
            sample_rate = 16000      # 采样率：16kHz
            duration = 0.5           # 持续时间：0.5秒
            frequency = 800          # 频率：800Hz
            
            # 生成音频数据
            num_samples = int(sample_rate * duration)
            audio_data = []
            
            for i in range(num_samples):
                # 生成正弦波，添加淡入淡出效果
                fade_factor = (i / num_samples) * (1 - i / num_samples)
                sample = int(32767 * 0.3 * fade_factor)
                audio_data.append(sample)
            
            # 创建WAV文件
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)      # 单声道
                wav_file.setsampwidth(2)      # 16位
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(bytes(audio_data))
            
            wav_data = wav_buffer.getvalue()
            wav_buffer.close()
            
            logger.info("✅ 备用蜂鸣声生成完成")
            return wav_data
            
        except Exception as e:
            logger.error(f"❌ 生成备用音频失败: {e}")
            # 返回一个最小的WAV文件作为最后的备选
            return self._generate_minimal_wav()
    
    def _generate_minimal_wav(self) -> bytes:
        """生成最小的WAV文件"""
        try:
            # 创建一个最小的WAV文件（44字节）
            # 包含WAV头部和1个静音样本
            minimal_wav = (
                b'RIFF$\x00\x00\x00'      # RIFF头部
                b'WAVE'                    # WAVE标识
                b'fmt \x10\x00\x00\x00'   # 格式块
                b'\x01\x00'               # 音频格式：PCM
                b'\x01\x00'               # 声道数：1
                b'@\x1f\x00\x00'         # 采样率：8000Hz
                b'\x80>\x00\x00'          # 字节率
                b'\x02\x00'               # 块对齐
                b'\x10\x00'               # 位深度：16
                b'data\x00\x00\x00\x00'   # 数据块（空）
            )
            
            logger.info("✅ 最小WAV文件生成完成")
            return minimal_wav
            
        except Exception as e:
            logger.error(f"❌ 生成最小WAV文件失败: {e}")
            # 最后的备选：返回空数据
            return b""
    
    def update_tts_params(self, **kwargs):
        """更新TTS参数"""
        try:
            # 验证参数有效性
            valid_params = {
                'spd': lambda x: 0 <= int(x) <= 9,      # 语速：0-9
                'pit': lambda x: 0 <= int(x) <= 9,      # 音调：0-9
                'vol': lambda x: 0 <= int(x) <= 15,     # 音量：0-15
                'per': lambda x: 0 <= int(x) <= 4,      # 发音人：0-4
                'aue': lambda x: int(x) in [3, 4, 5, 6] # 音频格式
            }
            
            for param, value in kwargs.items():
                if param in valid_params and valid_params[param](value):
                    self.default_params[param] = str(value)
                    logger.info(f"🔄 TTS参数已更新: {param} = {value}")
                else:
                    logger.warning(f"⚠️ 无效的TTS参数: {param} = {value}")
                    
        except Exception as e:
            logger.error(f"❌ 更新TTS参数失败: {e}")
    
    def get_module_status(self) -> dict:
        """获取模块状态信息"""
        return {
            'module': 'TTS',
            'status': 'active',
            'has_token': self.access_token is not None,
            'token_expires_in': max(0, self.token_expire_time - time.time()) if self.token_expire_time else 0,
            'api_key_configured': bool(self.API_KEY and self.SECRET_KEY),
            'default_params': self.default_params.copy()
        }
    
    def reset_token(self):
        """重置访问令牌"""
        self.access_token = None
        self.token_expire_time = 0
        logger.info("🔄 TTS访问令牌已重置")
    
    def test_api_connection(self) -> bool:
        """测试TTS API连接"""
        try:
            # 获取访问令牌来测试连接
            token = self.get_access_token()
            if token:
                logger.info("✅ TTS API连接测试成功")
                return True
            else:
                logger.warning("⚠️ TTS API连接测试失败")
                return False
                
        except Exception as e:
            logger.error(f"❌ TTS API连接测试异常: {e}")
            return False
