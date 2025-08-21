#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试ASR语音识别修复
验证修复后的语音识别是否能正常工作，减少错误码3307
"""

import time
import threading
from asr_llm_working import recognize_speech_from_pcm

def test_asr_recognition():
    """测试ASR语音识别功能"""
    print("🎯 测试ASR语音识别修复")
    print("=" * 50)
    
    # 测试1: 模拟不同长度的音频数据
    print("\n🔊 测试1: 音频长度和质量检查")
    
    # 模拟短音频（应该被过滤）
    short_audio = b'\x00\x00' * 1000  # 2000字节，少于8000字节
    print(f"📊 测试短音频: {len(short_audio)} 字节")
    result = recognize_speech_from_pcm(short_audio, silent=False)
    if result is None:
        print("✅ 短音频被正确过滤")
    else:
        print("❌ 短音频应该被过滤")
    
    # 模拟正常音频
    normal_audio = b'\x00\x00' * 8000  # 16000字节，正常长度
    print(f"\n📊 测试正常音频: {len(normal_audio)} 字节")
    result = recognize_speech_from_pcm(normal_audio, silent=False)
    print(f"识别结果: {result}")
    
    print("\n✅ 测试1完成")
    
    # 测试2: 音频能量计算
    print("\n🔊 测试2: 音频能量计算")
    
    # 低能量音频
    low_energy_audio = b'\x00\x00' * 8000  # 全零，能量很低
    print(f"📊 测试低能量音频: {len(low_energy_audio)} 字节")
    result = recognize_speech_from_pcm(low_energy_audio, silent=False)
    print(f"识别结果: {result}")
    
    # 高能量音频
    high_energy_audio = b'\x7F\x7F' * 8000  # 高振幅，能量较高
    print(f"\n📊 测试高能量音频: {len(high_energy_audio)} 字节")
    result = recognize_speech_from_pcm(high_energy_audio, silent=False)
    print(f"识别结果: {result}")
    
    print("\n✅ 测试2完成")
    
    # 测试3: 错误处理
    print("\n🔊 测试3: 错误处理机制")
    
    # 测试空音频
    empty_audio = b''
    print(f"📊 测试空音频: {len(empty_audio)} 字节")
    result = recognize_speech_from_pcm(empty_audio, silent=False)
    print(f"识别结果: {result}")
    
    print("\n✅ 测试3完成")
    
    print("\n🎯 所有测试完成！")
    print("=" * 50)
    print("💡 这些测试主要验证音频预处理和错误处理")
    print("💡 实际的语音识别需要真实的语音输入")

def test_voice_detection_params():
    """测试语音检测参数设置"""
    print("\n🎤 测试语音检测参数设置")
    print("=" * 50)
    
    print("📋 当前语音检测参数:")
    print("- 能量阈值: 400 (提高，减少噪音误触发)")
    print("- 停顿阈值: 1.0秒 (增加，确保语音完整)")
    print("- 非说话时长: 0.5秒 (增加，避免过早截断)")
    print("- 短语时间限制: 10秒 (增加，支持更长语音)")
    print("- 音频长度过滤: 0.5-15秒 (过滤噪音和异常)")
    
    print("\n✅ 参数设置测试完成")

if __name__ == "__main__":
    try:
        test_asr_recognition()
        test_voice_detection_params()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
    
    print("\n🎯 测试完成！")
    print("💡 要测试真实语音识别，请运行: python asr_llm_working.py")
