# -*- coding: utf-8 -*-
"""
语音识别模块
"""

import logging
import requests
import base64
import json
from config import ASR_API_KEY, ASR_SECRET_KEY, API_TIMEOUTS

logger = logging.getLogger(__name__)

class ASRModule:
    """语音识别模块"""
    
    def __init__(self):
        self.api_key = ASR_API_KEY
        self.secret_key = ASR_SECRET_KEY
        self.token = None
        
    async def get_token(self):
        """获取百度ASR访问令牌"""
        if self.token:
            return self.token
            
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        
        try:
            response = requests.post(url, params=params, timeout=API_TIMEOUTS['ASR_TOKEN'])
            if response.status_code == 200:
                result = response.json()
                self.token = result.get("access_token")
                return self.token
            else:
                logger.error(f"获取ASR令牌失败: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"获取ASR令牌时出错: {e}")
            return None
    
    async def recognize(self, audio_data):
        """语音识别"""
        token = await self.get_token()
        if not token:
            return None
            
        url = f"https://vop.baidu.com/server_api?cuid=webrtc_assistant&token={token}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "format": "pcm",
            "rate": 16000,
            "channel": 1,
            "cuid": "webrtc_assistant",
            "token": token,
            "speech": base64.b64encode(audio_data).decode('utf-8'),
            "len": len(audio_data)
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=API_TIMEOUTS['ASR_REQUEST'])
            if response.status_code == 200:
                result = response.json()
                if result.get("err_no") == 0:
                    text = result.get("result", [""])[0]
                    logger.info(f"语音识别成功: {text}")
                    return text
                else:
                    logger.error(f"语音识别失败: {result.get('err_msg')}")
                    return None
            else:
                logger.error(f"ASR请求失败: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"语音识别时出错: {e}")
            return None
