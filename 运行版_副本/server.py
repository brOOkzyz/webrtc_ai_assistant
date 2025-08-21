#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebRTC语音助手服务端 - 模块化架构
主要功能：
1. 管理WebSocket客户端连接
2. 处理音频数据流
3. 协调ASR、LLM、TTS三个核心模块
4. 提供语音助手服务

版本: 2.0.0
"""

import asyncio
import websockets
import logging
import time
import uuid
import json
from concurrent.futures import ThreadPoolExecutor

# 导入自定义模块
from asr_module import ASRModule
from llm_module import LLMModule
from tts_module import TTSModule
from audio_processor import AudioProcessor

# 配置日志系统
logging.basicConfig(
    level=logging.INFO, 
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('server.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class WebRTCServer:
    """
    WebRTC语音助手服务器类
    
    负责：
    - 管理客户端连接
    - 处理音频数据流
    - 协调语音识别、对话生成、语音合成
    - 提供实时语音交互服务
    """
    
    def __init__(self, host='localhost', port=8765):
        """
        初始化WebRTC服务器
        
        Args:
            host (str): 服务器监听地址，默认localhost
            port (int): 服务器监听端口，默认8765
        """
        self.host = host
        self.port = port
        
        # 初始化核心功能模块
        self.asr_module = ASRModule()
        self.llm_module = LLMModule()
        self.tts_module = TTSModule()
        self.audio_processor = AudioProcessor(buffer_size=50)
        
        # 客户端管理
        self.clients = {}
        self.executor = ThreadPoolExecutor(max_workers=20)
        
    async def start(self):
        """启动WebRTC服务器"""
        logger.info(f"🚀 正在启动WebRTC服务器 {self.host}:{self.port}")
        
        try:
            # 创建WebSocket服务器并开始监听
            self.websocket_server = await websockets.serve(
                self.handle_client, 
                self.host, 
                self.port
            )
            
            logger.info(f"✅ WebRTC服务器启动成功！")
            logger.info(f"📍 监听地址: {self.host}:{self.port}")
            logger.info(f"💡 客户端可通过 webrtc_client.html 连接")
            logger.info(f"🔄 等待客户端连接...")
            
            # 保持服务器运行，等待客户端连接
            await asyncio.Future()
            
        except Exception as e:
            logger.error(f"❌ 服务器启动失败: {e}")
            raise
    
    async def stop(self):
        """停止WebRTC服务器"""
        try:
            if hasattr(self, 'websocket_server') and self.websocket_server:
                self.websocket_server.close()
                await self.websocket_server.wait_closed()
                logger.info("✅ WebRTC服务器已停止")
        except Exception as e:
            logger.error(f"❌ 停止服务器失败: {e}")
    
    async def handle_client(self, websocket):
        """处理新客户端连接"""
        # 为每个客户端生成唯一ID
        client_id = str(uuid.uuid4())
        
        # 记录客户端信息
        self.clients[client_id] = {
            'websocket': websocket, 
            'id': client_id, 
            'connected_at': time.time(),
            'status': 'connected'
        }
        
        logger.info(f"🔌 新客户端连接: {client_id}")
        
        try:
            # 发送连接确认消息
            await self.send_message(websocket, {
                'type': 'connection_established', 
                'client_id': client_id, 
                'message': '连接成功，语音助手已就绪'
            })
            
            # 处理客户端消息流
            async for message in websocket:
                await self.process_message(client_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 客户端 {client_id} 主动断开连接")
        except Exception as e:
            logger.error(f"❌ 处理客户端 {client_id} 消息时出错: {e}")
        finally:
            # 清理客户端资源
            await self.cleanup_client(client_id)
    
    async def process_message(self, client_id: str, message):
        """处理客户端发送的消息"""
        try:
            # 根据消息类型进行不同处理
            if isinstance(message, bytes):
                # 二进制音频数据，直接处理
                await self.handle_binary_audio_data(client_id, message)
            elif isinstance(message, str):
                # 文本消息，尝试解析JSON
                await self.handle_text_message(client_id, message)
            else:
                logger.warning(f"⚠️ 收到未知类型的消息: {type(message)}")
                
        except Exception as e:
            logger.error(f"❌ 处理消息失败: {e}")
            await self.send_error_message(client_id, f"消息处理失败: {str(e)}")
    
    async def handle_binary_audio_data(self, client_id: str, audio_data: bytes):
        """处理二进制音频数据"""
        try:
            logger.debug(f"🎵 收到二进制音频数据: {len(audio_data)} 字节")
            
            # 将音频数据添加到处理缓冲区
            if self.audio_processor.add_audio_data(client_id, audio_data):
                # 取消之前的ASR任务（如果存在）
                if client_id in self.audio_processor.asr_tasks and self.audio_processor.asr_tasks[client_id] is not None:
                    try:
                        self.audio_processor.asr_tasks[client_id].cancel()
                    except Exception as e:
                        logger.warning(f"⚠️ 取消ASR任务失败: {e}")
                
                # 创建新的延迟ASR处理任务
                self.audio_processor.asr_tasks[client_id] = asyncio.create_task(
                    self.delayed_asr_processing(client_id)
                )
                
        except Exception as e:
            logger.error(f"❌ 处理二进制音频数据失败: {e}")
    
    async def handle_text_message(self, client_id: str, message_text: str):
        """处理文本消息"""
        try:
            # 尝试解析JSON消息
            parsed_message = json.loads(message_text)
            message_type = parsed_message.get('type')
            
            logger.info(f"📝 收到文本消息: {message_type}")
            
            # 根据消息类型分发处理
            if message_type == 'audio_data':
                # 处理base64编码的音频数据
                await self.handle_base64_audio_data(client_id, parsed_message.get('audio', ''))
            elif message_type == 'text':
                # 处理纯文本输入
                await self.handle_text_input(client_id, parsed_message)
            elif message_type == 'interrupt_tts':
                # 处理TTS打断请求
                await self.handle_tts_interruption(client_id, parsed_message)
            elif message_type == 'ping':
                # 处理心跳检测
                await self.send_message(self.clients[client_id]['websocket'], {
                    'type': 'pong', 
                    'timestamp': time.time()
                })
            else:
                logger.warning(f"⚠️ 未知的消息类型: {message_type}")
                
        except json.JSONDecodeError:
            logger.warning(f"⚠️ 收到无效的JSON消息: {message_text[:100]}...")
        except Exception as e:
            logger.error(f"❌ 处理文本消息失败: {e}")
    
    async def handle_base64_audio_data(self, client_id: str, audio_data: str):
        """处理base64编码的音频数据"""
        try:
            import base64
            audio_bytes = base64.b64decode(audio_data)
            logger.debug(f"🎵 收到base64编码音频数据: {len(audio_bytes)} 字节")
            
            # 将解码后的音频数据添加到处理缓冲区
            if self.audio_processor.add_audio_data(client_id, audio_bytes):
                # 取消之前的ASR任务
                if client_id in self.audio_processor.asr_tasks and self.audio_processor.asr_tasks[client_id] is not None:
                    try:
                        self.audio_processor.asr_tasks[client_id].cancel()
                    except Exception as e:
                        logger.warning(f"⚠️ 取消ASR任务失败: {e}")
                
                # 创建新的延迟ASR处理任务
                self.audio_processor.asr_tasks[client_id] = asyncio.create_task(
                    self.delayed_asr_processing(client_id)
                )
                
        except Exception as e:
            logger.error(f"❌ 处理base64音频数据失败: {e}")
    
    async def handle_text_input(self, client_id: str, message_data: dict):
        """处理纯文本输入"""
        text = message_data.get('text', '')
        if text:
            logger.info(f"📝 收到文本输入: {text}")
            await self.process_llm_conversation(client_id, text)
    
    async def delayed_asr_processing(self, client_id: str):
        """延迟ASR处理，等待语音真正结束"""
        try:
            # 等待1秒，让语音输入完成
            await asyncio.sleep(1.0)
            
            if client_id in self.audio_processor.last_audio_time:
                # 检查是否已经静音足够长时间
                if self.audio_processor.is_silent(client_id, silence_threshold=1.0):
                    # 检查是否有足够的音频数据进行处理
                    if self.audio_processor.has_sufficient_audio(client_id, threshold=3):
                        logger.info(f"🎤 语音输入结束，开始ASR处理")
                        await self.process_audio_for_asr(client_id)
                    else:
                        logger.info(f"⏳ 音频数据不足，继续等待...")
                        # 继续等待，创建新的延迟任务
                        self.audio_processor.asr_tasks[client_id] = asyncio.create_task(
                            self.delayed_asr_processing(client_id)
                        )
                        
        except asyncio.CancelledError:
            # 任务被取消，这是正常情况
            pass
        except Exception as e:
            logger.error(f"❌ 延迟ASR处理失败: {e}")
    
    async def process_audio_for_asr(self, client_id: str):
        """处理音频进行语音识别"""
        try:
            logger.info(f"🎯 开始ASR语音识别")
            
            # 获取音频缓冲区中的数据
            audio_data = self.audio_processor.get_audio_data(client_id)
            if not audio_data:
                logger.warning("⚠️ 音频缓冲区为空，无法进行ASR处理")
                return
            
            # 在线程池中执行ASR识别（避免阻塞主线程）
            loop = asyncio.get_event_loop()
            asr_result = await loop.run_in_executor(
                self.executor, 
                self.asr_module.recognize_speech, 
                audio_data
            )
            
            if asr_result:
                # ASR识别成功，发送结果给客户端
                await self.send_message(self.clients[client_id]['websocket'], {
                    'type': 'asr_result', 
                    'text': asr_result, 
                    'timestamp': time.time()
                })
                
                # 继续处理LLM对话
                await self.process_llm_conversation(client_id, asr_result)
            else:
                # ASR识别失败，发送错误消息
                await self.send_message(self.clients[client_id]['websocket'], {
                    'type': 'asr_error', 
                    'message': '语音识别失败，请重试', 
                    'timestamp': time.time()
                })
                
        except Exception as e:
            logger.error(f"❌ ASR处理失败: {e}")
    
    async def process_llm_conversation(self, client_id: str, recognized_text: str):
        """处理LLM对话"""
        try:
            logger.info(f"🤖 处理LLM对话: {recognized_text}")
            
            # 在线程池中执行LLM请求
            loop = asyncio.get_event_loop()
            llm_response = await loop.run_in_executor(
                self.executor, 
                self.llm_module.ask_question, 
                recognized_text, 
                client_id
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
            else:
                logger.warning("⚠️ LLM未返回有效回复")
                
        except Exception as e:
            logger.error(f"❌ LLM处理失败: {e}")
    
    async def generate_tts_audio(self, client_id: str, text: str):
        """生成TTS音频"""
        try:
            logger.info(f"🔊 开始生成TTS音频: {text}")
            
            # 在线程池中执行TTS合成
            loop = asyncio.get_event_loop()
            audio_data = await loop.run_in_executor(
                self.executor, 
                self.tts_module.synthesize_speech, 
                text
            )
            
            if audio_data:
                # 将音频数据编码为base64
                import base64
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                # 发送TTS音频给客户端
                await self.send_message(self.clients[client_id]['websocket'], {
                    'type': 'tts_audio', 
                    'audio': audio_base64, 
                    'text': text, 
                    'timestamp': time.time()
                })
                
                logger.info(f"✅ TTS音频生成完成: {len(audio_data)} 字节")
            else:
                logger.warning("⚠️ TTS模块未返回有效音频数据")
                
        except Exception as e:
            logger.error(f"❌ TTS生成失败: {e}")
    
    async def handle_tts_interruption(self, client_id: str, message_data: dict):
        """处理TTS打断请求"""
        try:
            logger.info(f"🛑 收到客户端 {client_id} 的TTS打断请求")
            
            # 清理音频缓冲区，准备处理新的语音输入
            self.audio_processor.clear_buffer(client_id)
            
            # 取消正在进行的ASR任务
            if client_id in self.audio_processor.asr_tasks and self.audio_processor.asr_tasks[client_id] is not None:
                try:
                    self.audio_processor.asr_tasks[client_id].cancel()
                except Exception as e:
                    logger.warning(f"⚠️ 取消ASR任务失败: {e}")
            
            # 发送打断确认消息给客户端
            await self.send_message(self.clients[client_id]['websocket'], {
                'type': 'interruption_confirmed', 
                'message': 'TTS播放已停止，准备处理新的语音输入', 
                'timestamp': time.time()
            })
            
            logger.info(f"✅ 客户端 {client_id} 的TTS打断处理完成")
            
        except Exception as e:
            logger.error(f"❌ 处理TTS打断失败: {e}")
    
    async def send_message(self, websocket, message_data: dict):
        """发送消息给客户端"""
        try:
            message = json.dumps(message_data, ensure_ascii=False)
            await websocket.send(message)
        except Exception as e:
            logger.error(f"❌ 发送消息失败: {e}")
    
    async def send_error_message(self, client_id: str, error_message: str):
        """发送错误消息给客户端"""
        try:
            await self.send_message(self.clients[client_id]['websocket'], {
                'type': 'error', 
                'message': error_message, 
                'timestamp': time.time()
            })
        except Exception as e:
            logger.error(f"❌ 发送错误消息失败: {e}")
    
    async def cleanup_client(self, client_id: str):
        """清理客户端资源"""
        try:
            # 清理音频处理资源
            self.audio_processor.cleanup_client(client_id)
            
            # 清理对话历史
            self.llm_module.clear_conversation_history(client_id)
            
            # 清理客户端信息
            if client_id in self.clients:
                del self.clients[client_id]
            
            logger.info(f"🧹 客户端 {client_id} 资源清理完成")
            
        except Exception as e:
            logger.error(f"❌ 清理客户端资源失败: {e}")

async def main():
    """主函数 - 启动WebRTC语音助手服务器"""
    try:
        # 创建并启动服务器
        server = WebRTCServer()
        await server.start()
    except KeyboardInterrupt:
        logger.info("🛑 服务器被用户中断")
    except Exception as e:
        logger.error(f"❌ 服务器运行异常: {e}")
        raise

if __name__ == "__main__":
    try:
        # 运行主函数
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 服务器被用户中断")
    except Exception as e:
        logger.error(f"❌ 服务器运行异常: {e}")
        exit(1)
