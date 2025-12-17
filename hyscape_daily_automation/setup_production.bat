@echo off
echo ============================================================
echo Hyscape Automation - Production Setup
echo ============================================================
echo.

echo Enter Python executable path:
echo Example: C:\Users\YourName\AppData\Local\Microsoft\WindowsApps\python.exe
set /p PYTHON_PATH=

echo.
echo Enter project directory path:
echo Example: C:\Source\hyscape_daily_automation
set /p PROJECT_PATH=

echo.
echo Updating RUN_autobriefing.bat...
powershell -Command "(Get-Content RUN_autobriefing.bat) -replace '\{PYTHON_PATH\}', '%PYTHON_PATH%' | Set-Content RUN_autobriefing.bat"
powershell -Command "(Get-Content RUN_autobriefing.bat) -replace '\{PROJECT_PATH\}', '%PROJECT_PATH%' | Set-Content RUN_autobriefing.bat"

echo.
echo ============================================================
echo Setup completed!
echo Double-click RUN_autobriefing.bat to run automation
echo ============================================================
pause
