# 🎯 Clean Pick Generation Workflow

## 🔧 **Issues Fixed:**

1. ✅ **Conflicting picks removed** - Only one pick per game (highest confidence)
2. ✅ **Data leakage removed** - NFL 100% models deleted
3. ✅ **Smart selection** - Automatically picks best team when both qualify

---

## 🚀 **New Workflow:**

### **Option 1: Run Everything (Recommended)**
```bash
REFRESH_PICKS_CLEAN.bat
```

This will:
1. Delete NFL models with 100% accuracy (data leakage)
2. Clear old picks from Firebase
3. Generate fresh picks with no conflicts

### **Option 2: Run Steps Individually**
```bash
# Step 1: Delete leaked models
python delete_leaked_models.py

# Step 2: Clear old picks
python clear_old_picks.py

# Step 3: Generate smart picks
python generate_picks_smart.py
```

---

## 🎯 **Smart Pick Logic:**

### **Before (Old System):**
```
Game: DAL @ DEN
- DAL model: 72.7% ✓
- DEN model: 71.4% ✓
Result: BOTH picks generated (CONFLICT!)
```

### **After (New System):**
```
Game: DAL @ DEN
- DAL model: 72.7% ✓
- DEN model: 71.4% ✓
Selection: Pick DAL (higher confidence)
Result: ONE pick generated (NO CONFLICT!)
```

---

## 📊 **What Gets Filtered:**

### **1. Data Leakage (100% Models)**
- **Problem:** NFL Total models showing 100% accuracy
- **Cause:** Training data included game results
- **Solution:** Delete all models with 100% accuracy
- **Impact:** Removes 31 NFL Total models

### **2. Conflicting Picks**
- **Problem:** Both teams in same game picked
- **Cause:** Both teams have 70%+ models
- **Solution:** Pick the team with higher confidence
- **Impact:** Reduces picks from 23 → ~13-15

---

## 🔍 **Example Output:**

### **Expected Smart Picks:**

**NFL (5-7 picks):**
- CHI @ BAL → CHI (70.0%)
- NYJ @ CIN → CIN (83.3%)
- SF @ HOU → SF (90.9%)
- CLE @ NE → NE (76.9%)
- TB @ NO → NO (72.7%)
- DAL @ DEN → DAL (72.7%) *[Picked over DEN 71.4%]*
- TEN @ IND → IND (70.0%)
- GB @ PIT → GB (92.3%)

**NHL (6-8 picks):**
- COL @ NJD → COL (71.0%)
- VGK @ TBL → TBL (70.8%) *[Picked over VGK 70.4%]*
- SJS @ MIN → MIN (78.6%) *[Picked over SJS 72.4%]*
- UTA @ WPG → WPG (78.6%)
- LAK @ CHI → LAK (77.8%) *[Picked over CHI 75.0%]*
- DAL @ NSH → NSH (71.0%)
- NYR @ CGY → CGY (76.2%) *[Picked over NYR 71.4%]*
- EDM @ VAN → VAN (81.2%) *[Picked over EDM 75.0%]*

---

## 💡 **Additional Suggestions:**

### **1. Confidence Tiers**
Add confidence tiers to picks:
- **🔥 HIGH (85%+):** GB @ PIT (92.3%), SF @ HOU (90.9%)
- **⭐ MEDIUM (75-84%):** VAN (81.2%), MIN (78.6%)
- **✅ SAFE (70-74%):** CHI (70.0%), COL (71.0%)

### **2. Minimum Confidence Gap**
Only generate pick if confidence gap > 5%:
```python
if best_confidence - second_best_confidence < 0.05:
    # Skip this game - too close to call
    return None
```

### **3. Model Agreement Score**
Track when multiple models agree:
```python
if team_has_moneyline_model and team_has_spread_model:
    confidence_boost = 1.05  # 5% boost for agreement
```

### **4. Automated Daily Schedule**
Set up Windows Task Scheduler to run daily:
```
Time: 9:00 AM EST (before games)
Task: REFRESH_PICKS_CLEAN.bat
Frequency: Daily
```

### **5. Pick Limits**
Limit picks per sport to avoid overexposure:
```python
max_picks_per_sport = 5  # Only show top 5 per sport
```

---

## 🔄 **Daily Workflow:**

### **Morning (9 AM):**
1. Run `REFRESH_PICKS_CLEAN.bat`
2. Check dashboard for model status
3. Review generated picks

### **Before Games:**
1. Verify picks on app
2. Check for any last-minute odds changes
3. Monitor confidence levels

### **After Games:**
1. Update results in sheets
2. Track pick performance
3. Adjust models if needed

---

## 📝 **Files Created:**

| File | Purpose |
|------|---------|
| `delete_leaked_models.py` | Remove NFL 100% models |
| `generate_picks_smart.py` | Smart pick generation (no conflicts) |
| `REFRESH_PICKS_CLEAN.bat` | Run all steps in order |
| `CLEAN_PICK_WORKFLOW.md` | This guide |

---

## ⚠️ **Important Notes:**

1. **Run this workflow daily** to get fresh picks
2. **Check dashboard** to ensure models are still performing well
3. **Monitor conflicts** - log shows when picks are filtered
4. **Track performance** - keep records of pick accuracy
5. **Adjust threshold** - Can change from 70% to 75% if needed

---

## 🎯 **Next Steps:**

1. **Run the clean workflow now:**
   ```bash
   REFRESH_PICKS_CLEAN.bat
   ```

2. **Check your app** - Should see ~13-15 clean picks

3. **Set up automation** - Schedule daily runs

4. **Monitor performance** - Track win rates

---

**Ready to generate clean picks? Run `REFRESH_PICKS_CLEAN.bat`!** 🚀

