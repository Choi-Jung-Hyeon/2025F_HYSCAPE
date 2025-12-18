# Hyscape Daily Briefing - Remove Scheduled Task Script

# Requires Administrator privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "This script requires Administrator privileges!"
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Red
    pause
    exit
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Hyscape Daily Briefing - Remove Scheduled Task" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$TaskName = "Hyscape_Daily_Briefing"

# Check if task exists
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if (-Not $ExistingTask) {
    Write-Host "Task '$TaskName' does not exist." -ForegroundColor Yellow
    Write-Host "Nothing to remove." -ForegroundColor Yellow
    pause
    exit
}

Write-Host "Found scheduled task: $TaskName" -ForegroundColor Yellow
$Response = Read-Host "Are you sure you want to remove this task? (Y/N)"

if ($Response -eq "Y" -or $Response -eq "y") {
    try {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host ""
        Write-Host "============================================================" -ForegroundColor Green
        Write-Host "SUCCESS: Scheduled task removed!" -ForegroundColor Green
        Write-Host "============================================================" -ForegroundColor Green
    }
    catch {
        Write-Host ""
        Write-Host "============================================================" -ForegroundColor Red
        Write-Host "ERROR: Failed to remove scheduled task!" -ForegroundColor Red
        Write-Host "============================================================" -ForegroundColor Red
        Write-Host "Error details: $_" -ForegroundColor Red
    }
}
else {
    Write-Host "Operation cancelled." -ForegroundColor Yellow
}

Write-Host ""
pause
