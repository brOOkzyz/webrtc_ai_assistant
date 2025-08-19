#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebRTC语音助手系统 - 命令行接口
"""

import asyncio
import argparse
import sys
import logging
from .server import WebRTCServer
from . import get_info, create_server

def setup_logging(verbose=False):
    """设置日志级别"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='[%(asctime)s] [%(levelname)s] %(message)s'
    )

def print_banner():
    """打印系统横幅"""
    info = get_info()
    print("=" * 60)
    print(f"🚀 {info['name'].upper()} v{info['version']}")
    print(f"📝 {info['description']}")
    print(f"👨‍💻 作者: {info['author']}")
    print(f"📄 许可证: {info['license']}")
    print("=" * 60)

def print_help():
    """打印帮助信息"""
    print("\n📖 使用说明:")
    print("  启动服务器: webrtc-voice-assistant start [--host HOST] [--port PORT]")
    print("  查看信息:  webrtc-voice-assistant info")
    print("  查看帮助:  webrtc-voice-assistant --help")
    
    print("\n🔧 参数说明:")
    print("  --host HOST    服务器主机地址 (默认: localhost)")
    print("  --port PORT    服务器端口 (默认: 8765)")
    print("  --verbose     启用详细日志")
    print("  --version     显示版本信息")

async def start_server(host, port, verbose):
    """启动WebRTC服务器"""
    try:
        print_banner()
        print(f"\n🌐 启动WebRTC服务器...")
        print(f"📍 地址: {host}:{port}")
        print(f"💡 客户端连接: http://{host}:{port}")
        print(f"📱 使用 webrtc_client.html 连接")
        print("\n按 Ctrl+C 停止服务器")
        print("-" * 60)
        
        server = create_server(host=host, port=port)
        await server.start()
        
    except KeyboardInterrupt:
        print("\n\n🛑 服务器被用户中断")
    except Exception as e:
        print(f"\n❌ 服务器启动失败: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="WebRTC语音助手系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  webrtc-voice-assistant start              # 启动服务器
  webrtc-voice-assistant start --port 8888  # 指定端口
  webrtc-voice-assistant info               # 查看包信息
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # start 命令
    start_parser = subparsers.add_parser('start', help='启动WebRTC服务器')
    start_parser.add_argument('--host', default='localhost', help='服务器主机地址 (默认: localhost)')
    start_parser.add_argument('--port', type=int, default=8765, help='服务器端口 (默认: 8765)')
    start_parser.add_argument('--verbose', action='store_true', help='启用详细日志')
    
    # info 命令
    info_parser = subparsers.add_parser('info', help='显示包信息')
    
    # 全局参数
    parser.add_argument('--version', action='version', version='%(prog)s 2.0.0')
    
    args = parser.parse_args()
    
    if not args.command:
        print_banner()
        print_help()
        return
    
    if args.command == 'start':
        setup_logging(args.verbose)
        asyncio.run(start_server(args.host, args.port, args.verbose))
    
    elif args.command == 'info':
        info = get_info()
        print_banner()
        print(f"\n📦 包信息:")
        print(f"  名称: {info['name']}")
        print(f"  版本: {info['version']}")
        print(f"  描述: {info['description']}")
        print(f"  作者: {info['author']}")
        print(f"  许可证: {info['license']}")
        print(f"  关键词: {', '.join(info['keywords'])}")
        
        print(f"\n🔧 功能特性:")
        print(f"  ✅ 实时语音识别 (ASR)")
        print(f"  ✅ 智能对话系统 (LLM)")
        print(f"  ✅ 语音合成播放 (TTS)")
        print(f"  ✅ 用户打断功能")
        print(f"  ✅ WebRTC实时通信")
        print(f"  ✅ 模块化架构设计")

if __name__ == "__main__":
    main()
