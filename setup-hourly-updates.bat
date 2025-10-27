@echo off
echo.
echo ========================================
echo  Hourly NFL Data Auto-Update Setup
echo ========================================
echo.
echo This will set up automatic hourly updates for:
echo - Betting odds (spreads, totals, moneylines)
echo - Game results (scores, outcomes)
echo - Weather conditions (temp, wind)
echo - Roster changes (QBs)
echo.
echo Your custom columns will be preserved!
echo.
pause

echo.
echo Setting up hourly task...

schtasks /create /tn "NFL-Hourly-Update" /tr "cmd /c cd /d %~dp0confident-picks-automation && node update-game-data.js" /sc hourly /st 00:00 /f

if errorlevel 1 (
    echo.
    echo ❌ Failed to create scheduled task
    echo Please run this script as Administrator
    pause
    exit /b 1
)

echo.
echo ========================================
echo  ✅ Hourly Updates Configured!
echo ========================================
echo.
echo Task Name: NFL-Hourly-Update
echo Frequency: Every hour
echo.
echo What gets updated:
echo - Betting odds (constantly changing)
echo - Game scores (during/after games)
echo - Weather data (closer to game time)
echo - QB changes (roster updates)
echo.
echo What's preserved:
echo - All your custom columns
echo - All your formulas
echo - All your data in columns AU+
echo.
echo To manage your scheduled task:
echo - View: Task Scheduler (taskschd.msc)
echo - Delete: schtasks /delete /tn "NFL-Hourly-Update" /f
echo - Run now: schtasks /run /tn "NFL-Hourly-Update"
echo.
echo 🎉 Your data will now update automatically every hour!
echo.
pause


