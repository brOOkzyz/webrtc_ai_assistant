#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebRTC语音助手系统 - 安装配置
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "WebRTC语音助手系统 - 集成ASR+LLM+TTS的完整解决方案"

# 读取requirements文件
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return [
        'websockets>=10.0',
        'requests>=2.25.0',
        'asyncio',
        'logging',
        'json',
        'time',
        'uuid',
        'base64',
        'wave',
        'io',
        'collections',
        'concurrent.futures'
    ]

setup(
    name="webrtc-voice-assistant",
    version="2.0.0",
    author="AI Assistant",
    author_email="assistant@example.com",
    description="WebRTC语音助手系统 - 集成ASR+LLM+TTS的完整解决方案",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/example/webrtc-voice-assistant",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Communications :: Conferencing",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "full": [
            "psutil>=5.8.0",
            "numpy>=1.20.0",
            "scipy>=1.7.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "webrtc-voice-assistant=webrtc_voice_assistant.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "webrtc_voice_assistant": [
            "*.html",
            "*.md",
            "*.txt",
            "*.sh",
            "*.bat",
        ],
    },
    keywords=[
        "webrtc", "asr", "llm", "tts", "voice", "assistant", 
        "speech", "recognition", "synthesis", "ai", "chatbot"
    ],
    project_urls={
        "Bug Reports": "https://github.com/example/webrtc-voice-assistant/issues",
        "Source": "https://github.com/example/webrtc-voice-assistant",
        "Documentation": "https://github.com/example/webrtc-voice-assistant/blob/main/README.md",
    },
    license="MIT",
    zip_safe=False,
)
