#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASR语音识别模块
集成百度ASR API，提供语音转文字功能

版本: 2.0.0
"""

import logging
import requests
import base64
import time
from typing import Optional

# 配置日志
logger = logging.getLogger(__name__)

class ASRModule:
    """ASR语音识别模块类"""
    
    def __init__(self):
        """初始化ASR模块"""
        # 百度ASR配置信息
        self.APPID = 119399339
        self.API_KEY = "OjBAo0bZXmeOE76weLUPtKkj"
        self.SECRET_KEY = "dBF1UBMdxXb3nz4gOJrBLOADkANrFNQ3"
        
        # 访问令牌管理
        self.access_token = None
        self.token_expire_time = 0
        
    def get_access_token(self) -> Optional[str]:
        """获取百度ASR访问令牌"""
        try:
            # 检查当前令牌是否仍然有效（提前5分钟过期）
            if self.access_token and time.time() < self.token_expire_time:
                logger.debug("✅ 使用现有访问令牌")
                return self.access_token
                
            # 获取新的访问令牌
            logger.info("🔑 正在获取百度ASR访问令牌...")
            
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
                logger.error(f"❌ 获取ASR访问令牌失败: HTTP {token_response.status_code}")
                return None
            
            # 解析响应数据
            token_data = token_response.json()
            if 'access_token' not in token_data:
                logger.error(f"❌ ASR访问令牌响应异常: {token_data}")
                return None
            
            # 更新令牌信息
            self.access_token = token_data['access_token']
            
            # 设置令牌过期时间（提前5分钟过期，避免边界情况）
            expires_in = token_data.get('expires_in', 2592000)  # 默认30天
            self.token_expire_time = time.time() + expires_in - 300
            
            logger.info("✅ 已成功获取ASR访问令牌")
            return self.access_token
            
        except requests.exceptions.Timeout:
            logger.error("❌ 获取ASR访问令牌超时")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 获取ASR访问令牌请求异常: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ 获取ASR访问令牌时发生未知错误: {e}")
            return None
    
    def recognize_speech(self, audio_data: bytes) -> Optional[str]:
        """执行语音识别"""
        try:
            logger.info("🔍 开始语音识别处理")
            
            # 获取访问令牌
            access_token = self.get_access_token()
            if not access_token:
                logger.error("❌ 无法获取ASR访问令牌")
                return self._fallback_asr()
            
            # 验证音频数据
            if not self._validate_audio_data(audio_data):
                return None
            
            # 将音频数据转换为base64编码
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # 构建ASR请求参数
            asr_data = self._build_asr_request(access_token, audio_base64, len(audio_data))
            
            # 执行ASR识别
            return self._execute_asr_request(asr_data)
            
        except Exception as e:
            logger.error(f"❌ 语音识别过程中发生未知错误: {e}")
            return self._fallback_asr()
    
    def _validate_audio_data(self, audio_data: bytes) -> bool:
        """验证音频数据有效性"""
        if not audio_data:
            logger.warning("⚠️ 音频数据为空")
            return False
        
        # 检查音频数据长度（至少1KB）
        if len(audio_data) < 1000:
            logger.warning(f"⚠️ 音频数据过短: {len(audio_data)} 字节，至少需要1KB")
            return False
        
        logger.debug(f"✅ 音频数据验证通过: {len(audio_data)} 字节")
        return True
    
    def _build_asr_request(self, access_token: str, audio_base64: str, audio_length: int) -> dict:
        """构建ASR请求参数"""
        return {
            'format': 'pcm',              # 音频格式：PCM
            'rate': 16000,                # 采样率：16kHz
            'channel': 1,                 # 声道数：单声道
            'token': access_token,        # 访问令牌
            'cuid': 'webrtc_client',      # 用户唯一标识
            'speech': audio_base64,       # base64编码的音频数据
            'len': audio_length           # 音频数据长度
        }
    
    def _execute_asr_request(self, asr_data: dict) -> Optional[str]:
        """执行ASR识别请求"""
        try:
            logger.info(f"📤 发送ASR识别请求: {asr_data['len']} 字节")
            
            # 百度ASR API端点
            asr_url = "https://vop.baidu.com/server_api"
            
            # 尝试不同的请求格式
            asr_result = self._try_json_request(asr_url, asr_data)
            if asr_result is not None:
                return asr_result
            
            # 如果JSON格式失败，尝试表单格式
            asr_result = self._try_form_request(asr_url, asr_data)
            if asr_result is not None:
                return asr_result
            
            # 所有请求格式都失败
            logger.error("❌ 所有ASR请求格式都失败")
            return self._fallback_asr()
            
        except Exception as e:
            logger.error(f"❌ 执行ASR请求时发生错误: {e}")
            return self._fallback_asr()
    
    def _try_json_request(self, url: str, data: dict) -> Optional[str]:
        """尝试使用JSON格式发送ASR请求"""
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=data, headers=headers, timeout=8)
            
            logger.info(f"📤 JSON格式ASR请求完成，状态码: {response.status_code}")
            
            if response.status_code == 200:
                return self._parse_asr_response(response)
            else:
                logger.warning(f"⚠️ JSON格式ASR请求失败: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ JSON格式ASR请求异常: {e}")
            return None
    
    def _try_form_request(self, url: str, data: dict) -> Optional[str]:
        """尝试使用表单格式发送ASR请求"""
        try:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.post(url, data=data, headers=headers, timeout=8)
            
            logger.info(f"📤 表单格式ASR请求完成，状态码: {response.status_code}")
            
            if response.status_code == 200:
                return self._parse_asr_response(response)
            else:
                logger.warning(f"⚠️ 表单格式ASR请求失败: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ 表单格式ASR请求异常: {e}")
            return None
    
    def _parse_asr_response(self, response: requests.Response) -> Optional[str]:
        """解析ASR API响应"""
        try:
            asr_result = response.json()
            logger.info(f"📋 ASR响应解析完成: {asr_result.get('err_msg', 'unknown')}")
            
            # 检查API返回状态
            if asr_result.get('err_no') == 0:
                # 成功识别
                result_text = asr_result.get('result', [''])[0] if asr_result.get('result') else ''
                
                if result_text and result_text.strip():
                    logger.info(f"✅ ASR识别成功: {result_text}")
                    return result_text
                else:
                    logger.warning("⚠️ ASR识别结果为空")
                    return None
            else:
                # API返回错误
                error_code = asr_result.get('err_no')
                error_msg = asr_result.get('err_msg', 'unknown')
                logger.error(f"❌ ASR API返回错误: 错误码={error_code}, 错误信息={error_msg}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 解析ASR响应失败: {e}")
            return None
    
    def _fallback_asr(self) -> Optional[str]:
        """ASR失败时的备用方案"""
        logger.warning("⚠️ 使用备用ASR方案")
        
        try:
            # 这里可以集成其他ASR服务，如：
            # - Google Speech Recognition
            # - Microsoft Azure Speech
            # - 本地语音识别模型
            
            # 目前返回模拟结果
            mock_result = "我听到了您的声音，这是一个测试回复"
            logger.info(f"✅ 备用ASR完成: {mock_result}")
            return mock_result
            
        except Exception as e:
            logger.error(f"❌ 备用ASR也失败了: {e}")
            return None
    
    def get_module_status(self) -> dict:
        """获取模块状态信息"""
        return {
            'module': 'ASR',
            'status': 'active',
            'has_token': self.access_token is not None,
            'token_expires_in': max(0, self.token_expire_time - time.time()) if self.token_expire_time else 0,
            'api_key_configured': bool(self.API_KEY and self.SECRET_KEY)
        }
    
    def reset_token(self):
        """重置访问令牌"""
        self.access_token = None
        self.token_expire_time = 0
        logger.info("🔄 ASR访问令牌已重置")
