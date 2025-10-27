@echo off
echo ========================================
echo  SETUP DAILY PREDICTION AUTOMATION
echo ========================================
echo.
echo This will create a Windows Task Scheduler task to run
echo daily predictions automatically every day at 6:00 AM.
echo.
pause

:: Get the full path to the batch file
set SCRIPT_PATH=%~dp0run-all-predictions.bat

:: Create the scheduled task
schtasks /create /tn "NFL Daily Predictions" /tr "\"%SCRIPT_PATH%\"" /sc daily /st 06:00 /f

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo  ✅ SUCCESS!
    echo ========================================
    echo.
    echo Daily prediction automation is now set up!
    echo.
    echo Task Name: NFL Daily Predictions
    echo Run Time: 6:00 AM daily
    echo Script: run-all-predictions.bat
    echo.
    echo You can:
    echo  - View the task in Windows Task Scheduler
    echo  - Run it manually anytime by double-clicking run-daily-predictions.bat
    echo  - Change the schedule in Task Scheduler if needed
    echo.
) else (
    echo.
    echo ========================================
    echo  ❌ ERROR
    echo ========================================
    echo.
    echo Failed to create scheduled task.
    echo Please try running this script as Administrator.
    echo.
)

pause

