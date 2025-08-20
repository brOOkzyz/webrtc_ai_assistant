@echo off
chcp 65001 >nul

REM 🎯 ASR + LLM + TTS 语音对话系统启动脚本
REM 客户交付版本 - Windows

echo 🎯 ASR + LLM + TTS 语音对话系统
echo ==================================
echo 正在启动系统...

REM 检查Python版本
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo ✅ Python版本: %python_version%

REM 检查依赖包
echo 🔍 检查依赖包...
python -c "import pyaudio, websocket, requests, speech_recognition" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ 检测到缺少依赖包，正在安装...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ 依赖包安装失败，请手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo ✅ 依赖包安装完成
) else (
    echo ✅ 依赖包检查通过
)

REM 检查配置文件
echo 🔍 检查配置文件...
if not exist "config.py" (
    echo ❌ 错误: 未找到config.py配置文件
    echo 请先配置您的API密钥
    pause
    exit /b 1
)

if not exist "baidu_tts_config.py" (
    echo ❌ 错误: 未找到baidu_tts_config.py配置文件
    echo 请先配置您的百度TTS服务
    pause
    exit /b 1
)

echo ✅ 配置文件检查通过

REM 启动主程序
echo 🚀 启动主程序...
echo ==================================
echo 💡 提示: 按Ctrl+C可以安全退出程序
echo ==================================

python asr_llm_working.py

pause
