@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo [RedGarph] 一键启动
echo =====================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [!!] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

python -c "import PyQt6" >nul 2>&1
if %errorlevel% neq 0 (
    echo [..] 安装 PyQt6...
    pip install PyQt6
)

echo [..] 启动 RedGarph...
python main.py
if errorlevel 1 (
    echo.
    echo [!!] 启动失败，错误码 %errorlevel%
    pause
    exit /b %errorlevel%
)
