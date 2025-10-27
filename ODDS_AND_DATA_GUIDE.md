# 🎯 Live Odds & Historical Data System

You now have a complete system for **automatic odds updates** and **historical NFL data collection**!

## 🎯 What You Get

### 📊 Live Odds Collection
- ✅ **Automatic odds updates** - Every 2 hours via cron job
- ✅ **Multiple sources** - DraftKings, FanDuel, The Odds API
- ✅ **Real-time data** - Always current betting odds
- ✅ **Google Sheets integration** - Updates your "Live_Odds" sheet

### 🏈 Historical NFL Data
- ✅ **3-5 years of data** - 2021-2024 seasons
- ✅ **Complete datasets** - Schedules, team stats, player stats
- ✅ **Model building ready** - Perfect for training AI models
- ✅ **Separate sheets** - Organized by year and data type

---

## 🚀 Quick Start

### 1. Collect Live Odds (Manual)
```powershell
.\collect-odds.bat
```
**Or:**
```powershell
cd confident-picks-automation
node collect-odds.js
```

### 2. Download Historical Data (One-time)
```powershell
.\download-nfl-data.bat
```
**Or:**
```powershell
cd confident-picks-automation
node download-nfl-data.js
```

### 3. Set Up Automatic Odds Updates
The system is already configured to update odds every 2 hours automatically when deployed to Vercel.

---

## 📊 Google Sheets Structure

After running both scripts, your Google Sheet will have:

### Live Data Sheets:
- **`Live_Odds`** - Current betting odds from multiple sources
- **`live_picks_sheets`** - Your existing picks data

### Historical Data Sheets:
- **`NFL_Schedule_2021`** - Complete 2021 season schedule
- **`NFL_Schedule_2022`** - Complete 2022 season schedule  
- **`NFL_Schedule_2023`** - Complete 2023 season schedule
- **`NFL_Schedule_2024`** - Complete 2024 season schedule
- **`NFL_TeamStats_2021`** - Team statistics for 2021
- **`NFL_TeamStats_2022`** - Team statistics for 2022
- **`NFL_TeamStats_2023`** - Team statistics for 2023
- **`NFL_TeamStats_2024`** - Team statistics for 2024

---

## 🎯 Live Odds Sheet Format

The `Live_Odds` sheet contains:

| Column | Description | Example |
|--------|-------------|---------|
| Game ID | Unique identifier | `dk_001` |
| Home Team | Home team name | `Kansas City Chiefs` |
| Away Team | Away team name | `Buffalo Bills` |
| Game Date | Game start time | `Oct 22, 2025 1:00 PM` |
| DK Spread | DraftKings spread | `-3.5` |
| DK Spread Odds | DraftKings spread odds | `-110` |
| FD Spread | FanDuel spread | `-3.5` |
| FD Spread Odds | FanDuel spread odds | `-108` |
| DK Total | DraftKings total | `52.5` |
| DK Total Odds | DraftKings total odds | `-110` |
| FD Total | FanDuel total | `52.5` |
| FD Total Odds | FanDuel total odds | `-108` |
| Last Updated | When data was collected | `2025-10-22T12:00:00Z` |

---

## 🏈 Historical Data Sheet Format

The historical sheets contain:

### Schedule Data:
- Game IDs, dates, teams
- Scores, spreads, totals
- Money lines, over/under
- Team statistics per game

### Team Stats Data:
- Passing, rushing, receiving stats
- Defensive statistics
- Special teams data
- Penalties, turnovers, time of possession

---

## 🔄 Automatic Updates

### Odds Collection (Every 2 Hours)
- **Schedule:** `0 */2 * * *` (every 2 hours)
- **Function:** `/api/collect-odds`
- **Updates:** `Live_Odds` sheet

### Picks Sync (Every 6 Hours)
- **Schedule:** `0 */6 * * *` (every 6 hours)
- **Function:** `/api/auto-sync`
- **Updates:** Firebase from Google Sheets

---

## 💡 How to Use This Data

