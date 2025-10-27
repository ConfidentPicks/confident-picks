@echo off
REM Setup Task Scheduler for Pick Generation and Migration
REM Run this as Administrator to create scheduled tasks

echo ========================================
echo CONFIDENT PICKS - SCHEDULER SETUP
echo ========================================
echo.

REM Get the current directory
set SCRIPT_DIR=%~dp0

echo Setting up scheduled tasks...
echo.

REM Create task for pick generation (morning)
schtasks /Create /TN "ConfidentPicks\GeneratePicks-Morning" /TR "python %SCRIPT_DIR%generate_picks_smart.py" /SC DAILY /ST 07:00 /F

echo ✓ Morning pick generation scheduled (7:00 AM)

REM Create task for pick generation (afternoon)
schtasks /Create /TN "ConfidentPicks\GeneratePicks-Afternoon" /TR "python %SCRIPT_DIR%generate_picks_smart.py" /SC DAILY /ST 14:00 /F

echo ✓ Afternoon pick generation scheduled (2:00 PM)

REM Create task for completed picks migration (every 5 minutes during active hours)
schtasks /Create /TN "ConfidentPicks\MoveCompletedPicks" /TR "python %SCRIPT_DIR%confident-picks-automation\move_completed_picks_to_scoring.py" /SC MINUTE /MO 5 /F

echo ✓ Completed picks migration scheduled (every 5 minutes)

echo.
echo ========================================
echo Scheduling setup complete!
echo ========================================
echo.
echo Tasks created:
echo   - Generate Picks (Morning) - Daily at 7:00 AM
echo   - Generate Picks (Afternoon) - Daily at 2:00 PM  
echo   - Move Completed Picks - Every 5 minutes
echo.
pause

