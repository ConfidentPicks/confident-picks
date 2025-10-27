@echo off
echo ================================================================================
echo LAUNCHING ALL MODEL TRAINING SCRIPTS
echo ================================================================================
echo.
echo This will open 3 new PowerShell windows for:
echo   1. NHL Puck Line Training
echo   2. NFL Spread Training (coming soon)
echo   3. NFL Total Training (coming soon)
echo.
echo NHL Moneyline is already running in your current terminal.
echo.
echo Press any key to launch NHL Puck Line training...
pause >nul

cd /d "%~dp0"

echo.
echo [1/3] Launching NHL Puck Line Training...
start powershell -NoExit -Command "cd '%CD%'; python confident-picks-automation\nhl_puckline_exhaustive_test.py"

echo [2/3] NFL Spread Training - Script creation in progress...
echo [3/3] NFL Total Training - Script creation in progress...

echo.
echo ================================================================================
echo LAUNCH COMPLETE!
echo ================================================================================
echo.
echo Monitor progress:
echo   - Open model_performance_dashboard.html in your browser
echo   - Check JSON files: nhl_puckline_progress.json
echo.
echo Press any key to exit...
pause >nul

