# 🔗 How to Connect Google Sheets to Firebase

**Status:** ✅ Integration code is ready! You just need to complete the 3-step setup.

## What I Built For You

I've created a complete Google Sheets ↔ Firebase integration system that allows you to:

✅ **Export** picks from Firebase to Google Sheets for analysis  
✅ **Import** picks from Google Sheets back to Firebase  
✅ **Sync** data automatically on a schedule  
✅ **Track** performance with spreadsheet formulas  
✅ **Collaborate** with team members on picks  

## 🚀 3-Step Setup (5 Minutes)

### Step 1: Enable Google Sheets API (1 minute)

1. Click this link: [**Enable Google Sheets API**](https://console.cloud.google.com/apis/library/sheets.googleapis.com?project=confident-picks-app-8-25)
   
2. You should see "Google Sheets API" at the top
   
3. Click the blue **"ENABLE"** button
   
4. Wait a few seconds until it says "API enabled"

✅ **Done!** The API is now active for your project.

---

### Step 2: Share Your Google Sheet (2 minutes)

First, create or open a Google Sheet where you want to sync your picks.

**If you don't have a sheet yet:**
1. Go to [Google Sheets](https://sheets.google.com)
2. Click "+ Blank" to create a new sheet
3. Name it "Confident Picks" or whatever you like

**Now share it with your Firebase service account:**

1. Click the green **"Share"** button (top-right corner)

2. In the "Add people and groups" field, paste this email:
   ```
   firebase-adminsdk-fbsvc@confident-picks-app-8-25.iam.gserviceaccount.com
   ```

3. Make sure the dropdown says **"Editor"** (not "Viewer")

4. Click **"Send"** or **"Done"**

5. **Copy your Spreadsheet ID** from the URL:
   ```
   https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
                                           ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
                                           This part is your Spreadsheet ID
   ```
   Save this ID - you'll need it in the next step!

✅ **Done!** Your sheet is now accessible by your Firebase app.

---

### Step 3: Install & Configure (2 minutes)

Open **PowerShell** and run these commands:

```powershell
# Navigate to the automation folder
cd confident-picks-automation

# Install the Google Sheets library
npm install

# Run the setup wizard
node setup-google-sheets.js
```

The setup wizard will ask you a few questions:

1. **Service account file path**: Enter:
   ```
   c:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json
   ```

2. **Have you enabled the Google Sheets API?** → Type: `yes`

3. **Have you shared the sheet?** → Type: `yes`

4. **Spreadsheet ID** → Paste the ID you copied in Step 2

5. **Test connection?** → Type: `yes`

If everything is green with ✅ checkmarks, you're all set!

✅ **Done!** Your integration is configured and tested.

---

## 🎯 How to Use It

### Export Firebase → Google Sheets

This takes all your picks from Firebase and creates a nicely formatted spreadsheet:

```powershell
node sync-sheets.js --to-sheets
```

**What you get:**
- All picks organized in columns (League, Game, Pick, Confidence, etc.)
- Ready for analysis with Excel formulas
- Automatically formatted and sorted

### Import Google Sheets → Firebase

This imports picks from your spreadsheet into Firebase:

```powershell
node sync-sheets.js --to-firebase
```

**Notes:**
- Imports go to `qa_picks` collection (for review first)
- You can edit picks in the sheet before importing
- Great for bulk uploads or manual data entry

### Sync Both Ways

```powershell
node sync-sheets.js --both
```

---

## 📊 What the Spreadsheet Looks Like

After syncing, your Google Sheet will have these columns:

| ID | League | Game | Pick | Market Type | Odds | Confidence | Tier | Status | Result | Commence Time | Reasoning |
|----|--------|------|------|-------------|------|------------|------|--------|--------|---------------|-----------|
| nfl_001 | NFL | Chiefs vs Bills | Chiefs -3.5 | spread | -110 | 0.78 | premium | pending | - | Oct 22, 1pm | Strong rushing attack... |

You can add your own columns for notes, analysis, etc.

---

## 💡 Pro Tips

### Add Analysis Formulas

**Win Rate:**
```excel
=COUNTIF(J:J,"hit")/COUNTA(J:J)
```

**Average Confidence:**
```excel
=AVERAGE(G:G)
```

**Profit/Loss:**
```excel
=SUMIF(J:J,"hit",1)*0.91 - COUNTIF(J:J,"miss")
```

### Create Multiple Sheets
- **Picks** - All active picks
- **Results** - Completed picks with outcomes
- **Analysis** - Performance tracking
- **Archive** - Historical data

### Share with Your Team
- Share the Google Sheet with teammates
- They can add comments and notes
- Track changes with version history
- Set up protected ranges for formulas

---

## 🔧 Troubleshooting

### "Module not found: googleapis"
**Fix:** Run `npm install googleapis` in the `confident-picks-automation` folder

### "The caller does not have permission"
**Fix:** You forgot to share the sheet! Go back to Step 2 and share it with:
```
firebase-adminsdk-fbsvc@confident-picks-app-8-25.iam.gserviceaccount.com
```

### "API has not been used in project"
**Fix:** You need to enable the Google Sheets API. Go back to Step 1.

### "Invalid spreadsheet ID"
**Fix:** Check that you copied the entire ID from the URL. It should be a long string like `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`

### Still not working?
Run the connection test:
```powershell
node test-sheets-connection.js
```

This will diagnose the issue and tell you exactly what to fix.

---

## 🚀 Advanced: API Endpoints

Once you deploy to Vercel, you can trigger syncs via API:

**Sync to Sheets:**
```bash
POST https://your-domain.vercel.app/api/sync-to-sheets
```

**Import from Sheets:**
```bash
POST https://your-domain.vercel.app/api/import-from-sheets
```

You can set these up to run automatically on a schedule!

---

## 📚 More Documentation

- **Quick troubleshooting:** `confident-picks-automation/QUICK_START.md`
- **Complete guide:** `confident-picks-automation/docs/GOOGLE_SHEETS.md`
- **API reference:** `confident-picks-automation/lib/google-sheets.js`

---

## ✨ What's Next?

After setup, you can:

1. ✅ Sync your picks to Google Sheets
2. ✅ Add formulas to analyze performance
3. ✅ Share with team members
4. ✅ Set up automated syncing
5. ✅ Build custom dashboards

---

## 🆘 Need Help?

1. **Check if API is enabled:** [Click here](https://console.cloud.google.com/apis/library/sheets.googleapis.com?project=confident-picks-app-8-25)

2. **Check if sheet is shared:** Open your sheet → Click "Share" → Look for the service account email

3. **Run the test:** `node test-sheets-connection.js`

4. **Check the docs:** `confident-picks-automation/docs/GOOGLE_SHEETS.md`

---

## Summary

**You now have:**
- ✅ Complete Google Sheets integration code
- ✅ Sync scripts (Firebase ↔ Sheets)
- ✅ API endpoints for automation
- ✅ Test scripts for debugging
- ✅ Comprehensive documentation

**To get it working, just:**
1. Enable the Google Sheets API (1 click)
2. Share your sheet with the service account
3. Run the setup wizard

**Total time:** ~5 minutes

Ready to start? Begin with **Step 1** above! 🚀



