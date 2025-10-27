@echo off
echo ========================================
echo  🏈 COMPLETE FIREBASE SYNC
echo ========================================
echo.
echo This will:
echo  1. Push all predictions to Firebase
echo  2. Organize into correct collections
echo  3. Migrate picks as game status changes
echo  4. Calculate W/L for completed games
echo.
pause

cd /d "%~dp0"
cd confident-picks-automation

node sync-and-migrate-firebase.js

echo.
echo ========================================
echo  Sync Complete!
echo ========================================
echo.
pause

