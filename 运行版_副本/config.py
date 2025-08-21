# -*- coding: utf-8 -*-
"""
配置文件 - WebRTC语音助手系统配置

版本: 2.0.0
"""

# =============================================================================
# LLM API 配置
# =============================================================================

# SiliconFlow API 配置
API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.siliconflow.cn"

# 模型配置
DEFAULT_MODEL = "THUDM/glm-4-9b-chat"
TEMPERATURE = 0.7          # 生成文本的随机性：0.0-1.0，越低越确定
MAX_TOKENS = 1000          # 最大生成token数

# 可用的模型列表
AVAILABLE_MODELS = [
    "THUDM/glm-4-9b-chat",    # 智谱GLM-4-9B模型
    "THUDM/glm-4-9b-chat-1m", # 智谱GLM-4-9B-1M模型
    "THUDM/glm-4-9b-chat-2m"  # 智谱GLM-4-9B-2M模型
]

# =============================================================================
# 音频处理配置
# =============================================================================

# 音频格式参数
AUDIO_SAMPLE_RATE = 16000      # 采样率：16kHz
AUDIO_CHANNELS = 1             # 声道数：单声道
AUDIO_SAMPLE_WIDTH = 2         # 采样位宽：16位
AUDIO_BUFFER_SIZE = 1024       # 音频缓冲区大小

# 语音检测参数
SILENCE_THRESHOLD = 1.0        # 静音检测阈值（秒）
VOICE_DETECTION_THRESHOLD = 0.012  # 语音检测音量阈值
MIN_VOICE_FRAMES = 1           # 最小语音帧数

# 音频缓冲区配置
AUDIO_BUFFER_MAX_SIZE = 50     # 最大音频缓冲区大小（块数）
AUDIO_PROCESSING_THRESHOLD = 3 # 音频处理阈值（最小块数）

# =============================================================================
# WebRTC 配置
# =============================================================================

# 服务器配置
SERVER_HOST = "localhost"      # 服务器监听地址
SERVER_PORT = 8765             # 服务器监听端口

# WebSocket 配置
WEBSOCKET_MAX_MESSAGE_SIZE = 1024 * 1024  # 最大消息大小：1MB
WEBSOCKET_PING_INTERVAL = 30              # Ping间隔（秒）
WEBSOCKET_PING_TIMEOUT = 10               # Ping超时（秒）

# =============================================================================
# 系统性能配置
# =============================================================================

# 线程池配置
THREAD_POOL_MAX_WORKERS = 20   # 最大工作线程数
THREAD_POOL_QUEUE_SIZE = 100   # 线程池队列大小

# 超时配置
API_TIMEOUTS = {
    'ASR_TOKEN': 5,            # ASR令牌获取超时（秒）
    'ASR_REQUEST': 8,          # ASR请求超时（秒）
    'LLM_REQUEST': 15,         # LLM请求超时（秒）
    'TTS_TOKEN': 5,            # TTS令牌获取超时（秒）
    'TTS_REQUEST': 10,         # TTS请求超时（秒）
    'WEBSOCKET': 30            # WebSocket操作超时（秒）
}

# 缓存配置
CACHE_TTL = {
    'ASR_TOKEN': 2592000,      # ASR令牌缓存时间：30天
    'TTS_TOKEN': 2592000,      # TTS令牌缓存时间：30天
    'CONVERSATION_HISTORY': 3600  # 对话历史缓存时间：1小时
}

# =============================================================================
# 日志配置
# =============================================================================

# 日志级别
LOG_LEVEL = "INFO"             # 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL

# 日志格式
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 日志文件配置
LOG_FILE = "webrtc_voice_assistant.log"  # 日志文件名
LOG_MAX_SIZE = 10 * 1024 * 1024         # 最大日志文件大小：10MB
LOG_BACKUP_COUNT = 5                     # 日志备份文件数量

# =============================================================================
# 错误处理和重试配置
# =============================================================================

# 重试配置
RETRY_CONFIG = {
    'ASR_MAX_RETRIES': 3,      # ASR最大重试次数
    'LLM_MAX_RETRIES': 3,      # LLM最大重试次数
    'TTS_MAX_RETRIES': 3,      # TTS最大重试次数
    'RETRY_DELAY': 1,          # 重试延迟（秒）
    'BACKOFF_MULTIPLIER': 2    # 退避乘数
}

# 错误阈值配置
ERROR_THRESHOLDS = {
    'MAX_CONSECUTIVE_FAILURES': 5,  # 最大连续失败次数
    'FAILURE_WINDOW': 300,          # 失败统计窗口（秒）
    'DEGRADATION_THRESHOLD': 0.8    # 服务降级阈值
}

# =============================================================================
# 安全配置
# =============================================================================

# API密钥配置
API_KEY_CONFIG = {
    'LLM_API_KEY': API_KEY,    # LLM API密钥
    'ASR_API_KEY': "your api key",      # ASR API密钥
    'TTS_API_KEY': "your api key",     # TTS API密钥
    'ASR_SECRET_KEY': "your secret key",  # ASR密钥
    'TTS_SECRET_KEY': "your secret key",  # TTS密钥
    'ASR_APP_ID': "your app id", # ASR应用ID
    'TTS_APP_ID': "your app id"  # TTS应用ID
}

