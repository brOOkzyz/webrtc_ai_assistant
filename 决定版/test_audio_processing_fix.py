#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试音频数据不足问题的修复
验证系统能够处理少量音频数据
"""

import time
import logging
from audio_processor import AudioProcessor
from config import ASR_PROCESSING_CONFIG

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def test_audio_processing_fix():
    """测试音频数据不足问题的修复"""
    print("🧪 测试音频数据不足问题的修复")
    print("=" * 50)
    
    # 创建音频处理器
    processor = AudioProcessor(buffer_size=50)
    client_id = "test_client_001"
    
    print(f"📋 当前配置:")
    print(f"  - 最小音频块数: {ASR_PROCESSING_CONFIG['MIN_AUDIO_CHUNKS']}")
    print(f"  - 最小音频字节: {ASR_PROCESSING_CONFIG['MIN_AUDIO_BYTES']}")
    print(f"  - 静音等待时间: {ASR_PROCESSING_CONFIG['SILENCE_WAIT_TIME']}秒")
    print()
    
    # 测试1: 单个音频块
    print("🔍 测试1: 单个音频块")
    test_audio = b"test_audio_data" * 10  # 160字节
    processor.add_audio_data(client_id, test_audio)
    
    buffer_size = processor.get_audio_buffer_size(client_id)
    has_sufficient = processor.has_sufficient_audio(client_id, threshold=1)
    
    print(f"  - 音频块数: {buffer_size}")
    print(f"  - 音频字节: {len(test_audio)}")
    print(f"  - 数据充足: {has_sufficient}")
    print(f"  - 结果: {'✅ 通过' if has_sufficient else '❌ 失败'}")
    print()
    
    # 测试2: 少量音频数据
    print("🔍 测试2: 少量音频数据")
    small_audio = b"small"  # 5字节
    processor.add_audio_data(client_id, small_audio)
    
    buffer_size = processor.get_audio_buffer_size(client_id)
    has_sufficient = processor.has_sufficient_audio(client_id, threshold=1)
    
    print(f"  - 音频块数: {buffer_size}")
    print(f"  - 音频字节: {len(small_audio)}")
    print(f"  - 数据充足: {has_sufficient}")
    print(f"  - 结果: {'✅ 通过' if has_sufficient else '❌ 失败'}")
    print()
    
    # 测试3: 静音检测
    print("🔍 测试3: 静音检测")
    print(f"  - 当前时间: {time.time()}")
    print(f"  - 最后音频时间: {processor.last_audio_time.get(client_id, 'None')}")
    
    # 等待静音时间
    wait_time = ASR_PROCESSING_CONFIG['SILENCE_WAIT_TIME']
    print(f"  - 等待静音时间: {wait_time}秒")
    time.sleep(wait_time + 0.1)
    
    is_silent = processor.is_silent(client_id, silence_threshold=wait_time)
    print(f"  - 是否静音: {is_silent}")
    print(f"  - 结果: {'✅ 通过' if is_silent else '❌ 失败'}")
    print()
    
    # 测试4: 获取音频数据
    print("🔍 测试4: 获取音频数据")
    audio_data = processor.get_audio_data(client_id)
    if audio_data:
        print(f"  - 获取到音频数据: {len(audio_data)} 字节")
        print(f"  - 结果: ✅ 通过")
    else:
        print(f"  - 未获取到音频数据")
        print(f"  - 结果: ❌ 失败")
    print()
    
    # 测试5: 缓冲区状态
    print("🔍 测试5: 缓冲区状态")
    buffer_size = processor.get_audio_buffer_size(client_id)
    print(f"  - 当前缓冲区大小: {buffer_size}")
    print(f"  - 结果: {'✅ 通过' if buffer_size == 0 else '❌ 失败'}")
    print()
    
    print("🎉 测试完成！")
    print("💡 如果所有测试都通过，说明音频数据不足问题已修复")
    print("💡 现在系统应该能够处理少量音频数据，不会无限等待")

if __name__ == "__main__":
    test_audio_processing_fix()
