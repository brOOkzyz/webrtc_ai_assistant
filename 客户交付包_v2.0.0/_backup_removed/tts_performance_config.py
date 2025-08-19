#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTS性能配置文件
用户可以根据需要选择延迟和稳定性之间的平衡
"""

# TTS性能配置选项
TTS_PERFORMANCE_MODE = "ULTRA_FAST"  # 可选: "ULTRA_FAST", "FAST", "BALANCED", "STABLE"

# 超低延迟模式配置（优先极致响应速度）
ULTRA_FAST_MODE_CONFIG = {
    "tts_stop_wait_time": 0.05,        # TTS停止等待时间（秒）
    "tts_status_check_interval": 0.01, # TTS状态检查间隔（秒）
    "max_wait_time": 0.5,              # 最大等待时间（秒）
    "use_fast_stop": True,             # 使用快速停止模式
    "process_cleanup_timeout": 0.02,   # 进程清理超时时间（秒）
    "force_stop_delay": 0.02,          # 强制停止延迟（秒）
    "websocket_connection_wait": 0.1,  # WebSocket连接等待时间（秒）
}

# 快速模式配置（优先响应速度）
FAST_MODE_CONFIG = {
    "tts_stop_wait_time": 0.1,         # TTS停止等待时间（秒）
    "tts_status_check_interval": 0.02, # TTS状态检查间隔（秒）
    "max_wait_time": 1.0,              # 最大等待时间（秒）
    "use_fast_stop": True,             # 使用快速停止模式
    "process_cleanup_timeout": 0.05,   # 进程清理超时时间（秒）
    "force_stop_delay": 0.05,          # 强制停止延迟（秒）
    "websocket_connection_wait": 0.2,  # WebSocket连接等待时间（秒）
}

# 平衡模式配置（平衡响应速度和稳定性）
BALANCED_MODE_CONFIG = {
    "tts_stop_wait_time": 0.2,         # TTS停止等待时间（秒）
    "tts_status_check_interval": 0.05, # TTS状态检查间隔（秒）
    "max_wait_time": 2.0,              # 最大等待时间（秒）
    "use_fast_stop": True,             # 使用快速停止模式
    "process_cleanup_timeout": 0.1,    # 进程清理超时时间（秒）
    "force_stop_delay": 0.1,           # 强制停止延迟（秒）
    "websocket_connection_wait": 0.3,  # WebSocket连接等待时间（秒）
}

# 稳定模式配置（优先稳定性）
STABLE_MODE_CONFIG = {
    "tts_stop_wait_time": 0.5,         # TTS停止等待时间（秒）
    "tts_status_check_interval": 0.1,  # TTS状态检查间隔（秒）
    "max_wait_time": 5.0,              # 最大等待时间（秒）
    "use_fast_stop": False,            # 不使用快速停止模式
    "process_cleanup_timeout": 0.2,    # 进程清理超时时间（秒）
    "force_stop_delay": 0.2,           # 强制停止延迟（秒）
    "websocket_connection_wait": 0.5,  # WebSocket连接等待时间（秒）
}

def get_tts_config():
    """根据性能模式获取TTS配置"""
    if TTS_PERFORMANCE_MODE == "ULTRA_FAST":
        return ULTRA_FAST_MODE_CONFIG
    elif TTS_PERFORMANCE_MODE == "FAST":
        return FAST_MODE_CONFIG
    elif TTS_PERFORMANCE_MODE == "STABLE":
        return STABLE_MODE_CONFIG
    else:
        return BALANCED_MODE_CONFIG

def print_current_config():
    """打印当前配置信息"""
    config = get_tts_config()
    print(f"🎯 当前TTS性能模式: {TTS_PERFORMANCE_MODE}")
    print(f"⚡ TTS停止等待时间: {config['tts_stop_wait_time']}秒")
    print(f"🔍 TTS状态检查间隔: {config['tts_status_check_interval']}秒")
    print(f"⏱️ 最大等待时间: {config['max_wait_time']}秒")
    print(f"🚀 快速停止模式: {'启用' if config['use_fast_stop'] else '禁用'}")
    print(f"🧹 进程清理超时: {config['process_cleanup_timeout']}秒")
    print(f"🛑 强制停止延迟: {config['force_stop_delay']}秒")
    print(f"🔌 WebSocket连接等待: {config['websocket_connection_wait']}秒")
    
    if TTS_PERFORMANCE_MODE == "ULTRA_FAST":
        print("💡 超低延迟模式：极致响应速度，可能存在轻微音频重叠风险")
    elif TTS_PERFORMANCE_MODE == "FAST":
        print("💡 快速模式：优先响应速度，可能存在轻微音频重叠风险")
    elif TTS_PERFORMANCE_MODE == "STABLE":
        print("💡 稳定模式：优先稳定性，响应速度较慢")
    else:
        print("💡 平衡模式：平衡响应速度和稳定性")

def change_performance_mode(mode):
    """更改性能模式"""
    global TTS_PERFORMANCE_MODE
    valid_modes = ["ULTRA_FAST", "FAST", "BALANCED", "STABLE"]
    
    if mode.upper() in valid_modes:
        TTS_PERFORMANCE_MODE = mode.upper()
        print(f"✅ 性能模式已更改为: {TTS_PERFORMANCE_MODE}")
        print_current_config()
        return True
    else:
        print(f"❌ 无效的性能模式: {mode}")
        print(f"💡 有效的模式: {', '.join(valid_modes)}")
        return False

if __name__ == "__main__":
    print("🎯 TTS性能配置工具")
    print("=" * 40)
    print_current_config()
    
    print("\n💡 要更改性能模式，请编辑此文件中的 TTS_PERFORMANCE_MODE 变量")
    print("💡 或者在代码中调用 change_performance_mode() 函数")
    
    # 示例：如何更改性能模式
    print("\n📝 使用示例:")
    print("from tts_performance_config import change_performance_mode")
    print("change_performance_mode('FAST')  # 切换到快速模式")
    print("change_performance_mode('STABLE')  # 切换到稳定模式")
