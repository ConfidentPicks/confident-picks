@echo off
echo ========================================
echo SYNCING SHEET CHANGES TO FIREBASE
echo ========================================
echo.

cd /d "C:\Users\durel\Documents\confident-picks-restored"

echo Running Python sync script...
python confident-picks-automation\sync_sheet_to_firebase.py

echo.
echo ========================================
echo SYNC COMPLETE!
echo ========================================
echo.
echo Press any key to close...
pause > nul
