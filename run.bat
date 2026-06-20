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

if exist "%~dp0dist\RedGarph.exe" (
    echo Starting RedGarph (compiled)...
    start "" "%~dp0dist\RedGarph.exe"
) else (
    echo Starting RedGarph (source)...
    python main.py
    if errorlevel 1 (
        echo.
        echo Launch failed (error code %errorlevel%^)
        pause
        exit /b %errorlevel%
    )
)
