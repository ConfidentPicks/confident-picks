@echo off
echo ========================================
echo RESTARTING NFL TRAINING SCRIPTS
echo ========================================
echo.

echo Killing old Python processes...
taskkill /F /IM python.exe >nul 2>&1

echo.
echo Waiting 2 seconds...
timeout /t 2 /nobreak >nul

echo.
echo Starting NFL training scripts...
echo.

cd confident-picks-automation

echo [1/3] Starting NFL Spread...
start "NFL Spread Training" cmd /k "python nfl_spread_exhaustive_test.py"
timeout /t 1 /nobreak >nul

echo [2/3] Starting NFL Total...
start "NFL Total Training" cmd /k "python nfl_total_exhaustive_test.py"
timeout /t 1 /nobreak >nul

echo [3/3] Starting NFL Moneyline...
start "NFL Moneyline Training" cmd /k "python nfl_moneyline_exhaustive_test.py"

cd ..

echo.
echo ========================================
echo ALL NFL SCRIPTS STARTED!
echo ========================================
echo.
echo Check the 3 new windows to see progress.
echo Each script will save models to Firebase as it finds them.
echo.
echo Press any key to close this window...
pause >nul

