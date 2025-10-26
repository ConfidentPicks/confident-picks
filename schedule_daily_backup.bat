@echo off
REM Schedule daily Firestore backup at 3 AM
REM Run this script as Administrator to set up the scheduled task

echo ========================================
echo Setting up Daily Firestore Backup
echo ========================================
echo.

REM Create scheduled task
schtasks /create /tn "Confident Picks - Daily Backup" /tr "python C:\Users\durel\Documents\confident-picks-restored\backup_firestore.py" /sc daily /st 03:00 /f

if %errorlevel% == 0 (
    echo.
    echo [SUCCESS] Daily backup scheduled successfully!
    echo.
    echo Task Details:
    echo - Name: Confident Picks - Daily Backup
    echo - Runs: Every day at 3:00 AM
    echo - Script: backup_firestore.py
    echo.
    echo To view the task:
    echo   schtasks /query /tn "Confident Picks - Daily Backup"
    echo.
    echo To run manually:
    echo   schtasks /run /tn "Confident Picks - Daily Backup"
    echo.
    echo To delete the task:
    echo   schtasks /delete /tn "Confident Picks - Daily Backup" /f
) else (
    echo.
    echo [ERROR] Failed to create scheduled task
    echo Please run this script as Administrator
)

echo.
pause