# 访问控制配置
ACCESS_CONTROL = {
    'MAX_CLIENTS_PER_IP': 5,   # 每个IP最大客户端数
    'RATE_LIMIT_PER_CLIENT': 100,  # 每个客户端每分钟最大请求数
    'BLOCKED_IPS': [],         # 被封禁的IP列表
    'ALLOWED_ORIGINS': ["*"]   # 允许的跨域来源
}

# =============================================================================
# 监控和统计配置
# =============================================================================

# 性能监控配置
MONITORING_CONFIG = {
    'ENABLE_PERFORMANCE_MONITORING': True,  # 启用性能监控
    'METRICS_COLLECTION_INTERVAL': 60,      # 指标收集间隔（秒）
    'PERFORMANCE_HISTORY_SIZE': 1000,       # 性能历史记录大小
    'SLOW_QUERY_THRESHOLD': 5.0            # 慢查询阈值（秒）
}

# 统计配置
STATISTICS_CONFIG = {
    'ENABLE_STATISTICS': True,              # 启用统计功能
    'STATS_UPDATE_INTERVAL': 30,            # 统计更新间隔（秒）
    'MAX_STATS_HISTORY': 24 * 60,          # 最大统计历史（分钟）
    'ENABLE_DETAILED_LOGGING': False        # 启用详细日志记录
}

# =============================================================================
# 开发调试配置
# =============================================================================

# 调试模式配置
DEBUG_CONFIG = {
    'ENABLE_DEBUG_MODE': False,             # 启用调试模式
    'LOG_RAW_AUDIO_DATA': False,            # 记录原始音频数据
    'LOG_API_REQUESTS': False,              # 记录API请求详情
    'LOG_WEBSOCKET_MESSAGES': False,        # 记录WebSocket消息
    'ENABLE_PROFILING': False               # 启用性能分析
}

# 测试配置
TEST_CONFIG = {
    'ENABLE_MOCK_SERVICES': False,          # 启用模拟服务
    'MOCK_ASR_RESPONSE': "这是一个测试回复",  # 模拟ASR响应
    'MOCK_LLM_RESPONSE': "这是一个测试AI回复",  # 模拟LLM响应
    'MOCK_TTS_AUDIO_SIZE': 1024            # 模拟TTS音频大小
}

# =============================================================================
# 配置验证函数
# =============================================================================

def validate_config():
    """验证配置文件的完整性和有效性"""
    try:
        # 检查必需的API密钥
        required_keys = ['LLM_API_KEY', 'ASR_API_KEY', 'TTS_API_KEY']
        for key in required_keys:
            if not API_KEY_CONFIG.get(key):
                print(f"❌ 缺少必需的API密钥: {key}")
                return False
        
        # 检查端口范围
        if not (1024 <= SERVER_PORT <= 65535):
            print(f"❌ 服务器端口超出有效范围: {SERVER_PORT}")
            return False
        
        # 检查超时配置
        for service, timeout in API_TIMEOUTS.items():
            if timeout <= 0:
                print(f"❌ 无效的超时配置: {service} = {timeout}")
                return False
        
        # 检查音频配置
        if AUDIO_SAMPLE_RATE <= 0 or AUDIO_CHANNELS <= 0:
            print(f"❌ 无效的音频配置: 采样率={AUDIO_SAMPLE_RATE}, 声道数={AUDIO_CHANNELS}")
            return False
        
        print("✅ 配置文件验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 配置验证失败: {e}")
        return False

def get_config_summary():
    """获取配置摘要信息"""
    return {
        'server': f"{SERVER_HOST}:{SERVER_PORT}",
        'llm_model': DEFAULT_MODEL,
        'audio_sample_rate': AUDIO_SAMPLE_RATE,
        'max_workers': THREAD_POOL_MAX_WORKERS,
        'log_level': LOG_LEVEL,
        'debug_mode': DEBUG_CONFIG['ENABLE_DEBUG_MODE']
    }

# =============================================================================
# 环境变量覆盖配置
# =============================================================================

import os

# 允许通过环境变量覆盖的配置
ENV_OVERRIDES = {
    'SERVER_HOST': os.getenv('WEBRTC_SERVER_HOST', SERVER_HOST),
    'SERVER_PORT': int(os.getenv('WEBRTC_SERVER_PORT', SERVER_PORT)),
    'LOG_LEVEL': os.getenv('WEBRTC_LOG_LEVEL', LOG_LEVEL),
    'DEBUG_MODE': os.getenv('WEBRTC_DEBUG_MODE', 'false').lower() == 'true'
}

# 应用环境变量覆盖
SERVER_HOST = ENV_OVERRIDES['SERVER_HOST']
SERVER_PORT = ENV_OVERRIDES['SERVER_PORT']
LOG_LEVEL = ENV_OVERRIDES['LOG_LEVEL']
DEBUG_CONFIG['ENABLE_DEBUG_MODE'] = ENV_OVERRIDES['DEBUG_MODE']

# =============================================================================
# 配置初始化
# =============================================================================

if __name__ == "__main__":
    # 运行配置验证
    if validate_config():
        print("配置摘要:")
        summary = get_config_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")
    else:
        print("配置验证失败，请检查配置文件")
        exit(1)
