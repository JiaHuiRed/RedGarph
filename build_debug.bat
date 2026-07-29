@echo off
cd /d "%~dp0"
call build_common.bat debug
if %errorlevel% equ 0 pause
