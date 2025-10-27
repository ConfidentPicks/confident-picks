# 🏀 NBA Data Collection Setup

## 🎯 **Task 3: NBA Data Collection (2 hours)**

---

## 📋 **Prerequisites**

- ✅ Google Sheets API access (already have this)
- ✅ Service account credentials (already have this)
- ✅ Python environment (already set up)

---

## 🚀 **Step-by-Step Setup**

### **Step 1: Create NBA Google Sheet (5 minutes)**

1. **Go to Google Sheets:**
   - Open: https://sheets.google.com
   - Click "Blank" to create new spreadsheet

2. **Name the Sheet:**
   - Title: `NBA Prediction Data`

3. **Create Tabs:**
   - Rename "Sheet1" to: `Historical_Games`
   - Add new sheet: `Current_Season`
   - Add new sheet: `Upcoming_Games`

4. **Copy Spreadsheet ID:**
   - Look at the URL: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit`
   - Copy the ID (long string between `/d/` and `/edit`)

5. **Share with Service Account:**
   - Click "Share" button
   - Add email: `firebase-adminsdk-fbsvc@confident-picks-app-8-25.iam.gserviceaccount.com`
   - Give "Editor" access
   - Click "Send"

---

### **Step 2: Update the Script (2 minutes)**

1. **Open the script:**
   - File: `confident-picks-automation/nba_data_fetcher.py`

2. **Find this line (line 17):**
   ```python
   NBA_SPREADSHEET_ID = 'YOUR_NBA_SHEET_ID_HERE'
   ```

3. **Replace with your ID:**
   ```python
   NBA_SPREADSHEET_ID = 'YOUR_ACTUAL_SPREADSHEET_ID'
   ```

4. **Save the file**

---

### **Step 3: Run the Data Collection (2 hours)**

1. **Open PowerShell in your project directory:**
   ```powershell
   cd C:\Users\durel\Documents\confident-picks-restored
   ```

2. **Run the script:**
   ```powershell
   python confident-picks-automation\nba_data_fetcher.py
   ```

3. **What it does:**
   - Fetches NBA games from ESPN API
   - Collects data for 2021-22, 2022-23, 2023-24 seasons
   - Collects current 2024-25 season games
   - Uploads to your Google Sheet
   - Shows progress every 30 days

4. **Expected output:**
   ```
   ================================================================================
   NBA DATA COLLECTION SCRIPT
   ================================================================================
   
   ================================================================================
   FETCHING NBA DATA FOR 2021-2022 SEASON
   ================================================================================
   
   Processed 30 days... Found 245 games so far
   Processed 60 days... Found 512 games so far
   ...
   ✅ Fetched 1,230 games for 2021-2022 season
   
   [Repeats for 2022-23, 2023-24, and current season]
   
   ================================================================================
   SUMMARY
   ================================================================================
   Historical Games (2021-2024): 3,690
   Current Season Games (2024-25): 156
   Total Games: 3,846
   ================================================================================
   ```

---

### **Step 4: Verify Data (5 minutes)**

1. **Open your NBA Google Sheet**

2. **Check `Historical_Games` tab:**
   - Should have ~3,600-3,800 rows
   - Columns: date, away_team, home_team, away_score, home_score, season
   - Dates range from 2021-10 to 2024-06

3. **Check `Current_Season` tab:**
   - Should have ~100-200 rows (depends on current date)
   - Some games may have empty scores (upcoming games)
   - Dates from 2024-10 to present

4. **Sample data should look like:**
   ```
   date        away_team  home_team  away_score  home_score  season
   2021-10-19  BKN        MIL        127         104         2021-22
   2021-10-19  GSW        LAL        121         114         2021-22
   ...
   ```

---

## ⏱️ **Time Estimates**

- **Setup (Steps 1-2):** 7 minutes
- **Data Collection (Step 3):** 1.5-2 hours (runs automatically)
- **Verification (Step 4):** 5 minutes
- **Total:** ~2 hours

---

## 🔄 **Running in Background**

To run the script in the background (so you can do other tasks):

```powershell
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\durel\Documents\confident-picks-restored; python confident-picks-automation\nba_data_fetcher.py" -WindowStyle Minimized
```

This will:
- ✅ Run in a separate PowerShell window
- ✅ Minimize automatically
- ✅ Let you continue with other tasks
- ✅ You can check progress by maximizing the window

---

## 🐛 **Troubleshooting**

### **Error: "Spreadsheet not found"**
- Make sure you shared the sheet with the service account email
- Check that the spreadsheet ID is correct

### **Error: "Rate limit exceeded"**
- The script has built-in rate limiting (0.5s between requests)
- If you still hit limits, increase the `time.sleep()` values

### **Error: "No games found"**
- ESPN API might be down or changed
- Check if you can access: `https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard`
- May need to adjust API endpoints

### **Slow Performance**
- Normal! Fetching 3+ years of data takes time
- Expect ~2 hours for full historical data
- You can run it overnight

---

## ✅ **Completion Checklist**

- [ ] NBA Google Sheet created
- [ ] Sheet shared with service account
- [ ] Spreadsheet ID added to script
- [ ] Script run successfully
- [ ] Historical data populated (~3,600+ games)
- [ ] Current season data populated (~100+ games)
- [ ] Data verified in Google Sheets

---

## 🎉 **Once Complete:**

**You now have:**
- ✅ 3+ years of NBA historical data
- ✅ Current season data
- ✅ Ready for NBA model training

**Next Steps:**
1. ✅ Let the script finish (runs in background)
2. ✅ Move to Task 4 (Legal Documents)
3. ⏸️ Wait for data collection to complete
4. 🔄 Tomorrow: Start NBA model training

---

**Estimated Time:** 2 hours (mostly automated)  
**Status:** Ready to run!

