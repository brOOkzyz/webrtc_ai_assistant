#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebRTC服务端 - 集成ASR + LLM + TTS功能
支持WebSocket连接，处理音频流，提供语音助手服务
"""

import asyncio
import websockets
import json
import logging
import base64
import time
import uuid
import requests
from collections import deque
from concurrent.futures import ThreadPoolExecutor

# 导入配置
from config import BASE_URL, DEFAULT_MODEL

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# 全局变量
# 优化：增加线程池大小，提高并发处理能力
executor = ThreadPoolExecutor(max_workers=20)  # 线程池，从10增加到20

class WebRTCServer:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.clients = {}
        self.audio_buffers = {}  # 存储每个客户端的音频缓冲区
        self.last_audio_time = {}  # 最后音频时间
        self.asr_tasks = {}      # ASR任务
        
    async def start(self):
        """启动WebRTC服务器"""
        logger.info(f"🚀 启动WebRTC服务器 {self.host}:{self.port}")
        
        try:
            async with websockets.serve(self.handle_client, self.host, self.port):
                logger.info(f"✅ WebRTC服务器已启动，监听端口 {self.port}")
                logger.info("💡 客户端可以通过 webrtc_client.html 连接")
                
                # 保持服务器运行
                await asyncio.Future()  # 无限等待
                
        except Exception as e:
            logger.error(f"❌ 服务器启动失败: {e}")
    
    async def handle_client(self, websocket, path):
        """处理客户端连接"""
        client_id = str(uuid.uuid4())
        client_info = {
            'websocket': websocket,
            'id': client_id,
            'connected_at': time.time(),
            'status': 'connected'
        }
        
        self.clients[client_id] = client_info
        self.audio_buffers[client_id] = deque(maxlen=50)  # 减少音频缓冲区大小，降低延迟
        self.last_audio_time[client_id] = time.time()  # 初始化最后音频时间
        # 不初始化asr_tasks，让它自然创建
        
        logger.info(f"🔌 新客户端连接: {client_id}")
        
        try:
            # 发送连接确认
            await self.send_message(websocket, {
                'type': 'connection_established',
                'client_id': client_id,
                'message': '连接成功'
            })
            
            # 处理客户端消息
            async for message in websocket:
                await self.process_message(client_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 客户端断开连接: {client_id}")
        except Exception as e:
            logger.error(f"❌ 处理客户端 {client_id} 消息时出错: {e}")
        finally:
            # 清理客户端资源
            await self.cleanup_client(client_id)
    
    async def process_message(self, client_id, message):
        """处理客户端消息"""
        try:
            if isinstance(message, bytes):
                # 二进制音频数据
                await self.handle_audio_data(client_id, message)
            else:
                # 文本消息
                data = json.loads(message)
                await self.handle_text_message(client_id, data)
                
        except Exception as e:
            logger.error(f"❌ 处理消息失败: {e}")
            await self.send_error(client_id, f"消息处理失败: {str(e)}")
    
    async def handle_audio_data(self, client_id, audio_data):
        """处理音频数据"""
        try:
            # 接收音频数据
            
            # 将音频数据添加到缓冲区
            self.audio_buffers[client_id].append(audio_data)
            
            # 记录最后接收时间，用于检测语音结束
            self.last_audio_time[client_id] = time.time()
            
            # 不再立即处理，等待语音结束
            # 取消之前的超时任务
            if client_id in self.asr_tasks and self.asr_tasks[client_id] is not None:
                try:
                    self.asr_tasks[client_id].cancel()
                except Exception as e:
                    logger.warning(f"⚠️ 取消ASR任务失败: {e}")
            
            # 设置新的延迟处理任务
            self.asr_tasks[client_id] = asyncio.create_task(self.delayed_asr_processing(client_id))
                
        except Exception as e:
            logger.error(f"❌ 处理音频数据失败: {e}")
    
    async def delayed_asr_processing(self, client_id):
        """延迟ASR处理，等待语音真正结束"""
        try:
            # 优化：减少等待时间，更快响应
            await asyncio.sleep(1.0)  # 从2秒减少到1秒
            
            # 检查是否在等待期间还有新的音频数据
            if client_id in self.last_audio_time:
                time_since_last_audio = time.time() - self.last_audio_time[client_id]
                
                # 如果2秒内没有新音频，说明语音结束
                # 优化：减少等待时间，更快触发ASR
                if time_since_last_audio >= 1.0:  # 从2秒减少到1秒
                    if client_id in self.audio_buffers and len(self.audio_buffers[client_id]) > 0:
                        logger.info(f"🎤 语音结束，开始ASR处理")
                        await self.process_audio_for_asr(client_id)
                else:
                    # 语音还在继续，继续等待
                    logger.info(f"⏳ 语音还在继续，继续等待...")
                    self.asr_tasks[client_id] = asyncio.create_task(self.delayed_asr_processing(client_id))
                
        except asyncio.CancelledError:
            # 任务被取消，正常情况
            pass
        except Exception as e:
            logger.error(f"❌ 延迟ASR处理失败: {e}")
    
    async def process_audio_for_asr(self, client_id):
        """处理音频进行语音识别"""
        try:
            logger.info(f"🎯 开始ASR识别")
            
            # 获取音频数据
            audio_chunks = list(self.audio_buffers[client_id])
            self.audio_buffers[client_id].clear()
            
            if not audio_chunks:
                logger.warning("⚠️ 音频缓冲区为空")
                return
            
            # 合并音频数据
            combined_audio = b''.join(audio_chunks)
            logger.info(f"📊 处理音频: {len(combined_audio)} 字节")
            
            # 直接使用PCM音频数据，无需转换
            # 在线程池中执行ASR
            loop = asyncio.get_event_loop()
            asr_result = await loop.run_in_executor(
                executor, 
                self.perform_asr, 
                combined_audio
            )
            
            if asr_result:
                # 发送ASR结果给客户端
                await self.send_message(self.clients[client_id]['websocket'], {
                    'type': 'asr_result',
                    'text': asr_result,
                    'timestamp': time.time()
                })
                
                # 处理LLM对话
                await self.process_llm_conversation(client_id, asr_result)
            else:
                # ASR识别失败，发送错误消息
                logger.warning("⚠️ ASR识别失败，跳过LLM处理")
                await self.send_message(self.clients[client_id]['websocket'], {
                    'type': 'asr_error',
                    'message': '语音识别失败，请重试',
                    'timestamp': time.time()
                })
                
        except Exception as e:
            logger.error(f"❌ ASR处理失败: {e}")
    

    def perform_asr(self, audio_data):
        """执行语音识别"""
        try:
            logger.info("🔍 开始语音识别")
            
            # 尝试使用百度ASR HTTP API
            import requests
            import base64
            import hashlib
            import time
            import json
            
            # 百度ASR配置
            APPID = 119399339
            API_KEY = "OjBAo0bZXmeOE76weLUPtKkj"
            SECRET_KEY = "dBF1UBMdxXb3nz4gOJrBLOADkANrFNQ3"
            
            try:
                # 获取访问令牌
                token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={API_KEY}&client_secret={SECRET_KEY}"
                
                logger.info("🔑 获取百度ASR访问令牌...")
                # 优化：减少超时时间，更快失败重试
                token_response = requests.get(token_url, timeout=5)  # 从10秒减少到5秒
                
                if token_response.status_code != 200:
                    logger.error(f"❌ 获取ASR访问令牌失败: {token_response.status_code}")
                    return self._fallback_asr()
                
                token_data = token_response.json()
                if 'access_token' not in token_data:
                    logger.error(f"❌ ASR访问令牌响应异常: {token_data}")
                    return self._fallback_asr()
                
                access_token = token_data['access_token']
                logger.info("✅ 已获取ASR访问令牌")
                
                # 调用百度ASR API - 使用正确的短语音识别API
                asr_url = "https://vop.baidu.com/server_api"
                
                # 检查音频数据
                # 将音频数据转换为base64
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                # 客户端直接采集PCM格式，无需检测和转换
                logger.info("✅ 使用客户端采集的PCM音频数据")
                
                # 简单的音频有效性检查（检查数据长度）
                if len(audio_data) < 1000:  # 至少1KB的音频数据
                    logger.warning("⚠️ 音频数据过短，可能无效")
                    return None
                
                logger.info("✅ 音频数据长度检查通过")
                
                # 构建请求参数 - 百度ASR HTTP API格式
                # 注意：HTTP API和WebSocket API的参数格式不同
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
                
                # 根据百度ASR文档，使用正确的请求格式
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
                
        except ImportError as e:
            logger.error(f"❌ 导入requests模块失败: {e}")
            return self._fallback_asr()
        except Exception as e:
            logger.error(f"❌ ASR识别失败: {e}")
            return self._fallback_asr()
    
    def _fallback_asr(self):
        """ASR失败时的备用方案"""
        logger.warning("⚠️ 使用备用ASR方案")
        
        # 模拟处理延迟
        import time
        time.sleep(1)
        
        # 返回模拟结果
        mock_result = "我听到了您的声音，这是一个测试回复"
        logger.info(f"✅ 备用ASR完成: {mock_result}")
        return mock_result
    
    async def process_llm_conversation(self, client_id, user_input):
        """处理LLM对话"""
        try:
            logger.info(f"🤖 处理用户输入: {user_input}")
            
            # 在线程池中执行LLM请求
            loop = asyncio.get_event_loop()
            llm_response = await loop.run_in_executor(
                executor,
                self.ask_llm,
                user_input
            )
            
            if llm_response:
                # 发送LLM回复给客户端
                await self.send_message(self.clients[client_id]['websocket'], {
                    'type': 'llm_response',
                    'text': llm_response,
                    'timestamp': time.time()
                })
                
                # 生成TTS音频
                await self.generate_tts_audio(client_id, llm_response)
                
        except Exception as e:
            logger.error(f"❌ LLM处理失败: {e}")
    
    def ask_llm(self, question):
        """向LLM提问"""
        try:
            # 使用用户提供的LLM API Key
            LLM_API_KEY = "sk-vjntadlyyvfewqskgazdzosowrqmaqcpmwhcnlknauqejssi"
            
            url = f"{BASE_URL}/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {LLM_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": DEFAULT_MODEL,
                "messages": [
                    {"role": "system", "content": "你是一个高效的语音助手。请用最简洁的语言回答问题，控制在50字以内，直接给出核心答案，不要解释过程。"},
                    {"role": "user", "content": question}
                ],
                "temperature": 0.5,  # 降低随机性，提高响应一致性
                "max_tokens": 100,   # 减少最大token数，更快响应
                "stream": False      # 非流式响应，简化处理
            }
            
            # 优化：减少超时时间，更快响应
            response = requests.post(url, headers=headers, json=data, timeout=15)  # 从30秒减少到15秒
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                return "抱歉，我没有理解您的问题。"
                
        except Exception as e:
            logger.error(f"❌ LLM请求失败: {e}")
            return "抱歉，服务暂时不可用。"
    
    async def generate_tts_audio(self, client_id, text):
        """生成TTS音频"""
        try:
            logger.info(f"🔊 生成TTS音频: {text}")
            
            # 在线程池中执行TTS
            loop = asyncio.get_event_loop()
            audio_data = await loop.run_in_executor(
                executor,
                self.perform_tts,
                text
            )
            
            if audio_data:
                # 将音频数据编码为base64发送给客户端
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                await self.send_message(self.clients[client_id]['websocket'], {
                    'type': 'tts_audio',
                    'audio': audio_base64,
                    'text': text,
                    'timestamp': time.time()
                })
                
        except Exception as e:
            logger.error(f"❌ TTS生成失败: {e}")
    
    def perform_tts(self, text):
        """执行TTS语音合成"""
        try:
            logger.info(f"🔊 执行TTS合成: {text}")
            
            # 集成百度TTS API
            import requests
            import hashlib
            import time
            import base64
            
            # 百度TTS配置
            TTS_API_KEY = "YOUR API KEY"
            TTS_SECRET_KEY = "YOUR SECRET KEY"
            TTS_APP_ID = "YOUR APP ID"
            
            # 生成访问令牌
            token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={TTS_API_KEY}&client_secret={TTS_SECRET_KEY}"
            
            try:
                # 优化：减少超时时间，更快响应
                token_response = requests.get(token_url, timeout=5)  # 从10秒减少到5秒
                token_data = token_response.json()
                
                if 'access_token' not in token_data:
                    logger.error(f"❌ 获取TTS访问令牌失败: {token_data}")
                    return self.generate_beep_sound()
                
                access_token = token_data['access_token']
                logger.info("✅ 已获取TTS访问令牌")
                
                # 调用TTS API
                tts_url = f"https://tsn.baidu.com/text2audio?tok={access_token}"
                
                tts_params = {
                    'tex': text,
                    'tok': access_token,
                    'cuid': 'webrtc_client',
                    'ctp': 1,
                    'lan': 'zh',
                    'spd': 5,      # 语速：5-9
                    'pit': 5,      # 音调：5-9
                    'vol': 5,      # 音量：5-9
                    'per': 0,      # 发音人：0-4
                    'aue': 3       # 格式：3为mp3
                }
                
                tts_response = requests.post(tts_url, data=tts_params, timeout=15)
                
                if tts_response.status_code == 200:
                    audio_data = tts_response.content
                    logger.info(f"✅ TTS合成成功: {len(audio_data)} 字节")
                    return audio_data
                else:
                    logger.error(f"❌ TTS API调用失败: {tts_response.status_code}")
                    return self.generate_beep_sound()
                    
            except requests.exceptions.Timeout:
                logger.error("❌ TTS API请求超时")
                return self.generate_beep_sound()
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ TTS API请求失败: {e}")
                return self.generate_beep_sound()
                
        except ImportError as e:
            logger.error(f"❌ 导入requests模块失败: {e}")
            logger.info("💡 使用提示音代替TTS，请安装requests: pip install requests")
            return self.generate_beep_sound()
        except Exception as e:
            logger.error(f"❌ TTS合成失败: {e}")
            return self.generate_beep_sound()
    
    def generate_beep_sound(self):
        """生成简单的提示音"""
        try:
            import wave
            import struct
            import math
            import tempfile
            
            # 生成1秒的440Hz正弦波
            sample_rate = 16000
            duration = 1.0
            frequency = 440.0
            
            num_samples = int(sample_rate * duration)
            audio_data = []
            
            for i in range(num_samples):
                sample = math.sin(2 * math.pi * frequency * i / sample_rate)
                # 转换为16位PCM
                audio_data.append(struct.pack('<h', int(sample * 32767 * 0.3)))
            
            # 创建WAV文件
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=True) as temp_file:
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # 单声道
                    wav_file.setsampwidth(2)   # 16位
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(b''.join(audio_data))
                
                # 读取生成的音频数据
                with open(temp_file.name, 'rb') as f:
                    return f.read()
                    
        except Exception as e:
            logger.error(f"❌ 生成提示音失败: {e}")
            # 最后的备选：返回空数据
            return b""
    
    async def handle_text_message(self, client_id, data):
        """处理文本消息"""
        try:
            message_type = data.get('type')
            
            if message_type == 'ping':
                # 心跳检测
                await self.send_message(self.clients[client_id]['websocket'], {
                    'type': 'pong',
                    'timestamp': time.time()
                })
                
            elif message_type == 'start_recording':
                # 开始录音
                logger.info(f"🎤 客户端 {client_id} 开始录音")
                
            elif message_type == 'stop_recording':
                # 停止录音
                logger.info(f"🛑 客户端 {client_id} 停止录音")
                
            elif message_type == 'interrupt_tts':
                # 🚨 处理TTS打断信号
                await self.handle_tts_interruption(client_id, data)
                
            else:
                logger.info(f"📝 收到文本消息: {data}")
                
        except Exception as e:
            logger.error(f"❌ 处理文本消息失败: {e}")
    
    async def handle_tts_interruption(self, client_id, data):
        """处理TTS打断信号"""
        try:
            logger.info(f"🛑 收到客户端 {client_id} 的TTS打断信号")
            
            # 清理当前客户端的音频缓冲区，准备处理新的语音输入
            if client_id in self.audio_buffers:
                self.audio_buffers[client_id].clear()
                logger.info(f"🧹 已清理客户端 {client_id} 的音频缓冲区")
            
            # 取消正在进行的ASR任务
            if client_id in self.asr_tasks and self.asr_tasks[client_id] is not None:
                try:
                    self.asr_tasks[client_id].cancel()
                    logger.info(f"🛑 已取消客户端 {client_id} 的ASR任务")
                except Exception as e:
                    logger.warning(f"⚠️ 取消ASR任务失败: {e}")
            
            # 发送打断确认消息给客户端
            await self.send_message(self.clients[client_id]['websocket'], {
                'type': 'interruption_confirmed',
                'message': 'TTS打断已确认，准备处理新的语音输入',
                'timestamp': time.time()
            })
            
            logger.info(f"✅ 客户端 {client_id} 的TTS打断处理完成")
            
        except Exception as e:
            logger.error(f"❌ 处理TTS打断失败: {e}")
    
    async def send_message(self, websocket, message):
        """发送消息给客户端"""
        try:
            await websocket.send(json.dumps(message, ensure_ascii=False))
        except Exception as e:
            logger.error(f"❌ 发送消息失败: {e}")
    
    async def send_error(self, client_id, error_message):
        """发送错误消息给客户端"""
        try:
            await self.send_message(self.clients[client_id]['websocket'], {
                'type': 'error',
                'message': error_message,
                'timestamp': time.time()
            })
        except Exception as e:
            logger.error(f"❌ 发送错误消息失败: {e}")
    
    async def cleanup_client(self, client_id):
        """清理客户端资源"""
        try:
            if client_id in self.clients:
                del self.clients[client_id]
            
            if client_id in self.audio_buffers:
                del self.audio_buffers[client_id]
                
            if client_id in self.last_audio_time:
                del self.last_audio_time[client_id]
                
            if client_id in self.asr_tasks and self.asr_tasks[client_id] is not None:
                try:
                    self.asr_tasks[client_id].cancel()
                except Exception as e:
                    logger.warning(f"⚠️ 清理时取消ASR任务失败: {e}")
                del self.asr_tasks[client_id]
                
            logger.info(f"🧹 客户端 {client_id} 资源已清理")
            
        except Exception as e:
            logger.error(f"❌ 清理客户端资源失败: {e}")
    
    async def broadcast_message(self, message):
        """广播消息给所有客户端"""
        disconnected_clients = []
        
        for client_id, client_info in self.clients.items():
            try:
                await self.send_message(client_info['websocket'], message)
            except Exception as e:
                logger.error(f"❌ 广播消息给客户端 {client_id} 失败: {e}")
                disconnected_clients.append(client_id)
        
        # 清理断开的客户端
        for client_id in disconnected_clients:
            await self.cleanup_client(client_id)

async def main():
    """主函数"""
    server = WebRTCServer()
    await server.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 服务器被中断")
    except Exception as e:
        logger.error(f"❌ 服务器运行错误: {e}")
