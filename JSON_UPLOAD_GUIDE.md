# 📁 JSON Upload Feature - Quick Start Guide

## 🚀 How to Upload Your UFC Picks

### **Step 1: Access the Admin Panel**
1. Open your app in the browser: `file:///C:/Users/durel/Documents/confident-picks-restored/index_10.5.2025.html`
2. Navigate to **Account** and sign in as Admin
3. Go to the **QA Dashboard** tab

### **Step 2: Open JSON Upload Panel**
1. Look for **"📁 Upload JSON Picks"** section (below "Create New Pick")
2. Click to expand the panel

### **Step 3: Upload Your Data**

#### **Option A: Paste Directly**
1. Open your NDJSON file: `C:\Users\durel\Downloads\ufc_rio_olivera_gamrot_picks.ndjson`
2. Copy all content (Ctrl+A, Ctrl+C)
3. Paste into the textarea in the upload panel
4. Click **"👁️ Preview"** to see first 3 picks
5. Click **"📤 Upload to Firebase"** to add all 40 picks

#### **Option B: Upload File**
1. Click **"Choose File"** button
2. Navigate to: `C:\Users\durel\Downloads\`
3. Select `ufc_rio_olivera_gamrot_picks.ndjson`
4. The file content will auto-populate the textarea
5. Click **"👁️ Preview"** then **"📤 Upload to Firebase"**

### **Step 4: Review & Approve**
1. All picks will be added to Firebase as **"draft"** status
2. They'll appear in the **"Picks Review"** list below
3. Click **"📝 Draft"** filter to see all new picks
4. Review each pick and click **"✓ Approve"** to make them live

---

## 📊 Data Conversion

Your UFC picks are automatically converted:

| **UFC Format** | **App Format** |
|----------------|----------------|
| `fighters[0]` → `awayTeam` | Luan Lacerda |
| `fighters[1]` → `homeTeam` | Saimon Oliveira |
| `prediction` → `pick` | Saimon Oliveira |
| `confidence` (0.65) → `confidence` | 65% |
| `eventDate` → `gameTime` | 2025-10-11 |
| `reasoning` → `reasoning` | Higher pace and pressure... |
| `sport` → `sport` | MMA |
| `league` → `league` | UFC |
| `event` → `event` | UFC Rio: Oliveira vs Gamrot |
| `market` → `market` | winner |

**Default values:**
- `odds`: -110 (since UFC data doesn't include odds)
- `status`: draft (all uploads start as draft)
- `injuryAlerts`: (empty)

---

## 🎯 What Happens After Upload

1. ✅ **All 40 picks** uploaded to Firebase `mlb_picks` collection
2. 📋 **Draft status** - ready for QA review
3. 🔄 **QA Dashboard** automatically refreshes
4. 👁️ **Review each pick** before approving
5. ✓ **Approve** to make live on the website
6. 🗑️ **Reject** to remove from consideration

---

## 🛠️ Troubleshooting

### **Upload Failed?**
- Check Firebase security rules (should be `allow read, write: if true;` for testing)
- Verify you're signed in as Admin
- Check browser console for errors (F12)

### **Preview Shows Error?**
- Verify NDJSON format (one JSON object per line)
- Check for invalid JSON syntax
- Each line must be valid JSON

### **File Upload Not Working?**
- Just copy/paste the content instead
- File upload is a convenience feature, paste method is more reliable

---

## 📝 Example Workflow

```
1. Copy NDJSON file content
2. Paste in upload panel
3. Click "Preview" → See 3 picks
4. Click "Upload" → All 40 picks added
5. Filter "Draft" → Review picks
6. Approve/Reject each pick
7. Approved picks go live on website
```

---

## 🔄 Future Enhancements

This manual upload system is **Phase 1**. Future phases will include:
- Automated pick generation from AI
- Auto-parsing of YouTube transcripts
- DraftKings odds integration
- Tri-LLM consensus system
- Injury report monitoring

**For now:** Use this manual upload to get picks on your site while you build the automation! 🚀


