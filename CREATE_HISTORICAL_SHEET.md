# 📊 Create Historical Data Spreadsheet

## 🎯 Goal
Move 2021-2024 historical data to a new spreadsheet to free up space in your current sheet for 2025 live updates.

## 📋 Step-by-Step Instructions

### Step 1: Create New Spreadsheet
1. **Go to Google Sheets:** https://sheets.google.com
2. **Click "Blank" to create a new spreadsheet**
3. **Rename it:** "NFL Historical Data (2021-2024)"

### Step 2: Share with Service Account
1. **Click "Share" button** (top right)
2. **Add this email:** `firebase-adminsdk-fbsvc@confident-picks-app-8-25.iam.gserviceaccount.com`
3. **Set permission:** Editor
4. **Click "Send"**

### Step 3: Get the Spreadsheet ID
1. **Look at the URL** of your new sheet
2. **Copy the ID** (the long string between `/d/` and `/edit`)
   - Example: `https://docs.google.com/spreadsheets/d/COPY_THIS_PART/edit`
3. **Save this ID** - we'll need it!

### Step 4: Run the Transfer Script
Once you have the new spreadsheet ID, paste it here and I'll transfer the data!

---

## 🔄 What Will Be Transferred

From **My_NFL_Betting_Data1** → **NFL Historical Data (2021-2024)**:
- `player_stats_2021` (18,969 records)
- `player_stats_2022` (18,831 records)
- `player_stats_2023` (18,643 records)
- `player_stats_2024` (18,981 records)

**Total:** 75,424 player game records

---

## 📊 After Transfer

### Historical Spreadsheet (2021-2024):
- Historical player stats
- Static data (won't change)
- Perfect for model training

### Current Spreadsheet (My_NFL_Betting_Data1):
- `upcoming_games` - 2025 full season
- `live_picks_sheets` - Live games
- `player_info` - All players
- `active_players_props` - Active players
- Space to add `player_stats_2025` (7,398 records)
- Space to add team stats, game results, etc.

---

## 🚀 Ready?

**Create the new spreadsheet, share it with the service account, and give me the ID!**

Then I'll automatically transfer all the historical data for you! 🎯


