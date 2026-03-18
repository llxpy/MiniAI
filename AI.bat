@echo off
chcp 65001 >nul 2>&1
title 我的专属AI助手
echo ==============================
echo      正在启动AI助手...
echo ==============================
echo.

:: 切换到python-caller目录（根据你的实际路径修改）
cd /d "C:\Users\Administrator\Desktop\MiniAI\python-caller"

:: 检查Python是否安装
python -V >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请先安装Python并添加到环境变量！
    pause
    exit /b 1
)

:: 检查Flask是否安装
python -m pip show flask >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖（Flask）...
    python -m pip install flask -i https://pypi.tuna.tsinghua.edu.cn/simple
)

:: 启动AI服务
echo 正在启动AI网页服务...
echo 启动成功后，浏览器会自动打开：http://127.0.0.1:5000
echo （关闭此窗口即可停止AI服务）
echo.
python node_caller.py

:: 防止窗口闪退
pause