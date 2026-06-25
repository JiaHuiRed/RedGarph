@echo off
cd /d "%~dp0"

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Install Python 3.10+ first.
    pause
    exit /b 1
)

where pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    pip install pyinstaller
)

echo Building RedGarph V0.1.0...
pyinstaller --onefile --windowed --name "RedGarph" --icon resources\icon.ico --clean --noconfirm --hidden-import=viewer --hidden-import=viewer.window --hidden-import=ctypes.wintypes main.py

if %errorlevel% equ 0 (
    echo.
    echo Build OK -- dist/RedGarph.exe
    rmdir /s /q build >nul 2>&1
    del RedGarph.spec >nul 2>&1
    pause
) else (
    echo.
    echo Build failed.
    pause
    exit /b %errorlevel%
)
