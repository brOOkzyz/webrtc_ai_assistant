#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebRTC语音助手启动脚本
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import WebRTCServer
from config import SERVER_HOST, SERVER_PORT

async def main():
    """主函数"""
    try:
        server = WebRTCServer(SERVER_HOST, SERVER_PORT)
        print(f"正在启动WebRTC语音助手服务器...")
        print(f"监听地址: {SERVER_HOST}:{SERVER_PORT}")
        await server.start()
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
