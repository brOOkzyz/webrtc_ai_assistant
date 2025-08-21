# -*- coding: utf-8 -*-
"""
语音合成模块
"""

import logging
import requests
import base64
import json
from config import TTS_API_KEY, TTS_SECRET_KEY, API_TIMEOUTS

logger = logging.getLogger(__name__)

class TTSModule:
    """语音合成模块"""
    
    def __init__(self):
        self.api_key = TTS_API_KEY
        self.secret_key = TTS_SECRET_KEY
        self.token = None
        
    async def get_token(self):
        """获取百度TTS访问令牌"""
        if self.token:
            return self.token
            
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        
        try:
            response = requests.post(url, params=params, timeout=API_TIMEOUTS['TTS_TOKEN'])
            if response.status_code == 200:
                result = response.json()
                self.token = result.get("access_token")
                return self.token
            else:
                logger.error(f"获取TTS令牌失败: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"获取TTS令牌时出错: {e}")
            return None
    
    async def synthesize(self, text, voice_type="0", speed="5", pitch="5", volume="5"):
        """语音合成"""
        token = await self.get_token()
        if not token:
            return None
            
        url = f"https://tsn.baidu.com/text2audio?tok={token}"
        
        data = {
            "tex": text,
            "tok": token,
            "cuid": "webrtc_assistant",
            "ctp": "1",
            "lan": "zh",
            "spd": speed,
            "pit": pitch,
            "vol": volume,
            "per": voice_type,
            "aue": "6"
        }
        
        try:
            response = requests.post(url, data=data, timeout=API_TIMEOUTS['TTS_REQUEST'])
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                if 'audio' in content_type:
                    audio_data = response.content
                    logger.info(f"语音合成成功，文本长度: {len(text)}")
                    return audio_data
                else:
                    error_text = response.text
                    logger.error(f"TTS返回错误: {error_text}")
                    return None
            else:
                logger.error(f"TTS请求失败: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"语音合成时出错: {e}")
            return None
    
    async def get_available_voices(self):
        """获取可用语音列表"""
        voices = [
            {"id": "0", "name": "女声", "description": "标准女声"},
            {"id": "1", "name": "男声", "description": "标准男声"},
            {"id": "3", "name": "度逍遥", "description": "情感男声"},
            {"id": "4", "name": "度丫丫", "description": "情感女声"}
        ]
        return voices
