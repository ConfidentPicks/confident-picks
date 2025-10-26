@echo off
echo ========================================
echo CHECKING MODEL TRAINING STATUS
echo ========================================
echo.

echo Checking for running training scripts...
echo.

tasklist /FI "IMAGENAME eq python.exe" /FO TABLE | findstr /I "python"

echo.
echo ========================================
echo RESTARTING FAILED SCRIPTS
echo ========================================
echo.

echo Starting NFL Spread exhaustive test...
start "NFL Spread" cmd /k "cd confident-picks-automation && python nfl_spread_exhaustive_test.py"

echo Starting NFL Total exhaustive test...
start "NFL Total" cmd /k "cd confident-picks-automation && python nfl_total_exhaustive_test.py"

echo Starting NFL Moneyline exhaustive test...
start "NFL Moneyline" cmd /k "cd confident-picks-automation && python nfl_moneyline_exhaustive_test.py"

echo.
echo ========================================
echo ALL SCRIPTS RESTARTED
echo ========================================
echo.
echo Check the new windows to monitor progress.
echo.
pause

