@echo off
echo ========================================
echo RESTARTING ALL MODEL TRAINING
echo ========================================
echo.

echo Killing all Python processes...
taskkill /F /IM python.exe >nul 2>&1

echo Waiting 3 seconds...
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo STARTING ALL TRAINING SCRIPTS
echo ========================================
echo.

echo [1/4] Starting NHL Puck Line...
start "NHL Puck Line" cmd /k "cd confident-picks-automation && python nhl_puckline_exhaustive_test.py"
timeout /t 1 /nobreak >nul

echo [2/4] Starting NFL Spread...
start "NFL Spread" cmd /k "cd /d %~dp0 && python nfl_spread_exhaustive_test.py"
timeout /t 1 /nobreak >nul

echo [3/4] Starting NFL Total (FIXED - No more data leakage!)...
start "NFL Total" cmd /k "cd /d %~dp0 && python nfl_total_exhaustive_test.py"
timeout /t 1 /nobreak >nul

echo [4/4] Starting NFL Moneyline...
start "NFL Moneyline" cmd /k "cd /d %~dp0 && python nfl_moneyline_exhaustive_test.py"

echo.
echo ========================================
echo ALL SCRIPTS STARTED!
echo ========================================
echo.
echo 4 training windows opened:
echo   - NHL Puck Line
echo   - NFL Spread
echo   - NFL Total (DATA LEAKAGE FIXED!)
echo   - NFL Moneyline
echo.
echo Check each window for progress.
echo Models will save to Firebase as they reach 70%+ accuracy.
echo.
echo Press any key to close this window...
pause >nul

