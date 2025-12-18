@echo off
chcp 65001 > nul
title Hyscape Daily Briefing - Schedule Setup

echo ============================================================
echo Hyscape Daily Briefing - Schedule Setup
echo ============================================================
echo.
echo This will create a scheduled task to run the daily briefing
echo automatically at 9:00 AM on weekdays (Monday-Friday).
echo.
echo NOTE: This requires Administrator privileges!
echo.
pause

REM Run PowerShell script with Administrator privileges
powershell -ExecutionPolicy Bypass -File "%~dp0setup_daily_schedule.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to run setup script!
    echo Please make sure you run this as Administrator.
    pause
)
