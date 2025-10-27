# NBA Data Collection Setup

## Overview
This system fetches NBA historical data (2021-2024) and current season (2024-25) data from ESPN API and writes it to Google Sheets.

## Files Created
1. **`confident-picks-automation/nba_data_fetcher.py`** - Main data collection script
2. **`confident-picks-automation/monitor_nba_fetch.py`** - Real-time progress monitor
3. **`nba_fetch_progress.json`** - Progress tracking file (auto-generated)

## Google Sheet Structure
The script creates 3 tabs in your NBA sheet:

1. **Historical_Games** - All games from 2021-22, 2022-23, 2023-24 seasons (~3,690 games)
2. **Current_Season** - 2024-25 season games (in progress)
3. **Upcoming_Games** - For future odds and predictions (populated later)

## Data Fields Collected
Each game includes:
- **Basic Info:** game_id, date, season, home_team, away_team
- **Scores:** home_score, away_score, completed status
- **Shooting Stats:** FG%, 3PT%, FT% for both teams
- **Box Score:** rebounds, assists, turnovers, steals, blocks for both teams

## How to Run

### Step 1: Start the Data Fetcher (runs in background)
```powershell
cd C:\Users\durel\Documents\confident-picks-restored
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python confident-picks-automation\nba_data_fetcher.py" -WindowStyle Minimized
```

### Step 2: Monitor Progress (optional, in new window)
```powershell
cd C:\Users\durel\Documents\confident-picks-restored
python confident-picks-automation\monitor_nba_fetch.py
```

## Expected Timeline
- **Historical Data (2021-2024):** ~1.5-2 hours
  - 3 seasons × ~1,230 games each = ~3,690 games
  - Rate limited to avoid API throttling
- **Current Season (2024-25):** ~15-30 minutes
  - ~200-300 games so far this season

**Total Time:** ~2 hours

## Progress Monitoring
The monitor displays:
- Current status (Starting, Fetching, Writing, Completed)
- Current season being fetched
- Progress bar with percentage
- Games fetched count
- Last update timestamp

## After Completion
Once data collection is complete:
1. ✅ Historical data will be in `Historical_Games` tab
2. ✅ Current season data will be in `Current_Season` tab
3. ✅ Ready for model training (next step)

## Next Steps (After Data Collection)
1. **Feature Engineering** - Calculate team stats, rolling averages, form
2. **Model Training** - Build Moneyline, Spread, Total models
3. **Exhaustive Testing** - Find 70%+ accuracy models for each team
4. **Integration** - Add to unified pick generator and dashboard

## Troubleshooting

### If the fetcher stops or errors:
1. Check `nba_fetch_progress.json` for error message
2. Re-run the fetcher - it will continue from where it left off
3. Check Google Sheet permissions (service account needs Editor access)

### If no data appears in sheet:
1. Verify Sheet ID: `1Hel-NsCxmk07nM0AH4VkJFB9hSK23X7XOxtA4wyRNRo`
2. Verify service account has Editor access
3. Check for API rate limiting (wait 5 minutes and retry)

## API Sources
- **Game Data:** ESPN NBA Scoreboard API
- **Odds Data:** Odds API (integrated later for upcoming games)

## Notes
- ESPN API is free and doesn't require authentication
- Rate limited to 0.5 seconds between requests to be respectful
- All 30 NBA teams supported
- Includes regular season games only (playoffs can be added later)

