@echo off
echo.
echo ========================================
echo  NFL Historical Data Download
echo ========================================
echo.
echo This will download 3-5 years of NFL data (2021-2024).
echo.
echo This will create separate sheets for each year:
echo - NFL_Schedule_2021, NFL_Schedule_2022, etc.
echo - NFL_TeamStats_2021, NFL_TeamStats_2022, etc.
echo.
echo This may take several minutes to complete.
echo.
pause

cd confident-picks-automation

echo.
echo Downloading historical NFL data...
node download-nfl-data.js

echo.
echo ========================================
echo  NFL Data Download Complete
echo ========================================
echo.
echo Check your Google Sheet for historical data!
echo Use this data to build prediction models.
echo.
pause


