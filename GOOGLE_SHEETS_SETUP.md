# 🚀 Quick Start: Connect Google Sheets to Firebase

Your Google Sheets integration is now ready! Follow these steps to get it working.

## ✅ What You Need

1. ✓ Firebase service account JSON file (you have this!)
   - Location: `c:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json`
   - Service Account Email: `firebase-adminsdk-fbsvc@confident-picks-app-8-25.iam.gserviceaccount.com`

2. ✓ Google Sheet (create one or use existing)

3. ✓ Google Sheets API enabled (we'll do this)

## 📋 Step-by-Step Setup (5 minutes)

### Step 1: Enable Google Sheets API

1. Open this link: [Enable Google Sheets API](https://console.cloud.google.com/apis/library/sheets.googleapis.com?project=confident-picks-app-8-25)

2. Make sure **"confident-picks-app-8-25"** is selected at the top

3. Click the blue **"ENABLE"** button

4. Wait a few seconds for it to activate ✅

### Step 2: Share Your Google Sheet

1. **Create a new Google Sheet** (or open an existing one):
   - Go to: https://sheets.google.com
   - Click "+ Blank" to create new sheet
   - Name it something like "Confident Picks Data"

2. **Copy this email address**:
   ```
   firebase-adminsdk-fbsvc@confident-picks-app-8-25.iam.gserviceaccount.com
   ```

3. **Share the sheet**:
   - Click the green **"Share"** button in top-right
   - Paste the email address above
   - Change access level to **"Editor"**
   - Click **"Send"** or **"Done"**

4. **Copy the Spreadsheet ID** from the URL:
   ```
   URL: https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
                                              ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
                                              This is your Spreadsheet ID
   ```

### Step 3: Install Dependencies

Open PowerShell in your project folder and run:

```powershell
cd confident-picks-automation
npm install googleapis
```

### Step 4: Run the Setup Script

```powershell
node setup-google-sheets.js
```

The script will ask you:
1. **Path to service account file**: Enter:
   ```
   c:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json
   ```

2. **Have you enabled the API?**: Type `yes`

3. **Have you shared the sheet?**: Type `yes`

4. **Spreadsheet ID**: Paste the ID you copied from the URL

5. **Test connection?**: Type `yes`

If everything is green ✅, you're done!

## 🎯 Now You Can:

### 1. Sync Firebase → Google Sheets

Export all your picks to a Google Sheet:

```powershell
node sync-sheets.js --to-sheets
```

This creates a nicely formatted spreadsheet with all your picks!

### 2. Import Google Sheets → Firebase

Add picks from a spreadsheet to Firebase:

```powershell
node sync-sheets.js --to-firebase
```

Imports go to the `qa_picks` collection for review first.

### 3. Use API Endpoints

Once deployed to Vercel, you can trigger syncs via API:

```bash
# Sync to Sheets
curl -X POST https://your-domain.vercel.app/api/sync-to-sheets

# Import from Sheets
curl -X POST https://your-domain.vercel.app/api/import-from-sheets
```

## 🔧 Configuration

The setup script creates: `confident-picks-automation/config/google-sheets.json`

You can edit this file to customize:
- Spreadsheet ID
- Sheet name (default: "Picks")
- Sync direction
- Auto-sync settings

## 📊 What Gets Synced?

When you sync to Google Sheets, you'll get these columns:

| ID | League | Game | Pick | Market Type | Odds | Confidence | Tier | Status | Result | Commence Time | Reasoning |
|----|--------|------|------|-------------|------|------------|------|--------|--------|---------------|-----------|
| nfl_001 | NFL | Chiefs vs Bills | Chiefs -3.5 | spread | -110 | 0.78 | premium | pending | - | 2025-10-22 13:00 | Strong rushing... |

## 🐛 Troubleshooting

### "The caller does not have permission"
→ Share the sheet with: `firebase-adminsdk-fbsvc@confident-picks-app-8-25.iam.gserviceaccount.com`

### "API has not been used in project"
→ Enable the Google Sheets API: [Click here](https://console.cloud.google.com/apis/library/sheets.googleapis.com?project=confident-picks-app-8-25)

### "Cannot find module 'googleapis'"
→ Run: `npm install googleapis`

### "Service account file not found"
→ Check the path to your JSON file is correct

## 💡 Use Cases

### 📊 Performance Tracking
Sync picks to Sheets and use formulas to calculate:
- Win rate: `=COUNTIF(J:J,"hit")/COUNTA(J:J)`
- ROI: Track profits over time
- Best performing markets

### 👥 Team Collaboration
- Share the sheet with your team
- Add comments and notes
- Review and approve picks before going live

### 📈 Analysis & Reporting
- Create pivot tables
- Build charts and graphs
- Export to Google Data Studio

### 💾 Backup & Archive
- Regular automated backups
- Historical data preservation
- Easy data recovery

## 🚀 Deploy to Vercel (Optional)

To use the API endpoints:

1. Install Vercel CLI:
   ```powershell
   npm install -g vercel
   ```

2. Deploy:
   ```powershell
   cd confident-picks-automation
   vercel --prod
   ```

3. Set environment variables in Vercel dashboard:
   - `GOOGLE_SHEETS_SPREADSHEET_ID`: Your spreadsheet ID
   - `GOOGLE_SHEETS_SHEET_NAME`: `Picks` (or your sheet name)
   - All your Firebase environment variables

## 📚 Full Documentation

For advanced usage, see:
- `confident-picks-automation/docs/GOOGLE_SHEETS.md` - Complete guide
- `confident-picks-automation/lib/google-sheets.js` - API reference

## ✨ Next Steps

1. ✅ Complete the setup above
2. ✅ Run your first sync
3. ✅ Explore the Google Sheet
4. ✅ Set up automated syncing
5. ✅ Build custom analysis sheets

---

**Need help?** Check the troubleshooting section above or review the full documentation.

**Working?** Great! Now you can track and analyze your picks like a pro! 🎉



