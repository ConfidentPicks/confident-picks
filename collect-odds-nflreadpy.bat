@echo off
echo.
echo ========================================
echo  Live NFL Odds Collection (nflreadpy)
echo ========================================
echo.
echo This will collect live NFL odds using nflreadpy and update your Google Sheet.
echo.
echo Requirements:
echo - Python installed
echo - nflreadpy package (pip install nflreadpy)
echo.
echo The odds will be updated in the "Live_Odds" sheet.
echo You can use this data in other sheets for predictions.
echo.
pause

cd confident-picks-automation

echo.
echo Collecting live NFL odds...
node collect-odds-nflreadpy.js

echo.
echo ========================================
echo  Odds Collection Complete
echo ========================================
echo.
echo Check your Google Sheet for updated odds data!
echo.
pause


