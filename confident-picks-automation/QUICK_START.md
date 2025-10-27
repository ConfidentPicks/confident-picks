# ⚡ Quick Start: Google Sheets + Firebase Integration

## What's Not Working?

If your Google Sheets integration isn't working, it's usually one of these 3 issues:

### ❌ Issue 1: Google Sheets API Not Enabled

**Fix:** Enable the API (1 click, 10 seconds)

1. Click: [Enable Google Sheets API](https://console.cloud.google.com/apis/library/sheets.googleapis.com?project=confident-picks-app-8-25)
2. Click the blue **"ENABLE"** button
3. Done! ✅

---

### ❌ Issue 2: Sheet Not Shared with Service Account

**Fix:** Share the sheet (30 seconds)

1. Open your Google Sheet
2. Click **"Share"** button (top-right, green button)
3. Add this email as **Editor**:
   ```
   firebase-adminsdk-fbsvc@confident-picks-app-8-25.iam.gserviceaccount.com
   ```
4. Click **"Send"**
5. Done! ✅

---

### ❌ Issue 3: Wrong Spreadsheet ID

**Fix:** Get the correct ID from the URL

Your Google Sheet URL looks like:
```
https://docs.google.com/spreadsheets/d/ABC123XYZ789/edit
                                        ^^^^^^^^^^^^
                                        This is the ID
```

Copy everything between `/d/` and `/edit`

---

## 🚀 Full Setup (5 Minutes)

### 1. Install Dependencies
```powershell
cd confident-picks-automation
npm install
```

### 2. Run Setup Wizard
```powershell
node setup-google-sheets.js
```

The wizard will:
- ✅ Load your Firebase service account
- ✅ Check API access
- ✅ Validate your spreadsheet
- ✅ Test the connection
- ✅ Create configuration file

### 3. Test It!

**Sync Firebase → Google Sheets:**
```powershell
node sync-sheets.js --to-sheets
```

**Import Google Sheets → Firebase:**
```powershell
node sync-sheets.js --to-firebase
```

---

## 🎯 What You Can Do

### 📊 Export Picks for Analysis
```powershell
node sync-sheets.js --to-sheets
```
Creates a formatted spreadsheet with all your picks, confidence scores, outcomes, and reasoning.

### 📥 Import Picks from Spreadsheet
```powershell
node sync-sheets.js --to-firebase
```
Import picks you've created or edited in Google Sheets back to Firebase.

### 🔄 Automated Syncing
Deploy to Vercel and set up automatic syncs every 6 hours.

---

## 📋 Spreadsheet Format

When you sync to Google Sheets, you'll get these columns:

| Column | Example |
|--------|---------|
| ID | `nfl_2025_week8_001` |
| League | `NFL` |
| Game | `Chiefs vs Bills` |
| Pick | `Chiefs -3.5` |
| Market Type | `spread` |
| Odds | `-110` |
| Confidence | `0.78` |
| Tier | `premium` |
| Status | `pending` / `active` / `completed` |
| Result | `hit` / `miss` |
| Commence Time | `2025-10-22 13:00:00` |
| Reasoning | `Strong rushing attack against weak run defense...` |

---

## 🔧 Common Issues

### "Module not found: googleapis"
```powershell
npm install googleapis
```

### "Permission denied"
Share the sheet with: `firebase-adminsdk-fbsvc@confident-picks-app-8-25.iam.gserviceaccount.com`

### "API not enabled"
Enable here: https://console.cloud.google.com/apis/library/sheets.googleapis.com?project=confident-picks-app-8-25

### "Invalid spreadsheet ID"
Get the ID from your sheet's URL (the long string between `/d/` and `/edit`)

---

## 💡 Pro Tips

### Add Formulas for Analysis

**Win Rate:**
```excel
=COUNTIF(J:J,"hit")/COUNTA(J:J)
```

**Average Confidence:**
```excel
=AVERAGE(G:G)
```

**Profit/Loss (assuming -110 odds):**
```excel
=SUMIF(J:J,"hit",1)*0.91 - COUNTIF(J:J,"miss")
```

**ROI:**
```excel
=(SUMIF(J:J,"hit",1)*0.91 - COUNTIF(J:J,"miss"))/COUNTA(J:J)*100
```

### Use Multiple Sheets
- `Picks` - All active picks
- `Results` - Completed picks with outcomes
- `Analysis` - Performance metrics
- `Archive` - Historical data

### Create Pivot Tables
Analyze performance by:
- League (NFL vs NBA vs NHL)
- Market Type (spreads vs totals)
- Confidence Level
- Day of week
- Time of day

---

## 📚 Documentation

- **Full Guide:** `docs/GOOGLE_SHEETS.md`
- **API Reference:** `lib/google-sheets.js`
- **Main README:** `README.md`

---

## ✨ Next Steps

1. ✅ Fix the 3 common issues above
2. ✅ Run the setup script
3. ✅ Test your first sync
4. ✅ Add analysis formulas
5. ✅ Set up automated syncing

**Still stuck?** Check `docs/GOOGLE_SHEETS.md` for detailed troubleshooting.