### For Prediction Making:
1. **Use Live_Odds sheet** - Get current betting lines
2. **Reference historical data** - Analyze past performance
3. **Create formulas** - Calculate value bets
4. **Build models** - Use historical data for training

### For Displaying Picks:
1. **Import odds data** - Use current lines in your picks
2. **Compare sources** - Find best odds across books
3. **Track movement** - Monitor line changes
4. **Validate picks** - Check against market consensus

### For Model Building:
1. **Historical analysis** - Use 2021-2024 data
2. **Feature engineering** - Create predictive variables
3. **Performance validation** - Test against past outcomes
4. **Trend analysis** - Identify patterns and tendencies

---

## 🔧 API Endpoints

### Manual Triggers:
```bash
# Collect live odds
curl -X POST https://your-domain.vercel.app/api/collect-odds

# Download historical data
curl -X POST https://your-domain.vercel.app/api/download-nfl-data

# Sync picks
curl -X POST https://your-domain.vercel.app/api/auto-sync
```

### Automatic Schedules:
- **Odds collection:** Every 2 hours
- **Picks sync:** Every 6 hours
- **Historical data:** One-time download

---

## 🛠️ Setup Requirements

### API Keys Needed:
1. **The Odds API** - Free tier available at https://the-odds-api.com/
2. **SportsData API** - For historical NFL data
3. **Google Sheets API** - Already enabled
4. **Firebase credentials** - Already configured

### Environment Variables:
```bash
# Odds collection
ODDS_API_KEY=your-odds-api-key

# Historical data
SPORTSDATA_API_KEY=your-sportsdata-api-key

# Google Sheets
GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id

# Firebase (already configured)
FIREBASE_PROJECT_ID=confident-picks-app-8-25
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-service-account-email
```

---

## 📈 Use Cases

### 1. Real-Time Odds Monitoring
- Track line movements
- Find value bets
- Compare across sportsbooks
- Monitor market consensus

### 2. Historical Analysis
- Analyze team performance trends
- Identify seasonal patterns
- Study home/away splits
- Track injury impacts

### 3. Model Development
- Train machine learning models
- Validate prediction accuracy
- Test different strategies
- Optimize betting systems

### 4. Pick Generation
- Use current odds for picks
- Reference historical data
- Apply statistical models
- Validate against market

---

## 🎯 Next Steps

### Immediate:
1. **Run odds collection** - `.\collect-odds.bat`
2. **Download historical data** - `.\download-nfl-data.bat`
3. **Check your Google Sheet** - Verify data is there

### Short Term:
1. **Set up API keys** - Get free keys for odds and data
2. **Deploy to Vercel** - Enable automatic updates
3. **Create analysis sheets** - Build formulas and charts

### Long Term:
1. **Build prediction models** - Use historical data
2. **Automate pick generation** - Combine odds and models
3. **Track performance** - Validate against outcomes
4. **Optimize strategies** - Improve accuracy over time

---

## 🔧 Troubleshooting

### Odds Collection Issues:
- **No data:** Check API keys and internet connection
- **Wrong format:** Verify sheet structure and permissions
- **Rate limits:** Check API quota and usage

### Historical Data Issues:
- **Missing years:** Verify API keys and data availability
- **Incomplete data:** Check for API errors and retry
- **Sheet errors:** Verify Google Sheets permissions

### General Issues:
- **Authentication:** Check Firebase and Google Sheets credentials
- **Permissions:** Verify sheet sharing with service account
- **API limits:** Monitor usage and upgrade if needed

---

## ✨ Summary

**You now have a complete data pipeline:**

1. **Live odds collection** - Automatic updates every 2 hours
2. **Historical data** - 3-5 years of NFL data for analysis
3. **Google Sheets integration** - All data in one place
4. **Automated workflows** - Set it and forget it
5. **Model building ready** - Perfect for AI development

**This gives you everything you need for professional-grade sports betting analysis!**

---

👉 **Ready to start?** Run `.\collect-odds.bat` and `.\download-nfl-data.bat` to get your data!


