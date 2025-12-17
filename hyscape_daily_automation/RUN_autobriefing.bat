@echo off
chcp 65001 > nul
title Hyscape Daily Automation

echo ============================================================
echo Hyscape Unified Daily Automation System
echo ============================================================
echo.
echo [%date% %time%] Starting automation...
echo.

cd /d {PROJECT_PATH}
{PYTHON_PATH} main_unified.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================================
    echo ERROR: Automation failed!
    echo ============================================================
    echo [%date% %time%] Error logged >> logs/error.log
) else (
    echo.
    echo ============================================================
    echo SUCCESS: All tasks completed!
    echo ============================================================
)

echo.
pause
