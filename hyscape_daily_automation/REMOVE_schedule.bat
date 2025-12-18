@echo off
chcp 65001 > nul
title Hyscape Daily Briefing - Remove Schedule

echo ============================================================
echo Hyscape Daily Briefing - Remove Schedule
echo ============================================================
echo.
echo This will remove the scheduled task for daily briefing.
echo.
echo NOTE: This requires Administrator privileges!
echo.
pause

REM Run PowerShell script with Administrator privileges
powershell -ExecutionPolicy Bypass -File "%~dp0remove_schedule.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to run remove script!
    echo Please make sure you run this as Administrator.
    pause
)
