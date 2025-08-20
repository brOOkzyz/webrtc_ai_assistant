@echo off
chcp 65001 >nul
echo 🚀 启动WebRTC语音助手服务器
echo ==================================

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python
    echo 请先安装Python并添加到PATH环境变量
    pause
    exit /b 1
)

REM 检查依赖
echo 📦 检查依赖...
python -c "import websockets" 2>nul
if errorlevel 1 (
    echo ❌ 缺少websockets依赖，正在安装...
    pip install websockets
)

python -c "import requests" 2>nul
if errorlevel 1 (
    echo ❌ 缺少requests依赖，正在安装...
    pip install requests
)

REM 检查配置文件
if not exist "config.py" (
    echo ❌ 错误: 未找到config.py配置文件
    echo 请先配置API密钥等信息
    pause
    exit /b 1
)

REM 启动服务器
echo ✅ 依赖检查完成
echo 🌐 启动WebRTC服务器...
echo 💡 服务器将在 http://localhost:8765 启动
echo 💡 客户端可以通过 webrtc_client.html 连接
echo.
echo 按 Ctrl+C 停止服务器
echo ==================================

python server.py
pause
