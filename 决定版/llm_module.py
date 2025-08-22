#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM对话模块
集成SiliconFlow API，提供智能对话功能

版本: 2.0.0
"""

import logging
import requests
from typing import Optional, List, Dict, Any
from config import BASE_URL, DEFAULT_MODEL

# 配置日志
logger = logging.getLogger(__name__)

class LLMModule:
    """LLM对话模块类"""
    
    def __init__(self):
        """初始化LLM模块"""
        # API配置
        self.API_KEY = "YOUR API KEY"
        self.base_url = BASE_URL
        self.model = DEFAULT_MODEL
        
        # 对话历史管理
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}
        
        # 系统提示词配置
        self.system_prompt = (
            "你是一个高效的语音助手。请用最简洁的语言回答问题，"
            "控制在50字以内，直接给出核心答案，不要解释过程。"
        )
        
    def ask_question(self, question: str, client_id: str = None) -> str:
        """向LLM提问并获取回复"""
        try:
            logger.info(f"🤖 处理用户问题: {question[:50]}...")
            
            # 构建API请求URL
            url = f"{self.base_url}/v1/chat/completions"
            
            # 设置请求头
            headers = {
                "Authorization": f"Bearer {self.API_KEY}",
                "Content-Type": "application/json"
            }
            
            # 构建对话消息
            messages = self._build_conversation_messages(question, client_id)
            
            # 构建请求数据
            request_data = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.5,      # 降低随机性，提高响应一致性
                "max_tokens": 100,       # 减少最大token数，更快响应
                "stream": False          # 非流式响应，简化处理
            }
            
            logger.debug(f"📤 发送LLM请求: {len(messages)} 条消息")
            
            # 发送请求到LLM API
            response = requests.post(url, headers=headers, json=request_data, timeout=15)
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            ai_reply = self._extract_ai_reply(result)
            
            if ai_reply:
                # 保存对话历史
                if client_id:
                    self._save_conversation_history(client_id, question, ai_reply)
                
                logger.info(f"✅ 回复生成成功: {ai_reply[:50]}...")
                return ai_reply
            else:
                logger.warning("⚠️ LLM未返回有效回复")
                return "抱歉，我没有理解您的问题。"
                
        except requests.exceptions.Timeout:
            logger.error("❌ LLM API请求超时")
            return "抱歉，服务响应超时，请稍后重试。"
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ LLM API请求失败: {e}")
            return "抱歉，服务暂时不可用，请检查网络连接。"
        except Exception as e:
            logger.error(f"❌ LLM处理过程中发生未知错误: {e}")
            return "抱歉，服务出现异常，请稍后重试。"
    
    def _build_conversation_messages(self, question: str, client_id: str = None) -> List[Dict[str, str]]:
        """构建对话消息列表"""
        # 基础消息结构
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": question}
        ]
        
        # 如果有对话历史，添加最近的对话
        if client_id and client_id in self.conversation_history:
            # 只保留最近的3轮对话，避免上下文过长
            recent_history = self.conversation_history[client_id][-6:]  # 3轮对话 = 6条消息
            messages = [messages[0]] + recent_history + [messages[1]]
            
            logger.debug(f"📚 添加对话历史: {len(recent_history)} 条消息")
        
        return messages
    
    def _extract_ai_reply(self, api_response: Dict[str, Any]) -> Optional[str]:
        """从API响应中提取回复"""
        try:
            if 'choices' in api_response and len(api_response['choices']) > 0:
                choice = api_response['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    return choice['message']['content'].strip()
            
            logger.warning("⚠️ API响应格式异常，无法提取回复")
            return None
            
        except Exception as e:
            logger.error(f"❌ 提取回复失败: {e}")
            return None
    
    def _save_conversation_history(self, client_id: str, question: str, answer: str):
        """保存对话历史"""
        try:
            # 确保客户端有对话历史记录
            if client_id not in self.conversation_history:
                self.conversation_history[client_id] = []
            
            # 添加用户问题和回答
            self.conversation_history[client_id].extend([
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer}
            ])
            
            # 限制对话历史长度，避免内存占用过大
            max_history = 20  # 保留最近10轮对话
            if len(self.conversation_history[client_id]) > max_history:
                self.conversation_history[client_id] = self.conversation_history[client_id][-max_history:]
                logger.debug(f"📚 对话历史已截断至 {max_history} 条")
            
            logger.debug(f"💾 已保存对话历史: 客户端 {client_id}, 总条数: {len(self.conversation_history[client_id])}")
            
        except Exception as e:
            logger.error(f"❌ 保存对话历史失败: {e}")
    
    def clear_conversation_history(self, client_id: str):
        """清除指定客户端的对话历史"""
        try:
            if client_id in self.conversation_history:
                history_count = len(self.conversation_history[client_id])
                del self.conversation_history[client_id]
                logger.info(f"🗑️ 已清除客户端 {client_id} 的对话历史 ({history_count} 条)")
            else:
                logger.debug(f"📝 客户端 {client_id} 没有对话历史需要清除")
                
        except Exception as e:
            logger.error(f"❌ 清除对话历史失败: {e}")
    
    def get_conversation_summary(self, client_id: str) -> str:
        """获取对话摘要信息"""
        try:
            if client_id in self.conversation_history:
                history = self.conversation_history[client_id]
                conversation_count = len(history) // 2  # 每轮对话包含问题和回答
                return f"对话历史: {conversation_count} 轮对话"
            else:
                return "无对话历史"
                
        except Exception as e:
            logger.error(f"❌ 获取对话摘要失败: {e}")
            return "获取对话摘要失败"
    
    def get_conversation_history(self, client_id: str, max_rounds: int = 5) -> List[Dict[str, str]]:
        """获取指定客户端的对话历史"""
        try:
            if client_id in self.conversation_history:
                history = self.conversation_history[client_id]
                # 返回最近的对话轮数
                max_messages = max_rounds * 2
                return history[-max_messages:] if len(history) > max_messages else history
            else:
                return []
                
        except Exception as e:
            logger.error(f"❌ 获取对话历史失败: {e}")
            return []
    
    def get_all_clients_summary(self) -> Dict[str, Any]:
        """获取所有客户端的对话统计信息"""
        try:
            summary = {
                'total_clients': len(self.conversation_history),
                'clients_info': {}
            }
            
            for client_id, history in self.conversation_history.items():
                summary['clients_info'][client_id] = {
                    'conversation_rounds': len(history) // 2,
                    'total_messages': len(history),
                    'last_activity': 'recent'  # 简化表示
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ 获取客户端统计信息失败: {e}")
            return {'error': str(e)}
    
    def update_system_prompt(self, new_prompt: str):
        """更新系统提示词"""
        try:
            old_prompt = self.system_prompt
            self.system_prompt = new_prompt
            logger.info(f"🔄 系统提示词已更新")
            logger.debug(f"📝 旧提示词: {old_prompt[:50]}...")
            logger.debug(f"📝 新提示词: {new_prompt[:50]}...")
            
        except Exception as e:
            logger.error(f"❌ 更新系统提示词失败: {e}")
    
    def get_module_status(self) -> Dict[str, Any]:
        """获取模块状态信息"""
        try:
            return {
                'module': 'LLM',
                'status': 'active',
                'api_configured': bool(self.API_KEY),
                'base_url': self.base_url,
                'model': self.model,
                'total_clients': len(self.conversation_history),
                'system_prompt': self.system_prompt[:100] + "..." if len(self.system_prompt) > 100 else self.system_prompt
            }
            
        except Exception as e:
            logger.error(f"❌ 获取模块状态失败: {e}")
            return {'error': str(e)}
    
    def test_api_connection(self) -> bool:
        """测试API连接"""
        try:
            # 发送一个简单的测试请求
            url = f"{self.base_url}/v1/models"
            headers = {"Authorization": f"Bearer {self.API_KEY}"}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                logger.info("✅ LLM API连接测试成功")
                return True
            else:
                logger.warning(f"⚠️ LLM API连接测试失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ LLM API连接测试异常: {e}")
            return False
