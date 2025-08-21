# -*- coding: utf-8 -*-
"""
智能对话模块
"""

import logging
import requests
import json
from config import API_KEY, BASE_URL, DEFAULT_MODEL, TEMPERATURE, MAX_TOKENS, API_TIMEOUTS

logger = logging.getLogger(__name__)

class LLMModule:
    """智能对话模块"""
    
    def __init__(self):
        self.api_key = API_KEY
        self.base_url = BASE_URL
        self.model = DEFAULT_MODEL
        self.temperature = TEMPERATURE
        self.max_tokens = MAX_TOKENS
        
    async def chat(self, message, conversation_history=None):
        """与LLM对话"""
        if not self.api_key or self.api_key == "your-api-key":
            logger.warning("API密钥未配置")
            return "抱歉，系统未配置API密钥，无法提供智能对话服务。"
            
        url = f"{self.base_url}/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({
            "role": "user",
            "content": message
        })
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=API_TIMEOUTS['LLM_REQUEST'])
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                logger.info(f"LLM回复生成成功")
                return content
            else:
                logger.error(f"LLM请求失败: {response.status_code} - {response.text}")
                return "抱歉，生成回复时出现错误，请稍后重试。"
        except Exception as e:
            logger.error(f"LLM对话时出错: {e}")
            return "抱歉，系统暂时无法响应，请稍后重试。"
    
    async def get_available_models(self):
        """获取可用模型列表"""
        if not self.api_key or self.api_key == "your-api-key":
            return []
            
        url = f"{self.base_url}/v1/models"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=API_TIMEOUTS['LLM_REQUEST'])
            if response.status_code == 200:
                result = response.json()
                models = [model["id"] for model in result.get("data", [])]
                return models
            else:
                logger.error(f"获取模型列表失败: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"获取模型列表时出错: {e}")
            return []
