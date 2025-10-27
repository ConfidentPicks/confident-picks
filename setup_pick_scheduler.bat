@echo off
REM Setup Task Scheduler for Pick Generation and Migration (Background)
REM Run this as Administrator to create scheduled tasks

echo ========================================
echo CONFIDENT PICKS - SCHEDULER SETUP
echo ========================================
echo.

REM Get the current directory
set SCRIPT_DIR=%~dp0

echo Setting up scheduled tasks (background, no popups)...
echo.

REM Create task for pick generation (morning) - Runs in background, no window
schtasks /Create /TN "ConfidentPicks\GeneratePicks-Morning" /TR "python %SCRIPT_DIR%generate_picks_smart.py" /SC DAILY /ST 07:00 /RL HIGHEST /F /RU "SYSTEM" /RP ""

echo ✓ Morning pick generation scheduled (7:00 AM)

REM Create task for pick generation (afternoon) - Runs in background, no window
schtasks /Create /TN "ConfidentPicks\GeneratePicks-Afternoon" /TR "python %SCRIPT_DIR%generate_picks_smart.py" /SC DAILY /ST 14:00 /RL HIGHEST /F /RU "SYSTEM" /RP ""

echo ✓ Afternoon pick generation scheduled (2:00 PM)

REM Create task for completed picks migration (every 15 minutes) - Background only
schtasks /Create /TN "ConfidentPicks\MoveCompletedPicks" /TR "python %SCRIPT_DIR%confident-picks-automation\move_completed_picks_to_scoring.py" /SC MINUTE /MO 15 /RL HIGHEST /F /RU "SYSTEM" /RP ""

echo ✓ Completed picks migration scheduled (every 15 minutes, background)

echo.
echo ========================================
echo Scheduling setup complete!
echo ========================================
echo.
echo Tasks created (all run in background, no popups):
echo   - Generate Picks (Morning) - Daily at 7:00 AM
echo   - Generate Picks (Afternoon) - Daily at 2:00 PM  
echo   - Move Completed Picks - Every 15 minutes
echo.
echo All tasks run silently in the background!
echo.
pause

