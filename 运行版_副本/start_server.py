#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebRTC语音助手服务器启动脚本

主要功能：
1. 配置检查和验证
2. 服务器启动和监控
3. 优雅关闭处理
4. 错误恢复和重启

版本: 2.0.0
"""

import os
import sys
import time
import signal
import logging
import argparse
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入配置和服务器
from config import validate_config, get_config_summary, SERVER_HOST, SERVER_PORT
from server import WebRTCServer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('startup.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class ServerManager:
    """服务器管理器"""
    
    def __init__(self):
        """初始化服务器管理器"""
        self.server = None
        self.is_running = False
        self.start_time = None
        self.restart_count = 0
        self.max_restarts = 3
        
        # 设置信号处理器
        self._setup_signal_handlers()
        
        logger.info("🔧 服务器管理器初始化完成")
    
    def _setup_signal_handlers(self):
        """设置信号处理器"""
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            logger.info("✅ 信号处理器设置完成")
        except Exception as e:
            logger.warning(f"⚠️ 信号处理器设置失败: {e}")
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        signal_name = signal.Signals(signum).name
        logger.info(f"🛑 收到信号: {signal_name}")
        self.shutdown()
    
    def validate_environment(self) -> bool:
        """验证运行环境"""
        try:
            logger.info("🔍 开始验证运行环境...")
            
            # 检查Python版本
            if sys.version_info < (3, 7):
                logger.error("❌ Python版本过低，需要Python 3.7+")
                return False
            
            # 检查配置文件
            if not validate_config():
                logger.error("❌ 配置文件验证失败")
                return False
            
            # 检查依赖模块
            required_modules = ['websockets', 'requests', 'asyncio']
            for module in required_modules:
                try:
                    __import__(module)
                except ImportError:
                    logger.error(f"❌ 缺少必需模块: {module}")
                    return False
            
            # 检查端口可用性
            if not self._check_port_availability():
                logger.error(f"❌ 端口 {SERVER_PORT} 不可用")
                return False
            
            logger.info("✅ 运行环境验证通过")
            return True
            
        except Exception as e:
            logger.error(f"❌ 环境验证失败: {e}")
            return False
    
    def _check_port_availability(self) -> bool:
        """检查端口是否可用"""
        try:
            import socket
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((SERVER_HOST, SERVER_PORT))
                return result != 0  # 0表示端口被占用
                
        except Exception as e:
            logger.warning(f"⚠️ 端口检查失败: {e}")
            return True  # 检查失败时假设端口可用
    
    def print_startup_banner(self):
        """打印启动横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    WebRTC语音助手服务器                      ║
║                                                              ║
║  版本: 2.0.0                                                ║
║  作者: AI Assistant                                         ║
║  功能: ASR + LLM + TTS 语音交互                             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
        # 打印配置摘要
        config_summary = get_config_summary()
        print("📋 配置摘要:")
        for key, value in config_summary.items():
            print(f"  {key}: {value}")
        print()
    
    async def start_server(self) -> bool:
        """启动服务器"""
        try:
            logger.info("🚀 正在启动WebRTC语音助手服务器...")
            
            # 创建服务器实例
            self.server = WebRTCServer(SERVER_HOST, SERVER_PORT)
            
            # 启动服务器
            await self.server.start()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 服务器启动失败: {e}")
            return False
    
    async def run_server(self):
        """运行服务器主循环"""
        try:
            self.is_running = True
            self.start_time = time.time()
            
            # 启动服务器
            if not await self.start_server():
                return False
            
            # 保持服务器运行
            while self.is_running:
                await asyncio.sleep(1)
                
                # 检查服务器健康状态
                if not self._check_server_health():
                    logger.warning("⚠️ 服务器健康检查失败")
                    break
            
            return True
            
        except asyncio.CancelledError:
            logger.info("🛑 服务器运行被取消")
            return True
        except Exception as e:
            logger.error(f"❌ 服务器运行异常: {e}")
            return False
        finally:
            self.is_running = False
    
    def _check_server_health(self) -> bool:
        """检查服务器健康状态"""
        try:
            if not self.server:
                return False
            
            # 检查运行时间
            if self.start_time:
                uptime = time.time() - self.start_time
                if uptime > 86400:  # 24小时
                    logger.info(f"📊 服务器已运行: {uptime/3600:.1f} 小时")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 健康检查失败: {e}")
            return False
    
    def shutdown(self):
        """关闭服务器"""
        try:
            logger.info("🛑 正在关闭服务器...")
            
            self.is_running = False
            
            # 清理资源
            if self.server:
                # 停止WebRTC服务器
                try:
                    asyncio.create_task(self.server.stop())
                except Exception as e:
                    logger.warning(f"⚠️ 停止服务器时出现警告: {e}")
            
            logger.info("✅ 服务器已关闭")
            
            # 退出程序
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"❌ 服务器关闭失败: {e}")
            sys.exit(1)
    
    async def restart_server(self):
        """重启服务器"""
        try:
            if self.restart_count >= self.max_restarts:
                logger.error(f"❌ 达到最大重启次数: {self.max_restarts}")
                return False
            
            self.restart_count += 1
            logger.info(f"🔄 正在重启服务器 (第 {self.restart_count} 次)...")
            
            # 等待一段时间后重启
            await asyncio.sleep(5)
            
            # 重新启动
            return await self.run_server()
            
        except Exception as e:
            logger.error(f"❌ 服务器重启失败: {e}")
            return False

async def main():
    """主函数"""
    try:
        # 创建服务器管理器
        manager = ServerManager()
        
        # 打印启动横幅
        manager.print_startup_banner()
        
        # 验证环境
        if not manager.validate_environment():
            logger.error("❌ 环境验证失败，无法启动服务器")
            return 1
        
        # 运行服务器
        success = await manager.run_server()
        
        if not success and manager.restart_count < manager.max_restarts:
            # 尝试重启
            logger.info("🔄 尝试重启服务器...")
            success = await manager.restart_server()
        
        if success:
            logger.info("✅ 服务器运行完成")
            return 0
        else:
            logger.error("❌ 服务器运行失败")
            return 1
            
    except KeyboardInterrupt:
        logger.info("🛑 服务器被用户中断")
        return 0
    except Exception as e:
        logger.error(f"❌ 主程序异常: {e}")
        return 1

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='WebRTC语音助手服务器')
    
    parser.add_argument(
        '--host', 
        default=SERVER_HOST,
        help=f'服务器监听地址 (默认: {SERVER_HOST})'
    )
    
    parser.add_argument(
        '--port', 
        type=int, 
        default=SERVER_PORT,
        help=f'服务器监听端口 (默认: {SERVER_PORT})'
    )
    
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='启用调试模式'
    )
    
    parser.add_argument(
        '--validate-only', 
        action='store_true',
        help='仅验证配置，不启动服务器'
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    try:
        # 解析命令行参数
        args = parse_arguments()
        
        # 如果只是验证配置
        if args.validate_only:
            print("🔍 配置验证模式")
            if validate_config():
                print("✅ 配置验证通过")
                config_summary = get_config_summary()
                print("📋 配置摘要:")
                for key, value in config_summary.items():
                    print(f"  {key}: {value}")
                sys.exit(0)
            else:
                print("❌ 配置验证失败")
                sys.exit(1)
        
        # 启动服务器
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n🛑 程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 程序启动失败: {e}")
        sys.exit(1)
