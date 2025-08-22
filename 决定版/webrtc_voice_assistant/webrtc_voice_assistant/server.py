#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebRTC语音助手服务端 - 模块化架构
"""

import asyncio
import websockets
import logging
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

# 导入自定义模块
from .asr_module import ASRModule
from .llm_module import LLMModule
from .tts_module import TTSModule
from .audio_processor import AudioProcessor

# 配置日志
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class WebRTCServer:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        
        # 初始化功能模块
        self.asr_module = ASRModule()
        self.llm_module = LLMModule()
        self.tts_module = TTSModule()
        self.audio_processor = AudioProcessor(buffer_size=50)
        
        # 客户端管理
        self.clients = {}
        self.executor = ThreadPoolExecutor(max_workers=20)
        
    async def start(self):
        logger.info(f"🚀 启动WebRTC服务器 {self.host}:{self.port}")
        try:
            async with websockets.serve(self.handle_client, self.host, self.port):
                logger.info(f"✅ WebRTC服务器已启动，监听端口 {self.port}")
                await asyncio.Future()
        except Exception as e:
            logger.error(f"❌ 服务器启动失败: {e}")
    
    async def handle_client(self, websocket, path):
        client_id = str(uuid.uuid4())
        self.clients[client_id] = {'websocket': websocket, 'id': client_id, 'connected_at': time.time()}
        logger.info(f"🔌 新客户端连接: {client_id}")
        
        try:
            await self.send_message(websocket, {'type': 'connection_established', 'client_id': client_id, 'message': '连接成功'})
            async for message in websocket:
                await self.process_message(client_id, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 客户端断开连接: {client_id}")
        except Exception as e:
            logger.error(f"❌ 处理客户端 {client_id} 消息时出错: {e}")
        finally:
            await self.cleanup_client(client_id)
    
    async def process_message(self, client_id: str, message: str):
        try:
            import json
            parsed_message = json.loads(message)
            message_type = parsed_message.get('type')
            
            if message_type == 'audio_data':
                await self.handle_audio_data(client_id, parsed_message.get('audio', ''))
            elif message_type == 'text':
                await self.handle_text_message(client_id, parsed_message)
            elif message_type == 'interrupt_tts':
                await self.handle_tts_interruption(client_id, parsed_message)
        except Exception as e:
            logger.error(f"❌ 处理消息失败: {e}")
    
    async def handle_audio_data(self, client_id: str, audio_data: str):
        try:
            import base64
            audio_bytes = base64.b64decode(audio_data)
            
            if self.audio_processor.add_audio_data(client_id, audio_bytes):
                if client_id in self.audio_processor.asr_tasks and self.audio_processor.asr_tasks[client_id] is not None:
                    try:
                        self.audio_processor.asr_tasks[client_id].cancel()
                    except Exception as e:
                        logger.warning(f"⚠️ 取消ASR任务失败: {e}")
                
                self.audio_processor.asr_tasks[client_id] = asyncio.create_task(self.delayed_asr_processing(client_id))
        except Exception as e:
            logger.error(f"❌ 处理音频数据失败: {e}")
    
    async def delayed_asr_processing(self, client_id: str):
        try:
            await asyncio.sleep(1.0)
            
            if client_id in self.audio_processor.last_audio_time:
                if self.audio_processor.is_silent(client_id, silence_threshold=1.0):
                    if self.audio_processor.has_sufficient_audio(client_id, threshold=3):
                        logger.info(f"🎤 语音结束，开始ASR处理")
                        await self.process_audio_for_asr(client_id)
                    else:
                        logger.info(f"⏳ 语音还在继续，继续等待...")
                        self.audio_processor.asr_tasks[client_id] = asyncio.create_task(self.delayed_asr_processing(client_id))
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"❌ 延迟ASR处理失败: {e}")
    
    async def process_audio_for_asr(self, client_id: str):
        try:
            logger.info(f"🎯 开始ASR识别")
            
            audio_data = self.audio_processor.get_audio_data(client_id)
            if not audio_data:
                logger.warning("⚠️ 音频缓冲区为空")
                return
            
            loop = asyncio.get_event_loop()
            asr_result = await loop.run_in_executor(self.executor, self.asr_module.recognize_speech, audio_data)
            
            if asr_result:
                await self.send_message(self.clients[client_id]['websocket'], {
                    'type': 'asr_result', 'text': asr_result, 'timestamp': time.time()
                })
                await self.process_llm_conversation(client_id, asr_result)
            else:
                await self.send_message(self.clients[client_id]['websocket'], {
                    'type': 'asr_error', 'message': '语音识别失败，请重试', 'timestamp': time.time()
                })
        except Exception as e:
            logger.error(f"❌ ASR处理失败: {e}")
    
    async def process_llm_conversation(self, client_id: str, recognized_text: str):
        try:
            logger.info(f"🤖 处理LLM对话: {recognized_text}")
            
            loop = asyncio.get_event_loop()
            llm_response = await loop.run_in_executor(self.executor, self.llm_module.ask_question, recognized_text, client_id)
            
            if llm_response:
                await self.send_message(self.clients[client_id]['websocket'], {
                    'type': 'llm_response', 'text': llm_response, 'timestamp': time.time()
                })
                await self.generate_tts_audio(client_id, llm_response)
        except Exception as e:
            logger.error(f"❌ LLM处理失败: {e}")
    
    async def generate_tts_audio(self, client_id: str, text: str):
        try:
            logger.info(f"🔊 生成TTS音频: {text}")
            
            loop = asyncio.get_event_loop()
            audio_data = await loop.run_in_executor(self.executor, self.tts_module.synthesize_speech, text)
            
            if audio_data:
                import base64
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                await self.send_message(self.clients[client_id]['websocket'], {
                    'type': 'tts_audio', 'audio': audio_base64, 'text': text, 'timestamp': time.time()
                })
        except Exception as e:
            logger.error(f"❌ TTS生成失败: {e}")
    
    async def handle_text_message(self, client_id: str, message_data: dict):
        text = message_data.get('text', '')
        if text:
            await self.process_llm_conversation(client_id, text)
    
    async def handle_tts_interruption(self, client_id: str, message_data: dict):
        try:
            self.audio_processor.clear_buffer(client_id)
            
            if client_id in self.audio_processor.asr_tasks and self.audio_processor.asr_tasks[client_id] is not None:
                try:
                    self.audio_processor.asr_tasks[client_id].cancel()
                except Exception as e:
                    logger.warning(f"⚠️ 取消ASR任务失败: {e}")
            
            await self.send_message(self.clients[client_id]['websocket'], {
                'type': 'interruption_confirmed', 'message': 'TTS播放已停止，准备处理新的语音输入', 'timestamp': time.time()
            })
            
            logger.info(f"🛑 客户端 {client_id} 的TTS播放已被打断")
        except Exception as e:
            logger.error(f"❌ 处理TTS打断失败: {e}")
    
    async def send_message(self, websocket, message_data: dict):
        try:
            import json
            message = json.dumps(message_data, ensure_ascii=False)
            await websocket.send(message)
        except Exception as e:
            logger.error(f"❌ 发送消息失败: {e}")
    
    async def cleanup_client(self, client_id: str):
        try:
            self.audio_processor.cleanup_client(client_id)
            self.llm_module.clear_conversation_history(client_id)
            
            if client_id in self.clients:
                del self.clients[client_id]
            
            logger.info(f"🧹 客户端 {client_id} 资源清理完成")
        except Exception as e:
            logger.error(f"❌ 清理客户端资源失败: {e}")

async def main():
    server = WebRTCServer()
    await server.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 服务器被用户中断")
    except Exception as e:
        logger.error(f"❌ 服务器运行异常: {e}")
