#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音检测配置文件
可以在这里调整各种阈值来优化语音检测效果
"""

# ==================== 能量阈值配置 ====================
# 主要能量阈值 - 调整这个值来改变语音检测的敏感度
ENERGY_THRESHOLD = 100000          # 默认100000，值越大越不敏感

# 实时音频监控的能量阈值
REALTIME_ENERGY_THRESHOLD = 100000 # 与主阈值保持一致

# 低能量阈值 - 用于环境噪音过滤
LOW_ENERGY_THRESHOLD = 50000       # 低于此值认为是环境噪音

# ==================== 语音识别器参数 ====================
# 能量阈值
RECOGNIZER_ENERGY_THRESHOLD = 100000

# 停顿检测时间（秒）
PAUSE_THRESHOLD = 1.5

# 非说话时长（秒）
NON_SPEAKING_DURATION = 1.2

# 动态能量调整比例
DYNAMIC_ENERGY_ADJUSTMENT_RATIO = 1.5

# 短语阈值
PHRASE_THRESHOLD = 0.9

# 环境噪音调整时长（秒）
AMBIENT_DURATION = 5.0

# ==================== 音频质量过滤 ====================
# 最小音频时长（秒）
MIN_AUDIO_DURATION = 1.0

# 最大音频时长（秒）
MAX_AUDIO_DURATION = 20.0

# 最小语音间隔（秒）
MIN_SPEECH_INTERVAL = 1.5

# ==================== 误触发过滤 ====================
# 连续短音频计数阈值
CONSECUTIVE_SHORT_AUDIO_THRESHOLD = 2

# 连续低能量计数阈值
CONSECUTIVE_LOW_ENERGY_THRESHOLD = 3

# 连续无意义语音计数阈值
CONSECUTIVE_MEANINGLESS_THRESHOLD = 1

# ==================== 等待时间配置 ====================
# 连续短音频后等待时间（秒）
SHORT_AUDIO_WAIT_TIME = 3

# 连续低能量后等待时间（秒）
LOW_ENERGY_WAIT_TIME = 5

# 无意义语音后等待时间（秒）
MEANINGLESS_SPEECH_WAIT_TIME = 2

# ==================== 有意义词汇列表 ====================
# 这些词汇被认为是有效的语音输入
MEANINGFUL_WORDS = [
    '你好', '开始', '说话', '回答', '问题', '停止', '退出', '谢谢', '再见',
    '好的', '可以', '什么', '怎么', '为什么', '如何', '请', '帮',
    '我', '你', '他', '她', '它', '是', '的', '了', '在', '有',
    '和', '与', '或', '但', '因为', '所以', '如果', '那么',
    '现在', '今天', '明天', '昨天'
]

# 最小有意义文本长度
MIN_MEANINGFUL_TEXT_LENGTH = 3

# ==================== 调试配置 ====================
# 是否启用详细调试信息
ENABLE_DEBUG = True

# 是否显示音频能量信息
SHOW_ENERGY_INFO = True

# 是否显示音频时长信息
SHOW_DURATION_INFO = True

# ==================== 性能配置 ====================
# 实时音频监控检查间隔（秒）
REALTIME_CHECK_INTERVAL = 0.02

# 音频缓冲区大小
AUDIO_BUFFER_SIZE = 512

# 音频采样率
SAMPLE_RATE = 16000

# 音频格式
AUDIO_FORMAT = 'pcm'

# 音频声道数
AUDIO_CHANNELS = 1

# ==================== 使用说明 ====================
"""
调整建议：

1. 如果经常误触发（环境噪音被识别为语音）：
   - 增加 ENERGY_THRESHOLD 到 120000 或更高
   - 增加 RECOGNIZER_ENERGY_THRESHOLD 到相同值
   - 增加 MIN_AUDIO_DURATION 到 1.2 或更高

2. 如果语音检测不够敏感（说话没反应）：
   - 减少 ENERGY_THRESHOLD 到 80000 或更低
   - 减少 RECOGNIZER_ENERGY_THRESHOLD 到相同值
   - 减少 MIN_AUDIO_DURATION 到 0.8 或更低

3. 如果响应太慢：
   - 减少各种等待时间
   - 减少计数阈值

4. 如果误触发仍然频繁：
   - 增加 MIN_MEANINGFUL_TEXT_LENGTH 到 4 或更高
   - 增加 MIN_SPEECH_INTERVAL 到 2.0 或更高
"""
