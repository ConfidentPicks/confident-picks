@echo off
echo.
echo ========================================
echo  Auto-Sync Setup for Windows
echo ========================================
echo.
echo This will help you set up automatic syncing.
echo.
echo Choose your sync frequency:
echo.
echo 1. Every hour
echo 2. Every 6 hours  
echo 3. Every day at 9 AM
echo 4. Every day at 6 PM
echo 5. Custom schedule
echo.
set /p choice="Enter your choice (1-5): "

cd confident-picks-automation

if "%choice%"=="1" (
    echo.
    echo Setting up hourly sync...
    schtasks /create /tn "ConfidentPicks-Sync" /tr "cd /d %cd% && node sheet-to-firebase.js" /sc hourly /f
    echo ✅ Hourly sync scheduled!
) else if "%choice%"=="2" (
    echo.
    echo Setting up 6-hourly sync...
    schtasks /create /tn "ConfidentPicks-Sync" /tr "cd /d %cd% && node sheet-to-firebase.js" /sc minute /mo 360 /f
    echo ✅ 6-hourly sync scheduled!
) else if "%choice%"=="3" (
    echo.
    echo Setting up daily sync at 9 AM...
    schtasks /create /tn "ConfidentPicks-Sync" /tr "cd /d %cd% && node sheet-to-firebase.js" /sc daily /st 09:00 /f
    echo ✅ Daily 9 AM sync scheduled!
) else if "%choice%"=="4" (
    echo.
    echo Setting up daily sync at 6 PM...
    schtasks /create /tn "ConfidentPicks-Sync" /tr "cd /d %cd% && node sheet-to-firebase.js" /sc daily /st 18:00 /f
    echo ✅ Daily 6 PM sync scheduled!
) else if "%choice%"=="5" (
    echo.
    echo For custom schedule, you'll need to use Task Scheduler manually.
    echo.
    echo Steps:
    echo 1. Open Task Scheduler (taskschd.msc)
    echo 2. Create Basic Task
    echo 3. Set your schedule
    echo 4. Action: Start a program
    echo 5. Program: cmd.exe
    echo 6. Arguments: /c "cd /d %cd% && node sheet-to-firebase.js"
    echo.
    pause
) else (
    echo Invalid choice!
)

echo.
echo ========================================
echo  Auto-Sync Setup Complete
echo ========================================
echo.
echo To manage your scheduled task:
echo - View: Task Scheduler (taskschd.msc)
echo - Delete: schtasks /delete /tn "ConfidentPicks-Sync" /f
echo.
pause


