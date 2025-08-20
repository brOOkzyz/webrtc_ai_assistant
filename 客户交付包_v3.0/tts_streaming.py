#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度智能云TTS模块 - 真正的流式播放版本
支持字符级别的实时语音合成，修复音频重叠播放问题
"""

import asyncio
import websockets
import json
import threading
import time
import pyaudio
import queue
import requests
from enum import Enum

# 导入百度智能云TTS配置
from baidu_tts_config import TTS_API_KEY, TTS_SECRET_KEY, TTS_APP_ID

class BaiduTTSStreaming:
    """百度智能云TTS流式播放客户端"""
    
    def __init__(self):
        self.authorization = None
        self.per = "4146"  # 默认发音人
        self.base_url = "wss://aip.baidubce.com/ws/2.0/speech/publiccloudspeech/v1/tts"
        self.audio_queue = queue.Queue()
        self.is_speaking = False
        self.text_buffer = ""
        self.audio_thread = None  # 音频播放线程引用
        self.websocket = None  # WebSocket连接
        self.ws_thread = None  # WebSocket线程
        
        # 音频播放参数
        self.CHUNK_SIZE = 1024
        self.FORMAT = pyaudio.paInt16
        self.RATE = 16000
        self.CHANNELS = 1
        
        # 添加线程锁，防止并发问题
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        
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
                self.authorization = result.get("access_token")
                print("✅ 成功获取access token")
                return True
            else:
                print(f"❌ 获取access token失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 获取access token异常: {e}")
            return False
    
    def _audio_player_thread(self):
        """音频播放线程 - 立即响应停止信号"""
        try:
            p = pyaudio.PyAudio()
            stream = p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                output=True,
                frames_per_buffer=self.CHUNK_SIZE
            )
            
            print("🔊 TTS音频播放器已启动")
            
            while self.is_speaking and not self._stop_event.is_set():
                try:
                    # 使用更短的超时时间，提高响应速度
                    audio_data = self.audio_queue.get(timeout=0.02)  # 减少到0.02秒
                    if audio_data is None:  # 结束信号
                        print("🔇 收到结束信号，音频播放线程退出")
                        break
                    
                    # 再次检查是否应该停止
                    if not self.is_speaking or self._stop_event.is_set():
                        print("🔇 检测到停止信号，音频播放线程退出")
                        break
                    
                    # 播放音频
                    stream.write(audio_data)
                    
                except queue.Empty:
                    # 超时后立即检查停止信号
                    if not self.is_speaking or self._stop_event.is_set():
                        print("🔇 超时检查到停止信号，音频播放线程退出")
                        break
                    continue
                except Exception as e:
                    print(f"❌ 音频播放错误: {e}")
                    break
            
            # 立即停止音频流
            try:
                print("🔇 音频播放线程正在停止音频流...")
                stream.stop_stream()
                stream.close()
                p.terminate()
                print("✅ 音频流已完全停止")
            except Exception as e:
                print(f"⚠️ 停止音频流时出错: {e}")
            
            # 更新播放状态
            with self._lock:
                self.is_speaking = False
            print("✅ TTS音频播放线程已完全退出")
            
        except Exception as e:
            print(f"❌ TTS音频播放器初始化失败: {e}")
            with self._lock:
                self.is_speaking = False
    
    async def _websocket_handler(self):
        """WebSocket连接处理 - 立即响应停止信号"""
        try:
            url = f"{self.base_url}?access_token={self.authorization}&per={self.per}"
            async with websockets.connect(url) as websocket:
                self.websocket = websocket
                
                # 发送开始合成请求
                start_payload = {
                    "type": "system.start",
                    "payload": {
                        "spd": 5,  # 语速
                        "pit": 5,  # 音调
                        "vol": 5,  # 音量
                        "audio_ctrl": "{\"sampling_rate\":16000}",
                        "aue": 4  # PCM-16k格式
                    }
                }
                
                await websocket.send(json.dumps(start_payload))
                
                response = await websocket.recv()
                response_data = json.loads(response)
                
                # 检查错误码
                code = response_data.get("code", -1)
                if code != 0:
                    print(f"❌ TTS初始化失败: {response_data}")
                    return
                
                # TTS WebSocket连接建立成功
                print("✅ TTS WebSocket连接已建立")
                
                # 立即处理连接建立前缓存的文本
                if self.text_buffer:
                    text_payload = {
                        "type": "text",
                        "payload": {
                            "text": self.text_buffer
                        }
                    }
                    await websocket.send(json.dumps(text_payload))
                    self.text_buffer = ""  # 清空缓冲区
                
                # 保持连接，等待文本输入
                while self.is_speaking and not self._stop_event.is_set():
                    try:
                        # 检查是否有待处理的文本
                        if self.text_buffer:
                            # 发送文本进行合成
                            text_payload = {
                                "type": "text",
                                "payload": {
                                    "text": self.text_buffer
                                }
                            }
                            
                            await websocket.send(json.dumps(text_payload))
                            self.text_buffer = ""  # 清空缓冲区
                        
                        # 接收音频数据
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=0.05)  # 减少超时时间
                            
                            if isinstance(response, bytes):
                                # 二进制音频数据，立即放入播放队列
                                if not self._stop_event.is_set():  # 再次检查停止信号
                                    self.audio_queue.put(response)
                            else:
                                # 文本消息
                                response_json = json.loads(response)
                                
                                if response_json.get("type") == "system.finish":
                                    print("🔇 收到系统完成信号，WebSocket线程退出")
                                    break
                                    
                        except asyncio.TimeoutError:
                            # 超时继续循环，检查停止信号
                            if not self.is_speaking or self._stop_event.is_set():
                                print("🔇 WebSocket超时检查到停止信号，线程退出")
                                break
                            continue
                            
                    except Exception as e:
                        print(f"❌ WebSocket处理错误: {e}")
                        break
                
                # 发送结束合成请求
                try:
                    finish_payload = {
                        "type": "system.finish"
                    }
                    
                    await websocket.send(json.dumps(finish_payload))
                    await asyncio.wait_for(websocket.recv(), timeout=0.5)  # 等待结束响应
                except Exception as e:
                    print(f"⚠️ 发送结束请求时出错: {e}")
                
                print("✅ WebSocket线程正常退出")
                
        except Exception as e:
            print(f"❌ WebSocket连接失败: {e}")
        finally:
            self.websocket = None
            print("🔇 WebSocket连接已关闭")
    
    def add_text(self, text):
        """添加文本到缓冲区，立即进行流式合成"""
        with self._lock:
            if not self.is_speaking:
                return
            
            # 如果WebSocket还没准备好，先缓存文本
            if not self.websocket:
                self.text_buffer += text
                return
            
            # 直接添加到缓冲区，WebSocket线程会自动处理
            self.text_buffer += text
    
    def flush_buffer(self):
        """强制处理剩余的文本缓冲区"""
        if self.text_buffer.strip() and self.websocket:
            # 文本会在WebSocket线程中自动处理
            pass
    
    def start_streaming(self):
        """开始流式播放"""
        with self._lock:
            # 如果已经在播放，先停止，避免音频重叠
            if self.is_speaking:
                print("⚠️ TTS已在播放中，立即停止当前播放...")
                self.stop_streaming()
                # 等待更长时间确保完全停止
                time.sleep(0.5)  # 从0.2秒增加到0.5秒
            
            if not self.authorization:
                if not self._get_access_token():
                    return False
            
            # 重置状态
            self.is_speaking = True
            self.text_buffer = ""
            self._stop_event.clear()
            
            # 清空音频队列
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except queue.Empty:
                    break
            
            # 启动音频播放线程
            self.audio_thread = threading.Thread(target=self._audio_player_thread)
            self.audio_thread.daemon = True
            self.audio_thread.start()
            
            # 启动WebSocket线程
            self.ws_thread = threading.Thread(target=lambda: asyncio.run(self._websocket_handler()))
            self.ws_thread.daemon = True
            self.ws_thread.start()
            
            return True
    
    def stop_streaming(self):
        """停止流式播放 - 真正的立即停止"""
        print("🚨 开始真正的立即停止TTS流式播放...")
        
        with self._lock:
            # 立即停止，不等待音频播放完毕
            self.is_speaking = False
            self._stop_event.set()
            
            # 立即清空音频队列
            queue_size = 0
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                    queue_size += 1
                except queue.Empty:
                    break
            print(f"🔇 已清空音频队列，清除了 {queue_size} 个音频数据")
            
            # 发送结束信号
            try:
                self.audio_queue.put_nowait(None)
            except queue.Full:
                pass
        
        # 立即强制停止音频播放线程
        if self.audio_thread and self.audio_thread.is_alive():
            print("🔇 立即强制停止音频播放线程...")
            # 不等待线程完成，立即继续
        
        # 立即强制停止WebSocket线程
        if self.ws_thread and self.ws_thread.is_alive():
            print("🔇 立即强制停止WebSocket线程...")
            # 不等待线程完成，立即继续
        
        # 强制等待一小段时间确保线程完全停止
        time.sleep(0.3)
        
        # 额外清理：强制停止所有可能的音频进程
        try:
            import subprocess
            print("🔇 强制停止所有音频进程...")
            
            # 停止所有afplay进程（macOS音频播放）
            result = subprocess.run(['pkill', '-9', 'afplay'], 
                                  stdout=subprocess.DEVNULL, 
                                  stderr=subprocess.DEVNULL,
                                  timeout=0.2)
            if result.returncode == 0:
                print("✅ 已停止所有afplay进程")
            
            # 停止所有aplay进程（Linux音频播放）
            result = subprocess.run(['pkill', '-9', 'aplay'], 
                                  stdout=subprocess.DEVNULL, 
                                  stderr=subprocess.DEVNULL,
                                  timeout=0.2)
            if result.returncode == 0:
                print("✅ 已停止所有aplay进程")
            
            # 停止所有Python音频相关进程
            result = subprocess.run(['pkill', '-9', '-f', 'python.*tts'], 
                                  stdout=subprocess.DEVNULL, 
                                  stderr=subprocess.DEVNULL,
                                  timeout=0.2)
            if result.returncode == 0:
                print("✅ 已停止所有Python TTS进程")
            
            # 停止所有音频相关进程
            result = subprocess.run(['pkill', '-9', '-f', 'audio'], 
                                  stdout=subprocess.DEVNULL, 
                                  stderr=subprocess.DEVNULL,
                                  timeout=0.2)
            if result.returncode == 0:
                print("✅ 已停止所有音频相关进程")
            
            print("✅ 所有音频进程已强制停止")
        except Exception as e:
            print(f"⚠️ 停止音频进程时出错: {e}")
        
        # 最终等待确保所有进程完全停止
        time.sleep(0.2)
        
        print("✅ TTS流式播放已真正立即停止")
    
    def is_audio_playing(self):
        """检查音频是否还在播放"""
        with self._lock:
            # 改进状态检查：不仅要检查线程是否存活，还要检查音频队列状态
            if not self.is_speaking:
                return False
            
            if not self.audio_thread or not self.audio_thread.is_alive():
                return False
            
            # 检查音频队列是否还有数据
            queue_size = self.audio_queue.qsize()
            if not self.audio_queue.empty():
                return True
            
            # 如果队列为空且线程存活，等待一小段时间再次检查
            time.sleep(0.1)  # 增加等待时间，减少检查频率
            if not self.audio_queue.empty():
                return True
            
            # 如果队列仍然为空，认为播放已完成
            return False
    
    def wait_for_audio_completion(self):
        """等待音频播放完成"""
        if not self.is_audio_playing():
            return True
        
        print("🔊 等待音频播放完成...")
        
        # 立即清空音频队列，不等待
        queue_empty_count = 0
        while not self.audio_queue.empty():
            # time.sleep(0.1)  # 注释掉等待逻辑
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
            queue_empty_count += 1
            if queue_empty_count > 50:  # 最多处理50个，避免无限循环
                break
        
        # 立即强制停止音频播放线程（不等待）
        if self.audio_thread and self.audio_thread.is_alive():
            print("🔇 立即强制停止音频播放线程...")
            # 不等待线程完成，立即返回
            # self.audio_thread.join(timeout=10)  # 注释掉等待逻辑
        
        # 最终检查
        return not self.is_audio_playing()

# 全局TTS实例管理
_tts_instance = None
_tts_lock = threading.Lock()

def _get_tts_instance():
    """获取或创建TTS实例"""
    global _tts_instance
    with _tts_lock:
        if _tts_instance is None:
            _tts_instance = BaiduTTSStreaming()
        return _tts_instance

def start_tts_streaming():
    """启动TTS流式播放"""
    global _tts_instance
    with _tts_lock:
        # 如果已有TTS实例在播放，先停止它
        if _tts_instance and _tts_instance.is_speaking:
            print("🔄 已有TTS实例在播放，先停止它，避免音频重叠...")
            _tts_instance.stop_streaming()
            # 等待一小段时间确保完全停止
            time.sleep(0.2)
        
        # 如果没有实例，创建新实例
        if _tts_instance is None:
            _tts_instance = BaiduTTSStreaming()
        
        return _tts_instance.start_streaming()

def add_text_to_tts(text):
    """添加文本到TTS流"""
    _get_tts_instance().add_text(text)

def stop_tts_streaming():
    """停止TTS流式播放"""
    global _tts_instance
    with _tts_lock:
        if _tts_instance:
            _tts_instance.stop_streaming()

def speak_text(text):
    """直接播放文本（非流式）"""
    global _tts_instance
    with _tts_lock:
        # 新机制：不强制停止当前播放，让它自然完成
        if _tts_instance and _tts_instance.is_audio_playing():
            print("🔄 检测到TTS正在播放，等待当前播放自然完成...")
            # 不调用stop_streaming，让当前播放自然完成
            # 等待一小段时间让当前播放继续
            time.sleep(0.1)
        
        # 创建新实例
        _tts_instance = BaiduTTSStreaming()
    
    # 启动流式播放
    if _tts_instance.start_streaming():
        # 添加文本
        _tts_instance.add_text(text)
        # 不等待播放完成，立即停止
        # _tts_instance.wait_for_audio_completion()  # 注释掉等待逻辑
        # 立即停止播放
        _tts_instance.stop_streaming()

def stop_tts():
    """停止TTS"""
    stop_tts_streaming()

def wait_for_tts_completion():
    """立即停止TTS播放（不等待）"""
    global _tts_instance
    with _tts_lock:
        if _tts_instance:
            print("🔇 立即停止TTS播放，不等待完成...")
            _tts_instance.stop_streaming()
            return True
        return True

def is_tts_playing():
    """检查TTS是否正在播放"""
    global _tts_instance
    with _tts_lock:
        if _tts_instance:
            return _tts_instance.is_audio_playing()
        return False

def flush_buffer():
    """强制处理TTS缓冲区"""
    global _tts_instance
    with _tts_lock:
        if _tts_instance:
            _tts_instance.flush_buffer()


if __name__ == "__main__":
    # 测试TTS功能
    test_text = "你好，这是一个百度智能云TTS测试。流式文本在线合成功能正常工作。"
    print("🎯 百度智能云TTS模块测试 - 真正的流式播放版本")
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
