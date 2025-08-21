# -*- coding: utf-8 -*-
"""
WebRTC语音助手系统配置
"""

# LLM API配置
API_KEY = "your-api-key"
BASE_URL = "https://api.siliconflow.cn"
DEFAULT_MODEL = "THUDM/glm-4-9b-chat"
TEMPERATURE = 0.7
MAX_TOKENS = 1000

# 音频配置
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
AUDIO_SAMPLE_WIDTH = 2
AUDIO_BUFFER_SIZE = 1024

# 语音检测
SILENCE_THRESHOLD = 1.0
VOICE_DETECTION_THRESHOLD = 0.012
MIN_VOICE_FRAMES = 1

# 服务器配置
SERVER_HOST = "localhost"
SERVER_PORT = 8765

# 线程池配置
THREAD_POOL_MAX_WORKERS = 20
THREAD_POOL_QUEUE_SIZE = 100

# 超时配置
API_TIMEOUTS = {
    'ASR_TOKEN': 5,
    'ASR_REQUEST': 8,
    'LLM_REQUEST': 15,
    'TTS_TOKEN': 5,
    'TTS_REQUEST': 10,
    'WEBSOCKET': 30
}

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"
LOG_FILE = "webrtc_voice_assistant.log"
