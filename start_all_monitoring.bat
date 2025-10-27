@echo off
echo Starting all monitoring scripts...
echo.

cd /d "%~dp0"

start "NBA Data Fetcher" /MIN python confident-picks-automation\nba_data_fetcher.py
timeout /t 2 /nobreak >nul

start "NBA Current Season Update" /MIN python confident-picks-automation\update_nba_current_teams.py
timeout /t 2 /nobreak >nul

cd confident-picks-automation

start "NHL Moneyline Training" /MIN python nhl_moneyline_exhaustive_test.py
timeout /t 2 /nobreak >nul

start "NHL Puck Line Training" /MIN python nhl_puckline_exhaustive_test.py
timeout /t 2 /nobreak >nul

start "NFL Moneyline Training" /MIN python nfl_moneyline_exhaustive_test.py
timeout /t 2 /nobreak >nul

start "NFL Spread Training" /MIN python nfl_spread_exhaustive_test.py
timeout /t 2 /nobreak >nul

start "NFL Total Training" /MIN python nfl_total_exhaustive_test.py

echo.
echo All scripts started!
echo Check Task Manager to see running processes.
pause
