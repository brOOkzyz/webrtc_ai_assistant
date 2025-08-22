#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM对话模块
集成SiliconFlow API，提供智能对话功能
"""

import logging
import requests
from typing import Optional
from .config import BASE_URL, DEFAULT_MODEL

logger = logging.getLogger(__name__)

class LLMModule:
    """LLM对话模块"""
    
    def __init__(self):
        # 使用用户提供的LLM API Key
        self.API_KEY = "sk-vjntadlyyvfewqskgazdzosowrqmaqcpmwhcnlknauqejssi"
        self.base_url = BASE_URL
        self.model = DEFAULT_MODEL
        
        # 对话历史管理
        self.conversation_history = {}
        
    def ask_question(self, question: str, client_id: str = None) -> str:
        """向LLM提问"""
        try:
            url = f"{self.base_url}/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.API_KEY}",
                "Content-Type": "application/json"
            }
            
            # 构建对话消息
            messages = [
                {"role": "system", "content": "你是一个高效的语音助手。请用最简洁的语言回答问题，控制在50字以内，直接给出核心答案，不要解释过程。"},
                {"role": "user", "content": question}
            ]
            
            # 如果有对话历史，添加最近的对话
            if client_id and client_id in self.conversation_history:
                # 只保留最近的3轮对话，避免上下文过长
                recent_history = self.conversation_history[client_id][-6:]  # 3轮对话 = 6条消息
                messages = [messages[0]] + recent_history + [messages[1]]
            
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.5,  # 降低随机性，提高响应一致性
                "max_tokens": 100,   # 减少最大token数，更快响应
                "stream": False      # 非流式响应，简化处理
            }
            
            # 优化：减少超时时间，更快响应
            response = requests.post(url, headers=headers, json=data, timeout=15)  # 从30秒减少到15秒
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                answer = result['choices'][0]['message']['content']
                
                # 保存对话历史
                if client_id:
                    if client_id not in self.conversation_history:
                        self.conversation_history[client_id] = []
                    
                    # 添加用户问题和回答
                    self.conversation_history[client_id].extend([
                        {"role": "user", "content": question},
                        {"role": "assistant", "content": answer}
                    ])
                    
                    # 限制对话历史长度，避免内存占用过大
                    if len(self.conversation_history[client_id]) > 20:  # 保留最近10轮对话
                        self.conversation_history[client_id] = self.conversation_history[client_id][-20:]
                
                return answer
            else:
                return "抱歉，我没有理解您的问题。"
                
        except Exception as e:
            logger.error(f"❌ LLM请求失败: {e}")
            return "抱歉，服务暂时不可用。"
    
    def clear_conversation_history(self, client_id: str):
        """清除指定客户端的对话历史"""
        if client_id in self.conversation_history:
            del self.conversation_history[client_id]
            logger.info(f"🗑️ 已清除客户端 {client_id} 的对话历史")
    
    def get_conversation_summary(self, client_id: str) -> str:
        """获取对话摘要"""
        if client_id in self.conversation_history:
            history = self.conversation_history[client_id]
            return f"对话历史: {len(history)//2} 轮对话"
        return "无对话历史"
