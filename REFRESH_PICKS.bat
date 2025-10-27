@echo off
echo ========================================
echo REFRESH PICKS SYSTEM
echo ========================================
echo.
echo This will:
echo   1. Clear old/incorrect picks from Firebase
echo   2. Generate fresh picks from approved models
echo.
pause

echo.
echo ========================================
echo STEP 1: Clearing old picks...
echo ========================================
python clear_old_picks.py

echo.
echo ========================================
echo STEP 2: Generating new picks...
echo ========================================
python generate_picks_from_models.py

echo.
echo ========================================
echo DONE!
echo ========================================
echo.
echo Check your app - you should see fresh picks!
echo.
pause

