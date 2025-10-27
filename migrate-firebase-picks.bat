@echo off
echo ========================================
echo  🔄 MIGRATE FIREBASE PICKS
echo ========================================
echo.
echo This will:
echo  1. Check upcoming_picks for games with odds
echo  2. Check live_picks for games with results
echo  3. Move picks to correct collections
echo  4. Calculate W/L for completed games
echo.
pause

cd /d "%~dp0"
cd confident-picks-automation

node migrate-picks-between-collections.js

echo.
echo ========================================
echo  Migration Complete!
echo ========================================
echo.
pause

