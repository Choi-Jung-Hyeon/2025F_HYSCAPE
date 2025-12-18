# Hyscape Daily Briefing - Task Scheduler Setup Script
# This script creates a scheduled task to run the daily briefing at 9 AM on weekdays

# Requires Administrator privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "This script requires Administrator privileges!"
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Red
    pause
    exit
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Hyscape Daily Briefing - Task Scheduler Setup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Get the current directory (where this script is located)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BatchFilePath = Join-Path $ScriptDir "RUN_autobriefing.bat"

# Verify the batch file exists
if (-Not (Test-Path $BatchFilePath)) {
    Write-Host "ERROR: RUN_autobriefing.bat not found at: $BatchFilePath" -ForegroundColor Red
    pause
    exit
}

Write-Host "Batch file location: $BatchFilePath" -ForegroundColor Green
Write-Host ""

# Task Scheduler settings
$TaskName = "Hyscape_Daily_Briefing"
$TaskDescription = "Hyscape 일일 브리핑 자동화 - 평일 오전 9시 실행"

# Check if task already exists
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($ExistingTask) {
    Write-Host "WARNING: Task '$TaskName' already exists!" -ForegroundColor Yellow
    $Response = Read-Host "Do you want to replace it? (Y/N)"
    if ($Response -ne "Y" -and $Response -ne "y") {
        Write-Host "Setup cancelled." -ForegroundColor Yellow
        pause
        exit
    }
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Existing task removed." -ForegroundColor Yellow
    Write-Host ""
}

# Create the action (run the batch file)
$Action = New-ScheduledTaskAction -Execute $BatchFilePath

# Create triggers for each weekday at 9:00 AM
$Triggers = @()

# Monday to Friday (DaysOfWeek uses English day names)
$DaysOfWeek = @('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday')
foreach ($Day in $DaysOfWeek) {
    $Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $Day -At 9:00AM
    $Triggers += $Trigger
}

# Create principal (run with highest privileges)
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest

# Create settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# Register the scheduled task
try {
    $Task = Register-ScheduledTask `
        -TaskName $TaskName `
        -Description $TaskDescription `
        -Action $Action `
        -Trigger $Triggers `
        -Principal $Principal `
        -Settings $Settings

    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "SUCCESS: Scheduled task created!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor Cyan
    Write-Host "  Name: $TaskName" -ForegroundColor White
    Write-Host "  Schedule: Monday-Friday at 9:00 AM" -ForegroundColor White
    Write-Host "  Script: $BatchFilePath" -ForegroundColor White
    Write-Host ""
    Write-Host "You can manage this task in:" -ForegroundColor Yellow
    Write-Host "  Task Scheduler -> Task Scheduler Library -> $TaskName" -ForegroundColor White
    Write-Host ""

    # Ask if user wants to test the task now
    $TestNow = Read-Host "Do you want to test the task now? (Y/N)"
    if ($TestNow -eq "Y" -or $TestNow -eq "y") {
        Write-Host ""
        Write-Host "Running task..." -ForegroundColor Cyan
        Start-ScheduledTask -TaskName $TaskName
        Write-Host "Task started. Check the output window." -ForegroundColor Green
    }
}
catch {
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "ERROR: Failed to create scheduled task!" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "Error details: $_" -ForegroundColor Red
}

Write-Host ""
pause
