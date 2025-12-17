@echo off
chcp 65001 > nul
title Hyscape Automation - Windows Setup

echo ============================================================
echo Hyscape Daily Automation - Windows Environment Setup
echo ============================================================
echo.

REM Navigate to script directory
cd /d H:\부서\cjh\hyscape_daily_automation

echo Step 1/3: Installing Python dependencies...
echo.
"C:\Users\jjeor\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe" -m pip install --upgrade pip
"C:\Users\jjeor\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe" -m pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Dependency installation failed!
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Step 2/3: Verifying .env configuration...
echo ============================================================
echo.

if not exist .env (
    echo WARNING: .env file not found!
    echo Please copy .env.template to .env and configure:
    echo   - GOOGLE_API_KEY
    echo   - SENDER_EMAIL
    echo   - SENDER_PASSWORD
    echo.
    pause
    exit /b 1
) else (
    echo ✓ .env file found
)

echo.
echo ============================================================
echo Step 3/3: Creating PDF directory...
echo ============================================================
echo.

if not exist "H:\부서\cjh\pdf" (
    mkdir "H:\부서\cjh\pdf"
    echo ✓ Created: H:\부서\cjh\pdf
) else (
    echo ✓ PDF directory exists: H:\부서\cjh\pdf
)

echo.
echo ============================================================
echo Setup completed successfully!
echo ============================================================
echo.
echo Next steps:
echo 1. Ensure .env file is properly configured
echo 2. Place PDF briefing files in H:\부서\cjh\pdf\
echo 3. Run RUN_autobriefing_windows.bat to test
echo 4. Schedule with Windows Task Scheduler (see WINDOWS_DEPLOYMENT.md)
echo.
pause
