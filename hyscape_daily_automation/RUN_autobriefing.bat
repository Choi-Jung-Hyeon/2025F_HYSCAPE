@echo off
chcp 65001 > nul
title Hyscape Daily Automation

echo ============================================================
echo Hyscape Unified Daily Automation System
echo ============================================================
echo.
echo [%date% %time%] Starting automation...
echo.

REM Change to WSL directory and run Python script
wsl cd /home/fourmi103/2025F_HYSCAPE/hyscape_daily_automation ^&^& /home/fourmi103/2025F_HYSCAPE/venv/bin/python main_unified.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================================
    echo ERROR: Automation failed!
    echo ============================================================
    echo [%date% %time%] Check logs for details
) else (
    echo.
    echo ============================================================
    echo SUCCESS: All tasks completed!
    echo ============================================================
)

echo.
pause
