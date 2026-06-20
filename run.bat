@echo off
chcp 65001 >nul
title RedGarph

echo [RedGarph] 一键启动
echo =====================
echo.

REM 检查 Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [!!] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

REM 检查 PyQt6
python -c "import PyQt6" >nul 2>&1
if %errorlevel% neq 0 (
    echo [..] 安装 PyQt6...
    pip install PyQt6
    echo.
)

REM 启动
echo [..] 启动 RedGarph...
start "" python main.py %*

echo [OK] 已启动！
