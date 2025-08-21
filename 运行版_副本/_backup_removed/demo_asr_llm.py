#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASR + LLM 串联系统演示脚本
展示完整的语音交互流程
"""

import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

def demo_workflow():
    """演示工作流程"""
    print("🎯 ASR + LLM 串联系统演示")
    print("=" * 60)
    print("完整流程: 录音 → 语音识别 → LLM对话 → 显示回复")
    print("=" * 60)
    
    print("\n📋 工作流程说明:")
    print("1. 🎤 用户启动录音")
    print("2. 🎙️ 对着麦克风说话")
    print("3. ⏹️ 按Enter键停止录音")
    print("4. 🔄 系统自动进行语音识别")
    print("5. 📝 显示识别结果")
    print("6. 🤖 自动发送给LLM")
    print("7. 💬 显示LLM的完整回复")
    
    print("\n💡 使用建议:")
    print("- 选择安静的环境进行录音")
    print("- 说话清晰，语速适中")
    print("- 说完完整句子再停止录音")
    print("- 识别完成后耐心等待LLM回复")
    
    print("\n🚀 准备启动系统...")
    print("按Enter键开始实际体验...")
    input()
    
    # 启动实际系统
    try:
        from asr_llm_final import main
        main()
    except ImportError:
        print("❌ 无法导入ASR+LLM系统，请检查文件是否存在")
    except Exception as e:
        print(f"❌ 启动失败: {e}")


def show_config_info():
    """显示配置信息"""
    print("\n🔧 系统配置信息:")
    print("-" * 40)
    
    try:
        from config import API_KEY, BASE_URL, DEFAULT_MODEL
        print(f"🤖 LLM服务: {BASE_URL}")
        print(f"🔑 API密钥: {API_KEY[:10]}...")
        print(f"📱 使用模型: {DEFAULT_MODEL}")
    except ImportError:
        print("❌ 无法读取LLM配置")
    
    try:
        from 流式_副本2.const import APPID, APPKEY, DEV_PID, URI
        print(f"🎤 ASR服务: {URI}")
        print(f"🆔 应用ID: {APPID}")
        print(f"🔑 应用密钥: {APPKEY[:10]}...")
        print(f"📊 识别模型: {DEV_PID}")
    except ImportError:
        print("❌ 无法读取ASR配置")


def main():
    """主函数"""
    print("🎬 ASR + LLM 串联系统演示")
    print("=" * 60)
    
    while True:
        print("\n🎯 请选择演示内容:")
        print("1. 📋 查看工作流程说明")
        print("2. 🔧 查看系统配置")
        print("3. 🚀 启动实际系统")
        print("4. 🚪 退出演示")
        
        choice = input("\n请输入选项 (1-4): ").strip()
        
        if choice == "1":
            demo_workflow()
        elif choice == "2":
            show_config_info()
        elif choice == "3":
            print("\n🚀 正在启动ASR+LLM串联系统...")
            try:
                from asr_llm_final import main
                main()
            except ImportError:
                print("❌ 无法导入ASR+LLM系统，请检查文件是否存在")
            except Exception as e:
                print(f"❌ 启动失败: {e}")
        elif choice == "4":
            print("👋 演示结束，再见！")
            break
        else:
            print("❌ 无效选项，请输入 1-4")


if __name__ == "__main__":
    main()
