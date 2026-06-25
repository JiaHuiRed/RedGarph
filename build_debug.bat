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

for /f "delims=" %%v in ('python -c "import sys; sys.path.insert(0, '.'); from viewer.constants import APP_VERSION; print(APP_VERSION)"') do set APP_VERSION=%%v

echo Building RedGarph V%APP_VERSION% (debug)...
pyinstaller --onefile --console --name "RedGarph_debug" --icon resources\icon.ico --clean --noconfirm --hidden-import=viewer --hidden-import=viewer.window --hidden-import=ctypes.wintypes main.py

if %errorlevel% equ 0 (
    echo.
    echo Build OK -- dist/RedGarph_debug.exe
    rmdir /s /q build >nul 2>&1
    del RedGarph_debug.spec >nul 2>&1
    pause
) else (
    echo.
    echo Build failed.
    pause
    exit /b %errorlevel%
)
