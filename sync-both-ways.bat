@echo off
echo.
echo ========================================
echo  Two-Way Google Sheets Sync
echo ========================================
echo.
echo What would you like to do?
echo.
echo 1. Firebase → Google Sheets (Export)
echo 2. Google Sheets → Firebase (Import)
echo 3. Both ways (Export then Import)
echo.
set /p choice="Enter your choice (1-3): "

cd confident-picks-automation

if "%choice%"=="1" (
    echo.
    echo Exporting Firebase to Google Sheets...
    node fixed-sync.js
) else if "%choice%"=="2" (
    echo.
    echo Importing Google Sheets to Firebase...
    node sheet-to-firebase.js
) else if "%choice%"=="3" (
    echo.
    echo Syncing both ways...
    echo.
    echo Step 1: Exporting Firebase to Google Sheets...
    node fixed-sync.js
    echo.
    echo Step 2: Importing Google Sheets to Firebase...
    node sheet-to-firebase.js
) else (
    echo.
    echo Invalid choice!
)

echo.
echo ========================================
echo  Operation Complete
echo ========================================
echo.
pause


