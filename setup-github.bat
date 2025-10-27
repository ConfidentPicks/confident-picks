@echo off
echo.
echo ========================================
echo  GitHub Integration Setup
echo ========================================
echo.
echo This will help you connect GitHub to your Firebase project.
echo.
echo You'll need a GitHub Personal Access Token.
echo Get one here: https://github.com/settings/tokens
echo.
pause

cd confident-picks-automation

echo.
echo Installing dependencies...
call npm install @octokit/rest
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies.
    echo Please make sure Node.js is installed.
    pause
    exit /b 1
)

echo.
echo Running GitHub setup wizard...
node setup-github.js

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Run: sync-github.bat
echo   2. Check your GitHub repository
echo.
pause


