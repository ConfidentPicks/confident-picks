@echo off
echo.
echo ========================================
echo  GitHub Sync
echo ========================================
echo.
echo What would you like to do?
echo.
echo 1. Export Firebase picks to GitHub
echo 2. Import GitHub picks to Firebase
echo 3. Sync both ways
echo.
set /p choice="Enter your choice (1-3): "

cd confident-picks-automation

if "%choice%"=="1" (
    echo.
    echo Exporting Firebase to GitHub...
    node sync-github.js --to-github
) else if "%choice%"=="2" (
    echo.
    echo Importing GitHub to Firebase...
    node sync-github.js --to-firebase
) else if "%choice%"=="3" (
    echo.
    echo Syncing both directions...
    node sync-github.js --both
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


