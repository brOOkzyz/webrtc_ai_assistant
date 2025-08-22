#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动脚本 - SiliconFlow LLM 聊天机器人
"""

import os
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 导入并运行主程序
from llm_chat import main

if __name__ == "__main__":
    main()
