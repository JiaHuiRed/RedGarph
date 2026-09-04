@echo off
setlocal enabledelayedexpansion

set MODE=%~1
if "%MODE%"=="debug" (
    set BUILD_NAME=RedGarph_debug
    set CONSOLE_FLAG=--console
    set OUTPUT_MSG=dist/RedGarph_debug/RedGarph_debug.exe
    set SPEC_FILE=RedGarph_debug.spec
) else (
    set BUILD_NAME=RedGarph
    set CONSOLE_FLAG=--windowed
    set OUTPUT_MSG=dist/RedGarph/RedGarph.exe
    set SPEC_FILE=RedGarph.spec
)

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Install Python 3.10+ first.
    pause
    exit /b 1
)

python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo PyInstaller installation failed.
        pause
        exit /b 1
    )
)

for /f "delims=" %%v in ('python -c "import sys; sys.path.insert(0, '.'); from viewer.constants import APP_VERSION; print(APP_VERSION)"') do set APP_VERSION=%%v

echo Checking version consistency...

python scripts/check_version.py

if %errorlevel% neq 0 (
    echo.
    echo Aborted due to version inconsistency.
    pause
    exit /b 1
)

echo Building RedGarph V%APP_VERSION% (%MODE%)...
python -m PyInstaller --onedir %CONSOLE_FLAG% --name "%BUILD_NAME%" --icon resources\icon.ico --add-data "resources\icon.ico;resources" --clean --noconfirm --hidden-import=viewer --hidden-import=viewer.window --hidden-import=ctypes.wintypes main.py

set BUILD_ERROR=%errorlevel%

if %BUILD_ERROR% equ 0 (
    echo.
    echo Build OK -- %OUTPUT_MSG%
) else (
    echo.
    echo Build failed.
)

echo Cleaning build artifacts...
rmdir /s /q build >nul 2>&1
del %SPEC_FILE% >nul 2>&1

exit /b %BUILD_ERROR%
