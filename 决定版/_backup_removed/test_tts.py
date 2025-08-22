#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTS模块测试脚本
"""

import logging
from tts_module import speak_text, stop_tts

def main():
    """测试TTS功能"""
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    print("🎯 TTS模块测试")
    print("=" * 50)
    
    # 测试文本
    test_texts = [
        "你好，这是一个TTS测试。",
        "百度智能云流式文本在线合成功能正常工作。",
        "现在可以听到语音输出了。"
    ]
    
    try:
        for i, text in enumerate(test_texts, 1):
            print(f"\n🔊 测试 {i}: {text}")
            speak_text(text)
            print(f"✅ 测试 {i} 完成")
            
            # 等待一下再播放下一个
            import time
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 测试被中断")
    except Exception as e:
        print(f"❌ TTS测试失败: {e}")
    finally:
        stop_tts()
        print("\n🎯 TTS测试完成")

if __name__ == "__main__":
    main()
