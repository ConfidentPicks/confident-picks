@echo off
echo ========================================
echo CLEAN PICK GENERATION WORKFLOW
echo ========================================
echo.
echo This will:
echo   1. Delete leaked NFL models (100%% accuracy)
echo   2. Clear old picks from Firebase
echo   3. Generate fresh picks (no conflicts)
echo.
pause

echo.
echo ========================================
echo STEP 1: Deleting leaked models...
echo ========================================
python delete_leaked_models.py

echo.
echo ========================================
echo STEP 2: Clearing old picks...
echo ========================================
python clear_old_picks.py

echo.
echo ========================================
echo STEP 3: Generating smart picks...
echo ========================================
python generate_picks_smart.py

echo.
echo ========================================
echo DONE!
echo ========================================
echo.
echo Check your app - you should see fresh picks with no conflicts!
echo.
pause

