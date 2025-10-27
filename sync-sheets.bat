@echo off
echo.
echo ========================================
echo  Google Sheets Sync
echo ========================================
echo.
echo What would you like to do?
echo.
echo 1. Export Firebase picks to Google Sheets
echo 2. Import Google Sheets to Firebase
echo 3. Sync both ways
echo 4. Test connection
echo.
set /p choice="Enter your choice (1-4): "

cd confident-picks-automation

if "%choice%"=="1" (
    echo.
    echo Exporting Firebase to Google Sheets...
    node sync-sheets.js --to-sheets
) else if "%choice%"=="2" (
    echo.
    echo Importing Google Sheets to Firebase...
    node sync-sheets.js --to-firebase
) else if "%choice%"=="3" (
    echo.
    echo Syncing both directions...
    node sync-sheets.js --both
) else if "%choice%"=="4" (
    echo.
    echo Testing connection...
    node test-sheets-connection.js
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



