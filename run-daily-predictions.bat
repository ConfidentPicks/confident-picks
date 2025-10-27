@echo off
echo ========================================
echo  DAILY PREDICTION UPDATE
echo ========================================
echo.

cd /d "%~dp0"

python confident-picks-automation/daily_prediction_update.py

echo.
echo ========================================
echo  Update Complete!
echo ========================================
echo.
pause


