@echo off
echo.
echo ========================================
echo  Google Sheets Setup for Firebase
echo ========================================
echo.
echo This will help you connect Google Sheets to your Firebase project.
echo.
pause

cd confident-picks-automation

echo.
echo Installing dependencies...
call npm install
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies.
    echo Please make sure Node.js is installed.
    pause
    exit /b 1
)

echo.
echo Running setup wizard...
node setup-google-sheets.js

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Run: sync-sheets.bat
echo   2. Check your Google Sheet for data
echo.
pause



