@echo off
REM Run Pick Workflow
REM This batch file runs the complete pick workflow

echo ========================================
echo CONFIDENT PICKS - WORKFLOW RUNNER
echo ========================================
echo.

REM Change to the script directory
cd confident-picks-automation

echo [1/3] Moving completed picks to scoring...
python move_completed_picks_to_scoring.py

echo.
echo [2/3] Generating new picks...
cd ..
python generate_picks_smart.py

echo.
echo ========================================
echo Workflow complete!
echo ========================================
pause

