#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版 ASR + LLM 串联脚本
一键实现：录音 → 识别 → LLM对话
"""

import threading
import time
import json
import logging
import pyaudio
import websocket
import queue
import requests
import os
import sys

# 导入配置
sys.path.insert(0, os.path.dirname(__file__))
from config import API_KEY, BASE_URL, DEFAULT_MODEL
from 流式_副本2.const import APPID, APPKEY, DEV_PID, URI

# 音频设置
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = int(RATE / 100)

# 全局变量
audio_queue = queue.Queue()
asr_text = ""
is_recording = False


def record_audio():
    """录制音频到队列"""
    global is_recording
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    
    print("🎤 正在录音... 按 Enter 键停止")
    
    try:
        while is_recording:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_queue.put(data)
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


def send_audio_to_asr():
    """将音频发送到ASR服务进行识别"""
    global asr_text
    
    # 连接WebSocket
    uri = URI + "?sn=" + str(int(time.time() * 1000))
    ws = websocket.WebSocketApp(uri,
                                on_open=send_start_frame,
                                on_message=handle_asr_response,
                                on_error=lambda ws, err: print(f"ASR错误: {err}"),
                                on_close=lambda ws: print("ASR连接关闭"))
    
    # 在后台运行WebSocket
    ws_thread = threading.Thread(target=ws.run_forever)
    ws_thread.daemon = True
    ws_thread.start()
    
    # 等待连接建立
    time.sleep(1)
    
    # 发送音频数据
    print("🔄 正在识别语音...")
    while not audio_queue.empty():
        try:
            audio_data = audio_queue.get(timeout=0.1)
            ws.send(audio_data, websocket.ABNF.OPCODE_BINARY)
            time.sleep(0.01)  # 控制发送速度
        except queue.Empty:
            break
    
    # 发送结束信号
    send_finish_frame(ws)
    
    # 等待识别完成
    time.sleep(2)
    ws.close()
    
    return asr_text.strip()


def send_start_frame(ws):
    """发送开始帧"""
    start_data = {
        "type": "START",
        "data": {
            "appid": APPID,
            "appkey": APPKEY,
            "dev_pid": DEV_PID,
            "cuid": "user123",
            "sample": RATE,
            "format": "pcm"
        }
    }
    ws.send(json.dumps(start_data))


def send_finish_frame(ws):
    """发送结束帧"""
    finish_data = {"type": "FINISH"}
    ws.send(json.dumps(finish_data))


def handle_asr_response(ws, message):
    """处理ASR响应"""
    global asr_text
    try:
        data = json.loads(message)
        if 'result' in data:
            asr_text += data['result']
            print(f"\r🎯 识别中: {asr_text}", end='', flush=True)
    except:
        pass


def ask_llm(question):
    """向LLM提问"""
    print(f"\n🤖 正在询问LLM...")
    print(f"📝 问题: {question}")
    
    url = f"{BASE_URL}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": DEFAULT_MODEL,
        "messages": [{"role": "user", "content": question}],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        else:
            return "抱歉，没有收到有效回复。"
            
    except Exception as e:
        return f"LLM请求失败: {e}"


def main():
    """主函数"""
    global is_recording, asr_text
    
    print("🎯 ASR + LLM 串联系统")
    print("=" * 50)
    print("流程: 录音 → 语音识别 → LLM对话")
    print("=" * 50)
    
    while True:
        print("\n🎯 请选择:")
        print("1. 🎤 开始录音并对话")
        print("2. 🚪 退出")
        
        choice = input("请输入选项 (1-2): ").strip()
        
        if choice == "1":
            # 重置状态
            asr_text = ""
            is_recording = True
            
            # 启动录音线程
            record_thread = threading.Thread(target=record_audio)
            record_thread.daemon = True
            record_thread.start()
            
            # 等待用户停止录音
            input()
            is_recording = False
            
            # 等待录音线程结束
            record_thread.join()
            
            # 进行语音识别
            recognized_text = send_audio_to_asr()
            
            if recognized_text:
                print(f"\n✅ 识别结果: {recognized_text}")
                
                # 询问LLM
                llm_response = ask_llm(recognized_text)
                
                print(f"\n🤖 LLM回复:")
                print("=" * 60)
                print(llm_response)
                print("=" * 60)
            else:
                print("❌ 语音识别失败，请重试")
                
        elif choice == "2":
            print("👋 再见！")
            break
        else:
            print("❌ 无效选项，请输入 1-2")


if __name__ == "__main__":
    main()
