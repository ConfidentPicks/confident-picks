# Google Sheets Integration Guide

This guide explains how to integrate Google Sheets with your Firebase Confident Picks project.

## 🎯 Overview

The Google Sheets integration allows you to:

- **Export picks** from Firebase to Google Sheets for analysis
- **Import picks** from Google Sheets to Firebase
- **Track performance** using spreadsheet formulas
- **Share data** with team members
- **Automated syncing** via API endpoints or cron jobs

## 📋 Prerequisites

1. **Firebase project** with service account credentials
2. **Google Cloud project** (same as Firebase)
3. **Google Sheet** to sync with
4. **Node.js 18+** for local scripts

## 🚀 Quick Setup

### Step 1: Enable Google Sheets API

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/library/sheets.googleapis.com)
2. Select your Firebase project
3. Click **"ENABLE"** to activate the Google Sheets API
4. Wait for activation (usually instant)

### Step 2: Share Your Google Sheet

1. Open your Google Sheet
2. Click the **"Share"** button
3. Add your Firebase service account email as **Editor**:
   ```
   firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com
   ```
4. Click **"Send"** or **"Done"**

> ⚠️ **Important:** The service account MUST have Editor access to read/write data

### Step 3: Run Setup Script

```bash
cd confident-picks-automation
npm install googleapis
node setup-google-sheets.js
```

Follow the interactive prompts to:
- Load your service account credentials
- Verify API access
- Configure your spreadsheet ID
- Test the connection

### Step 4: Configure Environment Variables

Add these to your `.env.local` or Vercel environment:

```bash
# Google Sheets Configuration
GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id-here
GOOGLE_SHEETS_SHEET_NAME=Picks

# Firebase credentials (already configured)
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
```

## 📊 Usage

### Manual Sync (Local)

Sync Firebase → Google Sheets:
```bash
node sync-sheets.js --to-sheets
```

Sync Google Sheets → Firebase:
```bash
node sync-sheets.js --to-firebase
```

Sync both directions:
```bash
node sync-sheets.js --both
```

### API Endpoints (Automated)

#### Sync to Google Sheets

**Endpoint:** `POST /api/sync-to-sheets`

**Description:** Exports all picks from Firebase to Google Sheets

**Response:**
```json
{
  "success": true,
  "message": "Firebase data synced to Google Sheets",
  "pickCount": 45,
  "duration": "1234ms",
  "timestamp": "2025-10-22T12:00:00.000Z"
}
```

**cURL Example:**
```bash
curl -X POST https://your-domain.vercel.app/api/sync-to-sheets
```

#### Import from Google Sheets

**Endpoint:** `POST /api/import-from-sheets`

**Description:** Imports picks from Google Sheets to Firebase (qa_picks collection)

**Body (optional):**
```json
{
  "collection": "qa_picks"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Google Sheets data imported to Firebase",
  "pickCount": 25,
  "collection": "qa_picks",
  "duration": "987ms",
  "timestamp": "2025-10-22T12:00:00.000Z"
}
```

**cURL Example:**
```bash
curl -X POST https://your-domain.vercel.app/api/import-from-sheets \
  -H "Content-Type: application/json" \
  -d '{"collection": "qa_picks"}'
```

### Automated Syncing

Add to your `vercel.json` for scheduled syncs:

```json
{
  "crons": [
    {
      "path": "/api/sync-to-sheets",
      "schedule": "0 */6 * * *"
    }
  ]
}
```

This syncs every 6 hours automatically.

## 📄 Data Format

### Firebase → Sheets Export

The script exports picks with these columns:

| Column | Description | Example |
|--------|-------------|---------|
| ID | Pick document ID | `nfl_2025_001` |
| League | Sport league | `NFL` |
| Game | Matchup | `Chiefs vs Bills` |
| Pick | Recommended bet | `Chiefs -3.5` |
| Market Type | Bet type | `spread` |
| Odds | Betting odds | `-110` |
| Confidence | Model confidence | `0.78` |
| Tier | Access tier | `premium` |
| Status | Pick status | `pending` |
| Result | Outcome | `hit` / `miss` |
| Commence Time | Game start time | `2025-10-22 13:00:00` |
| Reasoning | AI reasoning | `Strong rushing attack...` |

### Sheets → Firebase Import

When importing, the sheet should have headers matching the columns above. The script will:

