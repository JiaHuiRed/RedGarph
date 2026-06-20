@echo off
cd /d "%~dp0"

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Install Python 3.10+ first.
    pause
    exit /b 1
)

python -c "import PyQt6" >nul 2>&1
if %errorlevel% neq 0 (
    pip install PyQt6
)

echo Starting RedGarph...
python main.py
if errorlevel 1 (
    echo.
    echo Launch failed (error code %errorlevel%^)
    pause
    exit /b %errorlevel%
)
