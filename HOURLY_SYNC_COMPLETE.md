# ✅ Hourly Auto-Sync Complete!

## 🎉 What's Now Running Every Hour

Your system now automatically:

### 1️⃣ Updates `upcoming_games` Sheet
- **Betting odds** (spreads, totals, moneylines)
- **Game results** (scores, outcomes)
- **Weather conditions** (temp, wind)
- **Roster changes** (QBs)
- **Timestamp notification** in columns BD-BF

### 2️⃣ Syncs to `live_picks_sheets` Sheet
- **164 uncompleted games** (games without final scores)
- **Matchup column** added ("AWAY @ HOME" format)
- **All betting odds** columns
- **Future picks columns** for your predictions:
  - `my_moneyline_pick`
  - `my_spread_pick`
  - `my_total_pick`
  - `pick_confidence`
  - `pick_reasoning`
  - `bet_size`
  - `expected_value`
- **Timestamp notification** in columns AH-AJ

### 3️⃣ Updates Firebase `picks` Collection
- **164 picks** synced to Firebase
- Ready for your app to display
- Full game data included

---

## 📊 Columns in `live_picks_sheets`

### Game Information (Columns A-G):
| Column | Field | Description |
|--------|-------|-------------|
| A | game_id | Unique game identifier |
| B | matchup | "AWAY @ HOME" format |
| C | week | Week number |
| D | gameday | Game date |
| E | gametime | Game time |
| F | away_team | Away team |
| G | home_team | Home team |

### Betting Odds (Columns H-N):
| Column | Field | Description |
|--------|-------|-------------|
| H | spread_line | Point spread |
| I | away_spread_odds | Away spread odds |
| J | home_spread_odds | Home spread odds |
| K | total_line | Over/under total |
| L | over_odds | Over odds |
| M | under_odds | Under odds |
| N | away_moneyline | Away ML |
| O | home_moneyline | Home ML |

### Game Environment (Columns P-T):
| Column | Field | Description |
|--------|-------|-------------|
| P | location | City |
| Q | stadium | Stadium name |
| R | roof | Dome/Open/Retractable |
| S | surface | Grass/Turf |
| T | temp | Temperature |
| U | wind | Wind speed |

### Personnel (Columns V-Y):
| Column | Field | Description |
|--------|-------|-------------|
| V | away_qb_name | Away QB |
| W | home_qb_name | Home QB |
| X | away_coach | Away coach |
| Y | home_coach | Home coach |
| Z | referee | Referee |

### 🎯 YOUR PICKS (Columns AA-AG):
| Column | Field | What to Enter |
|--------|-------|---------------|
| AA | my_moneyline_pick | Your ML pick (AWAY/HOME) |
| AB | my_spread_pick | Your spread pick (AWAY/HOME) |
| AC | my_total_pick | Your total pick (OVER/UNDER) |
| AD | pick_confidence | Confidence % (0-100) |
| AE | pick_reasoning | Why this pick? |
| AF | bet_size | Units to bet |
| AG | expected_value | Expected value calculation |

### ⏰ Status (Columns AH-AI):
| Column | Field | Description |
|--------|-------|-------------|
| AH | Last Synced | Timestamp of last sync |
| AI | Timestamp | Actual timestamp |
| AJ | Next Update | Next sync time |

---

## 🔥 Firebase Structure

Each pick in Firebase has:

```javascript
{
  id: "2025_18_BUF_KC",
  league: "NFL",
  matchup: "BUF @ KC",
  week: 18,
  marketType: "spread",
  pickDesc: "BUF @ KC - Week 18",
  oddsAmerican: -110,
  modelConfidence: 0,
  commenceTime: timestamp,
  tier: "public",
  riskTag: "safe",
  reasoning: "Upcoming NFL game",
  status: "pending",
  createdAt: timestamp,
  updatedAt: timestamp,
  gameData: {
    away_team: "BUF",
    home_team: "KC",
    spread_line: -3.5,
    total_line: 52.5,
    away_moneyline: +130,
    home_moneyline: -150,
    location: "Kansas City",
    stadium: "Arrowhead Stadium",
    roof: "open",
    surface: "grass",
    temp: "45",
    wind: "10",
    away_qb: "Josh Allen",
    home_qb: "Patrick Mahomes",
    away_coach: "Sean McDermott",
    home_coach: "Andy Reid",
    referee: "Bill Vinovich"
  },
  metadata: {
    source: "nflreadpy",
    synced_from: "upcoming_games",
    last_synced: "2025-10-22T12:28:21.000Z"
  }
}
```

---

## ⏰ Hourly Update Schedule

**Task Name:** `NFL-Hourly-Update`

**What Happens Every Hour:**
1. ✅ Fetch latest NFL data from nflreadpy
2. ✅ Update `upcoming_games` with new odds, scores, weather
3. ✅ Filter for uncompleted games
4. ✅ Sync 164 games to `live_picks_sheets`
5. ✅ Push 164 picks to Firebase
6. ✅ Update timestamps on both sheets

**Next Update:** Top of every hour (00:00, 01:00, 02:00, etc.)

---

## 🎯 How to Use This

### For Making Picks:

1. **Open `live_picks_sheets` tab**
2. **Find games you want to bet on**
3. **Fill in your picks columns (AA-AG)**:
   - Enter your ML, spread, or total pick
   - Add confidence level
   - Add reasoning
   - Set bet size
4. **Odds auto-update every hour**
5. **Make adjustments as needed**

### For Tracking Performance:

1. **After games complete**, compare your picks to results
2. **Calculate W/L** based on your predictions
3. **Track expected value** vs actual returns
4. **Analyze confidence accuracy**

---

## 📱 Check Your Sheets

**Open your Google Sheet and check:**

### ✅ `upcoming_games` tab:
- 272 games (full 2025 season)
- Timestamp in columns BD-BF
- "Last Updated" shows recent time

### ✅ `live_picks_sheets` tab:
- 164 uncompleted games
- Matchup column (column B)
- Future picks columns (AA-AG)
- Timestamp in columns AH-AJ

### ✅ Firebase Console:
- Go to Firestore
- Check `picks` collection
- Should see 164 documents

---

## 🔧 Manage Your Hourly Sync

**View task status:**
```powershell
taskschd.msc
```
Look for "NFL-Hourly-Update"

**Run manually now:**
```powershell
cd confident-picks-automation
node update-game-data.js
```

**Stop automatic updates:**
```powershell
schtasks /delete /tn "NFL-Hourly-Update" /f
```

**Restart automatic updates:**
```powershell
cd ..
.\setup-hourly-updates.bat
```

---

## 🎊 Summary

You now have:
- ✅ **272 games** in `upcoming_games` (full season)
- ✅ **164 live games** in `live_picks_sheets` (uncompleted)
- ✅ **164 picks** in Firebase (ready for app)
- ✅ **Hourly auto-updates** for all data
- ✅ **Timestamps** on both sheets
- ✅ **Future picks columns** for your predictions
- ✅ **Matchup field** in "AWAY @ HOME" format

**Everything updates automatically every hour!** 🚀⏰


