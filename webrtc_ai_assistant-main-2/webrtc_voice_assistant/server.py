#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebRTC语音助手服务端
"""

import asyncio
import websockets
import logging
import time
import uuid
import json
from concurrent.futures import ThreadPoolExecutor

from asr_module import ASRModule
from llm_module import LLMModule
from tts_module import TTSModule
from audio_processor import AudioProcessor

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
    """WebRTC语音助手服务器"""
    
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        
        self.asr_module = ASRModule()
        self.llm_module = LLMModule()
        self.tts_module = TTSModule()
        self.audio_processor = AudioProcessor(buffer_size=50)
        
        self.clients = {}
        self.executor = ThreadPoolExecutor(max_workers=20)
        
    async def start(self):
        """启动WebRTC服务器"""
        logger.info(f"启动WebRTC服务器 {self.host}:{self.port}")
        
        try:
            async with websockets.serve(self.handle_client, self.host, self.port):
                logger.info(f"WebRTC服务器启动成功")
                logger.info(f"监听地址: {self.host}:{self.port}")
                await asyncio.Future()
                
        except Exception as e:
            logger.error(f"服务器启动失败: {e}")
            raise
    
    async def handle_client(self, websocket, path):
        """处理新客户端连接"""
        client_id = str(uuid.uuid4())
        
        self.clients[client_id] = {
            'websocket': websocket, 
            'id': client_id, 
            'connected_at': time.time(),
            'status': 'connected'
        }
        
        logger.info(f"客户端 {client_id} 已连接")
        
        try:
            async for message in websocket:
                await self.process_message(client_id, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"客户端 {client_id} 连接已关闭")
        except Exception as e:
            logger.error(f"处理客户端 {client_id} 消息时出错: {e}")
        finally:
            await self.cleanup_client(client_id)
    
    async def process_message(self, client_id, message):
        """处理客户端消息"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'audio':
                await self.process_audio(client_id, data)
            elif msg_type == 'text':
                await self.process_text(client_id, data)
                
        except json.JSONDecodeError:
            logger.error(f"无效的JSON消息: {message}")
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
    
    async def process_audio(self, client_id, data):
        """处理音频数据"""
        audio_data = data.get('audio')
        if not audio_data:
            return
            
        # 处理音频数据
        processed_audio = await self.audio_processor.process_audio(audio_data)
        
        # 语音识别
        text = await self.asr_module.recognize(processed_audio)
        if text:
            # 发送识别结果给客户端
            await self.send_to_client(client_id, {
                'type': 'asr_result',
                'text': text
            })
            
            # 生成回复
            response = await self.llm_module.chat(text)
            if response:
                # 语音合成
                audio_response = await self.tts_module.synthesize(response)
                if audio_response:
                    await self.send_to_client(client_id, {
                        'type': 'tts_result',
                        'audio': audio_response,
                        'text': response
                    })
    
    async def process_text(self, client_id, data):
        """处理文本消息"""
        text = data.get('text')
        if not text:
            return
            
        # 生成回复
        response = await self.llm_module.chat(text)
        if response:
            # 语音合成
            audio_response = await self.tts_module.synthesize(response)
            if audio_response:
                await self.send_to_client(client_id, {
                    'type': 'tts_result',
                    'audio': audio_response,
                    'text': response
                })
    
    async def send_to_client(self, client_id, data):
        """发送数据给客户端"""
        if client_id in self.clients:
            try:
                await self.clients[client_id]['websocket'].send(json.dumps(data))
            except Exception as e:
                logger.error(f"发送数据给客户端 {client_id} 失败: {e}")
    
    async def cleanup_client(self, client_id):
        """清理客户端连接"""
        if client_id in self.clients:
            del self.clients[client_id]
            logger.info(f"客户端 {client_id} 已清理")

async def main():
    """主函数"""
    server = WebRTCServer()
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
