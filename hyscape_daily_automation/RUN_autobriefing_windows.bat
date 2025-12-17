@echo off
chcp 65001 > nul
title Hyscape Daily Automation

echo ============================================================
echo Hyscape Unified Daily Automation System
echo ============================================================
echo.
echo [%date% %time%] Starting automation...
echo.

REM Navigate to script directory
cd /d H:\부서\cjh\hyscape_daily_automation

REM Run Python script
"C:\Users\jjeor\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe" main_unified.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================================
    echo ERROR: Automation failed!
    echo ============================================================
    echo [%date% %time%] Check logs for details
    echo Error code: %ERRORLEVEL%
) else (
    echo.
    echo ============================================================
    echo SUCCESS: All tasks completed!
    echo ============================================================
)

echo.
echo Press any key to exit...
pause
