# -*- coding: utf-8 -*-
"""
配置文件 - SiliconFlow LLM API 设置
"""

# API配置
API_KEY = "sk-vjntadlyyvfewqskgazdzosowrqmaqcpmwhcnlknauqejssi"
BASE_URL = "https://api.siliconflow.cn"

# 模型配置
DEFAULT_MODEL = "THUDM/glm-4-9b-chat"
TEMPERATURE = 0.7
MAX_TOKENS = 1000

# 打字机效果配置
TYPEWRITER_DELAY = 0.03  # 每个字符之间的延迟时间（秒）

# 可用的模型列表
AVAILABLE_MODELS = [
    "THUDM/glm-4-9b-chat"
]
