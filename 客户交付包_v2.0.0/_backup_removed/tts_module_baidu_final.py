#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度智能云流式文本在线合成（TTS）模块 - 最终版本
根据官方API文档实现：https://cloud.baidu.com/doc/SPEECH/s/lm5xd63rn
"""

import json
import logging
import threading
import time
import websocket
import pyaudio
import queue
import os
import sys
import requests

# 导入百度智能云TTS配置
try:
    from baidu_tts_config import TTS_API_KEY, TTS_SECRET_KEY, TTS_APP_ID
except ImportError:
    print("❌ 请先配置 baidu_tts_config.py 文件")
    print("📝 填入你的百度智能云TTS服务的API Key和Secret Key")
    sys.exit(1)

logger = logging.getLogger()

# TTS配置 - 根据百度智能云API文档
TTS_URI = "wss://tsn.baidu.com/text2audio"
TTS_RATE = 16000    # 采样率
TTS_CHANNELS = 1    # 声道数
TTS_BIT = 16        # 位深

# 音频播放参数
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16

class BaiduTTSFinal:
    """百度智能云流式TTS客户端 - 最终版本"""
    
    def __init__(self):
        self.ws = None
        self.audio_queue = queue.Queue()
        self.is_speaking = False
        self.access_token = None
        
    def _get_access_token(self):
        """获取百度智能云access token"""
        try:
            url = "https://aip.baidubce.com/oauth/2.0/token"
            params = {
                "grant_type": "client_credentials",
                "client_id": TTS_API_KEY,
                "client_secret": TTS_SECRET_KEY
            }
            
            response = requests.post(url, data=params)
            if response.status_code == 200:
                result = response.json()
                self.access_token = result.get("access_token")
                logger.info("成功获取access token")
                return True
            else:
                logger.error(f"获取access token失败: {response.status_code}")
                logger.error(f"错误信息: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"获取access token异常: {e}")
            return False
    
    def _on_tts_open(self, ws):
        """TTS WebSocket连接打开回调"""
        logger.info("TTS WebSocket连接已建立")
        
        def run():
            try:
                # 根据API文档，发送开始帧
                start_frame = {
                    "type": "START",
                    "data": {
                        "appid": TTS_APP_ID,
                        "access_token": self.access_token,
                        "format": "pcm",  # 音频格式
                        "rate": TTS_RATE,  # 采样率
                        "channels": TTS_CHANNELS,  # 声道数
                        "bit": TTS_BIT,  # 位深
                        "lang": "zh",  # 中文
                        "voice": 0,    # 发音人：0-4
                        "speed": 5,    # 语速：0-15
                        "volume": 5,   # 音量：0-15
                        "pitch": 5     # 音调：0-15
                    }
                }
                ws.send(json.dumps(start_frame))
                logger.info("TTS开始帧已发送")
                
            except Exception as e:
                logger.error(f"TTS开始帧发送失败: {e}")
        
        threading.Thread(target=run).start()
    
    def _on_tts_message(self, ws, message):
        """TTS WebSocket消息回调"""
        try:
            if isinstance(message, bytes):
                # 二进制音频数据
                self.audio_queue.put(message)
                logger.debug(f"收到音频数据: {len(message)} bytes")
            else:
                # 文本消息
                data = json.loads(message)
                if data.get('type') == 'system.finished':
                    logger.info("TTS合成完成")
                    # 发送结束信号
                    self.audio_queue.put(None)
                elif data.get('type') == 'error':
                    logger.error(f"TTS错误: {data}")
                    
        except Exception as e:
            logger.error(f"TTS消息处理失败: {e}")
    
    def _on_tts_error(self, ws, error):
        """TTS WebSocket错误回调"""
        logger.error(f"TTS WebSocket错误: {error}")
    
    def _on_tts_close(self, ws, close_status_code=None, close_msg=None):
        """TTS WebSocket关闭回调"""
        logger.info("TTS WebSocket连接已关闭")
    
    def _audio_player_thread(self):
        """音频播放线程"""
        try:
            p = pyaudio.PyAudio()
            stream = p.open(
                format=FORMAT,
                channels=TTS_CHANNELS,
                rate=TTS_RATE,
                output=True,
                frames_per_buffer=CHUNK_SIZE
            )
            
            logger.info("开始播放TTS音频...")
            
            while self.is_speaking:
                try:
                    audio_data = self.audio_queue.get(timeout=0.1)
                    if audio_data is None:  # 结束信号
                        break
                    
                    # 播放音频
                    stream.write(audio_data)
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"音频播放错误: {e}")
                    break
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            logger.info("TTS音频播放完成")
            
        except Exception as e:
            logger.error(f"音频播放器初始化失败: {e}")
    
    def synthesize_and_play(self, text):
        """合成文本并播放音频"""
        if not text or not text.strip():
            logger.warning("文本为空，跳过TTS")
            return
        
        logger.info(f"开始TTS合成: {text}")
        
        # 获取access token
        if not self.access_token:
            if not self._get_access_token():
                logger.error("无法获取access token，TTS失败")
                return
        
        # 重置状态
        self.is_speaking = True
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        
        # 建立TTS WebSocket连接
        self.ws = websocket.WebSocketApp(
            TTS_URI,
            on_open=self._on_tts_open,
            on_message=self._on_tts_message,
            on_error=self._on_tts_error,
            on_close=self._on_tts_close
        )
        
        # 启动TTS连接
        tts_thread = threading.Thread(target=self.ws.run_forever)
        tts_thread.daemon = True
        tts_thread.start()
        
        # 等待连接建立
        time.sleep(1)
        
        # 发送文本数据
        try:
            text_frame = {
                "type": "TEXT",
                "data": {
                    "text": text
                }
            }
            self.ws.send(json.dumps(text_frame))
            logger.info("TTS文本帧已发送")
            
            # 发送结束帧
            finish_frame = {
                "type": "FINISH"
            }
            self.ws.send(json.dumps(finish_frame))
            logger.info("TTS结束帧已发送")
            
        except Exception as e:
            logger.error(f"TTS数据发送失败: {e}")
            return
        
        # 启动音频播放线程
        audio_thread = threading.Thread(target=self._audio_player_thread)
        audio_thread.daemon = True
        audio_thread.start()
        
        # 等待音频播放完成
        audio_thread.join()
        
        # 关闭WebSocket连接
        if self.ws:
            self.ws.close()
        
        self.is_speaking = False
        logger.info("TTS合成和播放完成")
    
    def stop(self):
        """停止TTS"""
        self.is_speaking = False
        if self.ws:
            self.ws.close()
        # 清空音频队列
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break


# 全局TTS实例
tts_client = BaiduTTSFinal()


def speak_text(text):
    """便捷函数：合成并播放文本"""
    if not text or not text.strip():
        return
    
    print(f"\n🔊 TTS合成中: {text}")
    tts_client.synthesize_and_play(text)


def stop_tts():
    """停止TTS"""
    tts_client.stop()


if __name__ == "__main__":
    # 测试TTS功能
    logging.basicConfig(level=logging.INFO)
    
    test_text = "你好，这是一个百度智能云TTS测试。流式文本在线合成功能正常工作。"
    print("🎯 百度智能云TTS模块测试 - 最终版本")
    print("=" * 50)
    
    try:
        speak_text(test_text)
    except KeyboardInterrupt:
        print("\n👋 测试被中断")
        stop_tts()
    except Exception as e:
        print(f"❌ TTS测试失败: {e}")
        stop_tts()
    
    print("\n🎯 TTS测试完成")
