# 🤖 Comprehensive Model Training Plan

## Current Status (October 26, 2025)

### NFL
- ✅ **Moneyline**: 32 teams (60%+ accuracy)
- ❌ **Spread**: 0 teams
- ❌ **Total**: 0 teams

### NHL
- ❌ **Moneyline**: 0 teams (testing in progress, found 8 teams at 70%+ but not saved)
- ❌ **Puck Line**: 0 teams

---

## 🎯 Goal: Train ALL Teams for ALL Props

### Target Models:
- **NFL**: 32 teams × 3 props = **96 models**
- **NHL**: 32 teams × 2 props = **64 models**
- **TOTAL**: **160 models**

---

## 💻 Resource Requirements

### Current Usage:
- **CPU**: Light (1 core per script)
- **RAM**: ~34MB per exhaustive test script
- **Disk**: Minimal

### Recommended Parallel Scripts:
- ✅ **4-6 scripts simultaneously** (you have plenty of resources)
- Each script runs independently
- No conflicts or interference

---

## 📋 Execution Plan

### Phase 1: NHL Completion (Days 1-2)
Run these **2 scripts in parallel**:

1. **NHL Moneyline** (continue current run)
   ```bash
   python confident-picks-automation\nhl_exhaustive_test_moneyline.py
   ```
   - Target: 32 teams at 70%+
   - Time: 24-48 hours

2. **NHL Puck Line** (new)
   ```bash
   python confident-picks-automation\nhl_exhaustive_test_puckline.py
   ```
   - Target: 32 teams at 70%+
   - Time: 24-48 hours

### Phase 2: NFL Expansion (Days 2-4)
Run these **2 scripts in parallel**:

3. **NFL Spread** (new)
   ```bash
   python confident-picks-automation\nfl_exhaustive_test_spread.py
   ```
   - Target: 32 teams at 70%+
   - Time: 24-48 hours

4. **NFL Total** (new)
   ```bash
   python confident-picks-automation\nfl_exhaustive_test_total.py
   ```
   - Target: 32 teams at 70%+
   - Time: 24-48 hours

---

## 📊 Real-Time Monitoring

### Dashboard Features (to be implemented):
1. ✅ **Remove all mock data**
2. ✅ **Connect to Firebase for real-time updates**
3. ✅ **Show actual progress** (X/32 teams completed per prop)
4. ✅ **Auto-refresh every 10 seconds**
5. ✅ **Show which script is running**
6. ✅ **Estimated time remaining**

### Progress Tracking File:
Each script will write to:
- `nhl_moneyline_progress.json`
- `nhl_puckline_progress.json`
- `nfl_spread_progress.json`
- `nfl_total_progress.json`

Format:
```json
{
  "sport": "NHL",
  "prop": "Moneyline",
  "status": "running",
  "teamsCompleted": 8,
  "teamsTarget": 32,
  "currentConfig": "(150, 0.15, 0, 12)",
  "bestAccuracy": 0.809,
  "startTime": "2025-10-26T10:00:00",
  "estimatedCompletion": "2025-10-27T10:00:00"
}
```

---

## 🚀 Implementation Steps

### Step 1: Create Prop-Specific Training Scripts
- Duplicate `nhl_exhaustive_test.py` for each prop
- Modify to target specific prop (Moneyline, Puck Line, Total, Spread)
- Add progress tracking to JSON files

### Step 2: Fix Dashboard
- Remove `generateMockData()` functions
- Connect to Firebase `approved_models` collection
- Add real-time progress from JSON files
- Show "No data yet" instead of mock data

### Step 3: Launch All Scripts
- Start NHL Moneyline (already running)
- Start NHL Puck Line
- Start NFL Spread
- Start NFL Total
- Monitor via dashboard

---

## ⏱️ Timeline

| Day | Scripts Running | Expected Completions |
|-----|----------------|---------------------|
| 1 | NHL ML, NHL PL | NHL ML: 8-16 teams |
| 2 | NHL ML, NHL PL, NFL Spread, NFL Total | NHL ML: 32 teams, NHL PL: 16 teams |
| 3 | NHL PL, NFL Spread, NFL Total | NHL PL: 32 teams, NFL Spread: 16 teams |
| 4 | NFL Spread, NFL Total | NFL Spread: 32 teams, NFL Total: 16 teams |
| 5 | NFL Total | NFL Total: 32 teams |

**Total Time: 4-5 days** for all 160 models

---

## 🎬 Ready to Start?

**Option A: Start Everything Now** (Recommended)
- I'll create all 4 prop-specific scripts
- Fix the dashboard to show real data
- Launch all scripts in parallel
- You monitor via dashboard

**Option B: Finish NHL First, Then NFL**
- Complete NHL Moneyline + Puck Line (2 days)
- Then start NFL Spread + Total (2 days)
- Total: 4 days sequential

**Option C: Lower Threshold to 65%**
- Get more teams approved faster
- Complete in 2-3 days instead of 4-5
- Still good accuracy for launch

---

## 💡 Recommendation

**Start Option A immediately:**
1. Your computer can handle it (only using 34MB RAM per script)
2. Get all 160 models done in 4-5 days
3. Real-time dashboard shows progress
4. No waiting - everything runs in parallel

**Which option do you prefer?**

