@echo off
echo ========================================
echo  COMPLETE NFL PREDICTION UPDATE
echo ========================================
echo.
echo Running all 3 prediction models:
echo  1. Winner Predictions
echo  2. Spread Cover Predictions
echo  3. Total Predictions
echo.

cd /d "%~dp0"

python confident-picks-automation/run_all_models.py

echo.
echo ========================================
echo  Update Complete!
echo ========================================
echo.
pause