1. Read all rows from the sheet
2. Convert to pick objects
3. Upload to specified Firebase collection
4. Add metadata (`source`, `updatedAt`)

## 🔧 Advanced Usage

### Custom Sheet Format

Modify the conversion functions in `lib/google-sheets.js`:

```javascript
// Customize export format
function picksToSheetFormat(picks) {
  const headers = ['Custom', 'Headers', 'Here'];
  // ... custom logic
}

// Customize import format
function sheetFormatToPicks(rows) {
  // ... custom parsing logic
}
```

### Multiple Sheets

You can sync to different sheets by passing parameters:

```javascript
const result = await syncFirebaseToSheets(
  sheetsClient,
  db,
  spreadsheetId,
  'WeeklyPicks' // Different sheet name
);
```

### Filtering Picks

Modify the sync functions to filter picks:

```javascript
// Only sync live picks
const picksSnapshot = await firebaseDb
  .collection('live_picks')
  .where('status', '==', 'active')
  .get();
```

## 🛡️ Security Considerations

1. **Service Account Permissions**
   - Grant minimum necessary permissions
   - Don't share service account keys
   - Store keys as environment variables, never in code

2. **Sheet Access**
   - Only share with the service account
   - Don't make sheets publicly editable
   - Use protected ranges for critical data

3. **API Security**
   - Add authentication to API endpoints
   - Implement rate limiting
   - Validate all input data

## 🐛 Troubleshooting

### Error: "The caller does not have permission"

**Solution:** Ensure the sheet is shared with your service account email

### Error: "Unable to parse range"

**Solution:** Check the sheet name and range format (e.g., `Sheet1!A1:Z100`)

### Error: "API has not been used in project"

**Solution:** Enable the Google Sheets API in Google Cloud Console

### Error: "Invalid credentials"

**Solution:** 
- Verify service account JSON is correct
- Check that private key has proper newline characters
- Ensure all environment variables are set

### Data Not Syncing

**Checklist:**
- ✅ Google Sheets API enabled
- ✅ Sheet shared with service account
- ✅ Correct spreadsheet ID
- ✅ Sheet name matches configuration
- ✅ Firebase credentials valid
- ✅ Network connectivity working

## 📊 Example Workflow

### Weekly Analysis Workflow

1. **Sunday Night:** Auto-sync picks to Google Sheets
2. **Monday Morning:** Analyze performance in spreadsheet
3. **Monday Afternoon:** Update strategies in sheet
4. **Monday Evening:** Import updated picks back to Firebase
5. **Tuesday:** New picks generated using updated data

### Collaborative Review Workflow

1. **AI generates picks** → Saved to `qa_picks` in Firebase
2. **Auto-sync to Google Sheets** for team review
3. **Team members review** and edit picks in spreadsheet
4. **Approved picks imported** back to Firebase
5. **Promoted to `live_picks`** collection for users

## 🎯 Best Practices

1. **Regular Backups**
   - Sync to Sheets daily as a backup
   - Keep historical sheets for comparison

2. **Data Validation**
   - Use sheet formulas to validate data
   - Set up conditional formatting for anomalies

3. **Performance Tracking**
   - Add calculated columns for win rate
   - Create pivot tables for analysis
   - Track performance by league/market

4. **Collaboration**
   - Use sheet comments for notes
   - Share view-only links with stakeholders
   - Track changes with version history

## 📈 Example Formulas

Add these to your Google Sheet for analysis:

```excel
// Win Rate
=COUNTIF(J:J,"hit")/COUNTA(J:J)

// Average Confidence
=AVERAGE(G:G)

// Profit/Loss (assuming -110 odds)
=SUMIF(J:J,"hit",1)*0.91 - COUNTIF(J:J,"miss")

// ROI
=(SUMIF(J:J,"hit",1)*0.91 - COUNTIF(J:J,"miss"))/COUNTA(J:J)*100
```

## 🔗 Resources

- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [Service Account Authentication](https://cloud.google.com/iam/docs/service-accounts)

## 💡 Tips

- Use **named ranges** for easier referencing
- Create **separate sheets** for different sports
- Set up **Google Apps Script** for custom automation
- Use **data validation** to prevent errors
- Enable **protected ranges** for formulas

## ✨ Next Steps

After setup, you can:
1. Create custom dashboards in Google Sheets
2. Build Google Data Studio reports
3. Set up automated email reports
4. Integrate with other tools (Zapier, Make)
5. Create custom Google Apps Script automations




