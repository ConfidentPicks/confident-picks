@echo off
echo ========================================
echo  FIREBASE AUTOMATION SETUP
echo ========================================
echo.
echo This will create scheduled tasks to:
echo  1. Sync predictions to Firebase (daily at 6:00 AM)
echo  2. Migrate picks between collections (every 2 hours)
echo.
echo Tasks will run automatically in the background.
echo.
pause

:: Get the full path to the scripts
set SYNC_SCRIPT=%~dp0sync-firebase-complete.bat
set MIGRATE_SCRIPT=%~dp0migrate-firebase-picks.bat

echo.
echo Creating scheduled tasks...
echo.

:: Task 1: Daily sync at 6:00 AM
schtasks /create /tn "NFL Firebase Daily Sync" /tr "\"%SYNC_SCRIPT%\"" /sc daily /st 06:00 /f

if %errorlevel% equ 0 (
    echo ✅ Daily sync task created successfully
) else (
    echo ❌ Failed to create daily sync task
)

echo.

:: Task 2: Migration every 2 hours
schtasks /create /tn "NFL Firebase Migration" /tr "\"%MIGRATE_SCRIPT%\"" /sc hourly /mo 2 /f

if %errorlevel% equ 0 (
    echo ✅ Hourly migration task created successfully
) else (
    echo ❌ Failed to create migration task
)

echo.
echo ========================================
echo  ✅ AUTOMATION SETUP COMPLETE!
echo ========================================
echo.
echo Scheduled Tasks:
echo  1. NFL Firebase Daily Sync
echo     - Runs: Daily at 6:00 AM
echo     - Updates all predictions
echo.
echo  2. NFL Firebase Migration
echo     - Runs: Every 2 hours
echo     - Moves picks between collections
echo     - Calculates W/L for completed games
echo.
echo You can:
echo  - View tasks in Windows Task Scheduler
echo  - Run them manually anytime
echo  - Disable/modify in Task Scheduler
echo.
pause

