@echo off
echo.
echo ========================================
echo  Live Odds Collection
echo ========================================
echo.
echo This will collect live betting odds and update your Google Sheet.
echo.
echo The odds will be updated in the "Live_Odds" sheet.
echo You can use this data in other sheets for predictions.
echo.
pause

cd confident-picks-automation

echo.
echo Collecting live odds...
node collect-odds.js

echo.
echo ========================================
echo  Odds Collection Complete
echo ========================================
echo.
echo Check your Google Sheet for updated odds data!
echo.
pause


