# 🏈 Daily Prediction Automation Guide

## ✅ **WHAT'S BEEN SET UP**

Your NFL prediction system now has a **fully automated daily pipeline** that:

1. **Trains the model** on 2021-2024 historical data (768 games)
2. **Generates predictions** for all 2025 games (272 games)
3. **Adjusts confidence** using ESPN FPI team ratings
4. **Updates Google Sheet** automatically

---

## 📊 **COLUMNS AUTOMATICALLY UPDATED**

### **Column AX - `predicted_winner`**
- Team name predicted to win
- Based on Random Forest model (67.5% historical accuracy)
- Example: "PHI", "BUF", "KC"

### **Column AZ - `winner_confidence`**
- Model's raw confidence score (0-100%)
- Based on probability from Random Forest
- Example: "88.9%", "91.4%"

### **Column BA - `winner_confidence_fpi`**
- FPI-adjusted confidence score (0-100%)
- **Boosted** when model agrees with ESPN FPI
- **Lowered** when model disagrees with ESPN FPI
- Example: "93.0%" (boosted from 88.9%)

---

## 🚀 **HOW TO RUN**

### **Option 1: Manual Run (Anytime)**
```batch
# Double-click this file:
run-daily-predictions.bat

# Or run in terminal:
python confident-picks-automation/daily_prediction_update.py
```

### **Option 2: Automated Daily Run (Recommended)**
```batch
# Run this ONCE to set up automation:
setup-daily-predictions.bat

# This creates a Windows Task Scheduler task that runs automatically
# every day at 6:00 AM
```

---

## 📅 **AUTOMATION SCHEDULE**

**Default Schedule:** Daily at 6:00 AM

**To Change Schedule:**
1. Open Windows Task Scheduler
2. Find task: "NFL Daily Predictions"
3. Right-click → Properties
4. Go to "Triggers" tab
5. Edit the schedule as needed

**Suggested Times:**
- **6:00 AM** - Before you start work
- **12:00 PM** - Midday update
- **6:00 PM** - Evening update before games

---

## 🔧 **HOW IT WORKS**

### **Step 1: Load Data**
- Loads 768 historical games (2021-2024)
- Loads 272 current season games (2025)

### **Step 2: Train Model**
- Creates advanced features from team stats
- Trains Random Forest model
- Uses 24 different features per game

### **Step 3: Generate Predictions**
- Runs trained model on all 2025 games
- Generates winner predictions
- Calculates raw confidence scores

### **Step 4: ESPN FPI Adjustment**
- Loads ESPN FPI ratings for 32 NFL teams
- Compares model predictions with FPI favorites
- **Agreement:** Boosts confidence by 2-5%
- **Disagreement:** Lowers confidence by 3-10%

### **Step 5: Update Sheet**
- Writes all predictions to Google Sheet
- Updates columns AX, AZ, BA
- 272 games updated in seconds

---

## 📈 **MODEL PERFORMANCE**

**Historical Accuracy (2021-2024):** 67.5%
**Current Season Accuracy (2025):** 55.6%

**Confidence Distribution:**
- High Confidence (80-99%): ~85% of predictions
- Medium Confidence (60-79%): ~10% of predictions
- Low Confidence (51-59%): ~5% of predictions

---

## 🔄 **WHAT STAYS THE SAME**

✅ All predictions update in the **same columns** (AX, AZ, BA)
✅ No new columns are created
✅ Data is overwritten daily with fresh predictions
✅ Historical data is preserved and used for training

---

## 🛠️ **TROUBLESHOOTING**

### **Issue: Predictions not updating**
**Solution:** 
1. Check if script ran successfully
2. Look for error messages in terminal
3. Verify Google Sheets API credentials are valid

### **Issue: Scheduled task not running**
**Solution:**
1. Open Task Scheduler
2. Right-click "NFL Daily Predictions" → Run
3. Check "Last Run Result" for errors
4. Ensure script path is correct

### **Issue: Low confidence scores**
**Solution:**
- This is normal for closely matched teams
- FPI disagreement will lower confidence
- Check ESPN FPI ratings for those teams

---

## 📊 **FILES CREATED**

### **Main Script**
- `confident-picks-automation/daily_prediction_update.py` - Combined prediction pipeline

### **Batch Files**
- `run-daily-predictions.bat` - Manual run script
- `setup-daily-predictions.bat` - Task Scheduler setup

### **Documentation**
- `DAILY_PREDICTION_AUTOMATION.md` - This guide

---

## 🎯 **NEXT STEPS**

### **For Today:**
1. ✅ Run `setup-daily-predictions.bat` to enable automation
2. ✅ Verify predictions are in columns AX, AZ, BA
3. ✅ Check Task Scheduler to confirm task is created

### **Going Forward:**
- Predictions will update automatically every morning at 6:00 AM
- You can manually run anytime using `run-daily-predictions.bat`
- Model improves over time as more 2025 games are completed

---

## 💡 **TIPS**

1. **Run manually after big upsets** - Model adapts to new data
2. **Check FPI agreements** - High agreement = higher confidence in prediction
3. **Monitor accuracy** - Track how predictions perform over time
4. **Adjust schedule** - Change task scheduler time if needed

---

## ✅ **SUMMARY**

You now have a **fully automated NFL prediction system** that:
- ✅ Trains on 768 historical games
- ✅ Generates predictions for 272 current games
- ✅ Adjusts confidence with ESPN FPI
- ✅ Updates your Google Sheet daily
- ✅ Runs automatically at 6:00 AM (or your chosen time)

**All predictions stay in the same columns (AX, AZ, BA) and update daily!** 🏈📊


