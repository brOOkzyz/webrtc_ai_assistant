#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASR语音识别模块
集成百度ASR API，提供语音转文字功能
"""

import logging
import requests
import base64
import time
from typing import Optional

logger = logging.getLogger(__name__)

class ASRModule:
    """ASR语音识别模块"""
    
    def __init__(self):
        # 百度ASR配置
        self.APPID = 119399339
        self.API_KEY = "OjBAo0bZXmeOE76weLUPtKkj"
        self.SECRET_KEY = "dBF1UBMdxXb3nz4gOJrBLOADkANrFNQ3"
        self.access_token = None
        self.token_expire_time = 0
        
    def get_access_token(self) -> Optional[str]:
        """获取百度ASR访问令牌"""
        try:
            # 检查令牌是否过期
            if self.access_token and time.time() < self.token_expire_time:
                return self.access_token
                
            # 获取新的访问令牌
            token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.API_KEY}&client_secret={self.SECRET_KEY}"
            
            logger.info("🔑 获取百度ASR访问令牌...")
            # 优化：减少超时时间，更快失败重试
            token_response = requests.get(token_url, timeout=5)  # 从10秒减少到5秒
            
            if token_response.status_code != 200:
                logger.error(f"❌ 获取ASR访问令牌失败: {token_response.status_code}")
                return None
            
            token_data = token_response.json()
            if 'access_token' not in token_data:
                logger.error(f"❌ ASR访问令牌响应异常: {token_data}")
                return None
            
            self.access_token = token_data['access_token']
            # 设置令牌过期时间（提前5分钟过期）
            self.token_expire_time = time.time() + token_data.get('expires_in', 2592000) - 300
            
            logger.info("✅ 已获取ASR访问令牌")
            return self.access_token
            
        except Exception as e:
            logger.error(f"❌ 获取ASR访问令牌异常: {e}")
            return None
    
    def recognize_speech(self, audio_data: bytes) -> Optional[str]:
        """执行语音识别"""
        try:
            logger.info("🔍 开始语音识别")
            
            # 获取访问令牌
            access_token = self.get_access_token()
            if not access_token:
                logger.error("❌ 无法获取ASR访问令牌")
                return self._fallback_asr()
            
            # 检查音频数据
            if len(audio_data) < 1000:  # 至少1KB的音频数据
                logger.warning("⚠️ 音频数据过短，可能无效")
                return None
            
            logger.info("✅ 音频数据长度检查通过")
            
            # 将音频数据转换为base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # 构建请求参数 - 百度ASR HTTP API格式
            asr_data = {
                'format': 'pcm',          # 音频格式，固定值pcm
                'rate': 16000,            # 采样率，16000Hz
                'channel': 1,             # 声道数，单声道
                'token': access_token,    # 访问令牌
                'cuid': 'webrtc_client',  # 用户唯一ID
                'speech': audio_base64,   # base64编码的音频数据
                'len': len(audio_data)    # 音频数据长度
            }
            
            logger.info(f"📤 发送ASR请求: {len(audio_data)} 字节")
            
            # 调用百度ASR API
            asr_url = "https://vop.baidu.com/server_api"
            
            # 方法1：尝试POST JSON格式
            try:
                headers = {'Content-Type': 'application/json'}
                # 优化：减少超时时间，更快响应
                asr_response = requests.post(asr_url, json=asr_data, headers=headers, timeout=8)  # 从15秒减少到8秒
                logger.info(f"📤 ASR请求完成，状态码: {asr_response.status_code}")
            except Exception as e:
                logger.error(f"❌ JSON请求失败，尝试表单格式")
                # 方法2：尝试表单格式
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                # 优化：减少超时时间，更快响应
                asr_response = requests.post(asr_url, data=asr_data, headers=headers, timeout=8)  # 从15秒减少到8秒
            
            if asr_response.status_code == 200:
                asr_result = asr_response.json()
                logger.info(f"📋 ASR响应: {asr_result.get('err_msg', 'unknown')}")
                
                if asr_result.get('err_no') == 0:
                    result_text = asr_result.get('result', [''])[0] if asr_result.get('result') else ''
                    if result_text and result_text.strip():
                        logger.info(f"✅ ASR识别成功: {result_text}")
                        return result_text
                    else:
                        logger.warning("⚠️ ASR识别结果为空")
                        return None
                else:
                    logger.error(f"❌ ASR API返回错误: 错误码={asr_result.get('err_no')}, 错误信息={asr_result.get('err_msg')}")
                    return self._fallback_asr()
            else:
                logger.error(f"❌ ASR API请求失败: HTTP状态码={asr_response.status_code}")
                logger.error(f"❌ 响应内容: {asr_response.text}")
                return self._fallback_asr()
                
        except requests.exceptions.Timeout:
            logger.error("❌ ASR API请求超时")
            return self._fallback_asr()
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ ASR API请求异常: {e}")
            return self._fallback_asr()
        except Exception as e:
            logger.error(f"❌ ASR识别失败: {e}")
            return self._fallback_asr()
    
    def _fallback_asr(self) -> Optional[str]:
        """ASR失败时的备用方案"""
        logger.warning("⚠️ 使用备用ASR方案")
        # 这里可以集成其他ASR服务，如Google Speech Recognition
        return None
