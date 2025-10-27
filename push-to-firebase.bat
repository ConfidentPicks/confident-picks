@echo off
echo ========================================
echo  🏈 PUSH NFL PICKS TO FIREBASE
echo ========================================
echo.
echo This will:
echo  1. Read predictions from upcoming_games sheet
echo  2. Convert to Firebase format
echo  3. Push all picks to Firebase
echo.
pause

cd /d "%~dp0"
cd confident-picks-automation

node push-nfl-picks-to-firebase.js

echo.
echo ========================================
echo  Push Complete!
echo ========================================
echo.
pause

