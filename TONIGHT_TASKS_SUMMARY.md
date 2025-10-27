# 🌙 Tonight's Tasks - Complete Guide

**Date:** October 25, 2025  
**Time:** ~4 hours total  
**Goal:** Complete 4 critical tasks while models train in background

---

## ✅ **TASK 1: Firebase Security Rules (30 minutes)**

### **What to Do:**
1. Open Firebase Console: https://console.firebase.google.com/
2. Select project: `confident-picks-app-8-25`
3. Go to: Firestore Database → Rules tab
4. Copy contents from: `firestore.rules` (I created this file)
5. Paste into Firebase Console
6. Click "Publish"

### **Why Important:**
- 🔒 Prevents users from giving themselves admin access
- 🔒 Prevents users from upgrading to premium for free
- 🔒 Critical security fix before launch

### **Test It:**
```javascript
// Try to give yourself admin (should fail)
const { doc, updateDoc } = await import('https://www.gstatic.com/firebasejs/10.0.0/firebase-firestore.js');
const userRef = doc(window.db, 'users', window.auth.currentUser.uid);
await updateDoc(userRef, { role: 'admin' });
// Expected: Error "Missing or insufficient permissions"
```

### **Files:**
- 📄 `firestore.rules` - Rules to deploy
- 📄 `DEPLOY_SECURITY_RULES.md` - Detailed guide

---

## ✅ **TASK 2: Purchase Domain (15 minutes)**

### **What to Do:**
1. Go to Namecheap.com (or Google Domains, Cloudflare)
2. Search for: `confidentpicks.com` (or your preferred name)
3. Add to cart
4. Purchase (~$12/year)
5. Enable privacy protection (free)

### **Why Important:**
- 🌐 Needed for professional email
- 🌐 Needed for production hosting
- 🌐 Needed for Stripe live mode
- 🌐 Better branding than Firebase subdomain

### **Don't Configure DNS Yet:**
- We'll do that when we set up hosting (tomorrow)
- Just purchase and enable privacy for now

### **Files:**
- 📄 `DOMAIN_PURCHASE_GUIDE.md` - Detailed guide

---

## ✅ **TASK 3: NBA Data Collection (2 hours - runs in background)**

### **What to Do:**

#### **Step 1: Create Google Sheet (5 min)**
1. Go to: https://sheets.google.com
2. Create new sheet: "NBA Prediction Data"
3. Create tabs: `Historical_Games`, `Current_Season`, `Upcoming_Games`
4. Copy spreadsheet ID from URL
5. Share with: `firebase-adminsdk-fbsvc@confident-picks-app-8-25.iam.gserviceaccount.com`

#### **Step 2: Update Script (2 min)**
1. Open: `confident-picks-automation/nba_data_fetcher.py`
2. Find line 17: `NBA_SPREADSHEET_ID = 'YOUR_NBA_SHEET_ID_HERE'`
3. Replace with your actual spreadsheet ID
4. Save file

#### **Step 3: Run Script (2 hours - automated)**
```powershell
# Run in background
cd C:\Users\durel\Documents\confident-picks-restored
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python confident-picks-automation\nba_data_fetcher.py" -WindowStyle Minimized
```

### **Why Important:**
- 🏀 More content for your app
- 🏀 NBA season is active NOW
- 🏀 Can train models while NFL/NHL models finish
- 🏀 Diversifies your picks offering

### **What It Does:**
- Fetches 2021-2024 historical games (~3,600 games)
- Fetches current 2024-25 season games (~100+ games)
- Uploads to Google Sheets
- Takes ~2 hours (runs automatically)

### **Files:**
- 📄 `confident-picks-automation/nba_data_fetcher.py` - The script
- 📄 `NBA_DATA_COLLECTION_SETUP.md` - Detailed guide

---

## ✅ **TASK 4: Legal Documents (1 hour)**

### **What to Do:**

#### **Option A: Use AI (30 minutes - Recommended)**
1. Open Claude or ChatGPT
2. Copy prompt from: `LEGAL_DOCUMENTS_GENERATOR.md`
3. Replace `[YOUR_DOMAIN_HERE]` with your actual domain
4. Generate Terms of Service
5. Generate Privacy Policy
6. Review and customize
7. Save as HTML files

#### **Option B: Use Template Service (1 hour)**
1. Go to: https://www.termsfeed.com/ or https://termly.io/
2. Fill out questionnaire
3. Generate documents
4. Download and customize

### **Why Important:**
- ⚖️ Legal protection for your business
- ⚖️ Required before accepting payments
- ⚖️ GDPR/CCPA compliance
- ⚖️ Builds user trust

### **Key Sections:**
- **Terms:** Service description, subscription terms, disclaimers, liability
- **Privacy:** Data collection, usage, storage, user rights, GDPR/CCPA

### **Files:**
- 📄 `LEGAL_DOCUMENTS_GENERATOR.md` - Detailed guide with AI prompt

---

## 📊 **Progress Tracking**

### **Before Tonight:**
- ✅ 4 model training scripts running
- ✅ Dashboard showing real data
- ✅ Admin system working
- ✅ NFL models launched

### **After Tonight (4 hours):**
- ✅ Firebase security rules deployed
- ✅ Domain purchased
- ✅ NBA data collection running (in background)
- ✅ Legal documents created

### **Tomorrow:**
- 🔄 Stripe live mode setup
- 🔄 Stripe webhooks
- 🔄 Production hosting
- 🔄 Email service setup

---

## ⏱️ **Timeline**

| Task | Time | Can Run in Background? |
|------|------|------------------------|
| 1. Firebase Security Rules | 30 min | No (but quick) |
| 2. Domain Purchase | 15 min | No (but quick) |
| 3. NBA Data Collection | 2 hours | ✅ YES |
| 4. Legal Documents | 1 hour | No |
| **Total Active Time** | **1h 45min** | |
| **Total Elapsed Time** | **4 hours** | (NBA runs in background) |

---

## 🎯 **Recommended Order**

1. **Start NBA Data Collection First** (2 hours in background)
   - Set up sheet (5 min)
   - Update script (2 min)
   - Start script in background
   - Let it run while you do other tasks

2. **Deploy Firebase Security Rules** (30 min)
   - Quick and critical
   - Test to make sure it works

3. **Purchase Domain** (15 min)
   - Quick win
   - Needed for everything else

4. **Generate Legal Documents** (1 hour)
   - Use AI for speed
   - Review and customize
   - Save for deployment tomorrow

**Total:** 1h 45min active work, NBA runs in background for 2 hours

---

## ✅ **Success Criteria**

By end of tonight, you should have:

- [ ] Firebase security rules deployed and tested
- [ ] Domain purchased and registered
- [ ] NBA data collection script running (or completed)
- [ ] Terms of Service document created
- [ ] Privacy Policy document created
- [ ] All 4 model training scripts still running
- [ ] Dashboard showing progress for all models

---

## 🚀 **What's Running Overnight**

While you sleep, these will continue:

1. **NHL Moneyline** - Finding teams at 70%+
2. **NHL Puck Line** - Finding teams at 70%+ (already at 17/32!)
3. **NFL Spread** - Finding teams at 70%+
4. **NFL Total** - Finding teams at 70%+
5. **NBA Data Collection** - Fetching historical games

**Tomorrow morning:** Check progress on all 5 tasks!

---

## 📞 **Need Help?**

If you get stuck on any task:

1. Check the detailed guide for that task
2. Look for troubleshooting sections
3. Ask me for help!

---

**Let's get started!** 🚀

**Recommended:** Start with NBA data collection (runs in background), then do the quick tasks (security rules, domain), then legal docs while NBA collects data.

