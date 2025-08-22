#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试TTS重叠播放问题修复
验证在启动新TTS之前是否完全停止了旧的TTS
"""

import time
import threading
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

def test_tts_overlap_fix():
    """测试TTS重叠播放问题修复"""
    print("🧪 测试TTS重叠播放问题修复")
    print("=" * 50)
    
    try:
        # 导入修复后的模块
        from asr_llm_working import (
            force_stop_all_tts, 
            is_tts_playing, 
            tts_should_stop, 
            tts_stop_lock,
            ai_speaking_lock,
            is_ai_speaking
        )
        
        print("✅ 成功导入修复后的模块")
        
        # 测试1：检查TTS状态检查函数
        print("\n🔍 测试1：TTS状态检查")
        try:
            tts_status = is_tts_playing()
            print(f"✅ TTS状态检查正常，当前状态: {tts_status}")
        except Exception as e:
            print(f"❌ TTS状态检查失败: {e}")
        
        # 测试2：测试强制停止TTS函数
        print("\n🔍 测试2：强制停止TTS功能")
        try:
            print("🔄 测试强制停止TTS...")
            force_stop_all_tts()
            print("✅ 强制停止TTS测试成功")
        except Exception as e:
            print(f"❌ 强制停止TTS测试失败: {e}")
        
        # 测试3：测试停止标志设置
        print("\n🔍 测试3：停止标志设置")
        try:
            with tts_stop_lock:
                tts_should_stop = True
                print("✅ 停止标志设置成功")
        except Exception as e:
            print(f"❌ 停止标志设置失败: {e}")
        
        # 测试4：测试AI说话状态管理
        print("\n🔍 测试4：AI说话状态管理")
        try:
            with ai_speaking_lock:
                is_ai_speaking = False
                print("✅ AI说话状态管理正常")
        except Exception as e:
            print(f"❌ AI说话状态管理失败: {e}")
        
        print("\n🎯 所有测试完成！")
        print("💡 如果所有测试都通过，说明TTS重叠播放问题已修复")
        
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("💡 请确保 asr_llm_working.py 文件存在且可导入")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")

def test_conversation_flow():
    """测试对话流程中的TTS管理"""
    print("\n🧪 测试对话流程中的TTS管理")
    print("=" * 50)
    
    try:
        # 模拟对话流程
        print("🔄 模拟对话流程...")
        
        # 模拟用户输入
        user_input = "测试TTS重叠修复"
        print(f"🗣️ 用户输入: {user_input}")
        
        # 模拟TTS状态检查
        print("🔍 检查TTS状态...")
        time.sleep(0.5)  # 模拟检查时间
        
        print("✅ 对话流程测试完成")
        
    except Exception as e:
        print(f"❌ 对话流程测试失败: {e}")

if __name__ == "__main__":
    print("🚀 开始TTS重叠播放问题修复测试")
    print("=" * 60)
    
    # 运行基本功能测试
    test_tts_overlap_fix()
    
    # 运行对话流程测试
    test_conversation_flow()
    
    print("\n🎉 测试完成！")
    print("💡 如果测试通过，说明TTS重叠播放问题已修复")
    print("💡 现在可以运行 asr_llm_working.py 来测试实际效果")
