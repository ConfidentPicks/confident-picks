# 🎯 Pick Generation Guide

## Problem
- **Old picks** from previous system showing on app (0% confidence, wrong odds)
- **New models** (101 approved!) not being used yet

---

## Solution: Two-Step Process

### Step 1: Clear Old Picks
```bash
python clear_old_picks.py
```
**What it does:**
- Deletes all picks from `all_picks`, `live_picks`, `test_picks`, `nhl_test_picks`
- Removes the incorrect picks showing on your app

### Step 2: Generate Fresh Picks
```bash
python generate_picks_from_models.py
```
**What it does:**
- Fetches all 101 approved models from Firebase
- Gets upcoming games from NFL & NHL sheets
- Generates picks ONLY for teams with 70%+ confidence models
- Saves to `all_picks` collection in Firebase

---

## 🚀 Quick Start

**Option A: Run Both Steps**
```bash
REFRESH_PICKS.bat
```

**Option B: Run Individually**
```bash
# Clear old picks
python clear_old_picks.py

# Generate new picks
python generate_picks_from_models.py
```

---

## 📊 What You'll See

### Before:
- 7 NFL picks with 0% confidence
- Wrong odds (-110 for everything)
- Old system data

### After:
- Only picks from approved models (70%+ confidence)
- Correct odds from sheets
- Model name in reasoning
- Proper confidence scores

---

## 🔄 When to Re-run

**Re-run pick generation when:**
1. New games are added to upcoming_games sheets
2. New models reach 70%+ and get approved
3. Odds change and you want updated picks
4. Before each game day

**Schedule it:**
- Run `generate_picks_from_models.py` every 6 hours
- Or manually before each slate of games

---

## 🎯 Pick Generation Logic

```
For each upcoming game:
  For each team (home & away):
    Check if we have an approved model for that team
    If model confidence >= 70%:
      Generate pick with:
        - Team to win
        - Model confidence as pick confidence
        - Actual odds from sheet
        - Model name in reasoning
```

---

## 📝 Collections Used

| Collection | Purpose |
|------------|---------|
| `approved_models` | Source of truth for models (70%+ only) |
| `all_picks` | Where generated picks are saved |
| `live_picks` | (Legacy - can be cleared) |
| `test_picks` | (Legacy - can be cleared) |

---

## ⚠️ Important Notes

1. **Only 70%+ models generate picks** - This is your quality threshold
2. **Picks are team-specific** - If BUF has a 75% model but CAR doesn't, only BUF pick is generated
3. **Confidence = Model Accuracy** - The pick confidence comes directly from the model's current accuracy
4. **Unique document IDs** - Format: `{sport}_{awayTeam}_{homeTeam}_{pick}` prevents duplicates

---

## 🐛 Troubleshooting

**No picks generated?**
- Check if you have upcoming games in sheets
- Verify models are approved in Firebase (`approved_models` collection)
- Ensure models have 70%+ current_accuracy

**Still seeing old picks?**
- Run `clear_old_picks.py` again
- Check which collections your app is reading from (`index.html`)
- May need to clear browser cache

**Confidence still 0%?**
- Check the `confidence` field in Firebase (should be 0.70-1.0)
- Verify `index.html` is reading `confidence` correctly
- May need to multiply by 100 in display code

---

## 🔮 Future Enhancements

- [ ] Add spread picks (puck line for NHL)
- [ ] Add total (over/under) picks
- [ ] Implement pick migration (upcoming → live → completed)
- [ ] Add scheduled automation (Windows Task Scheduler)
- [ ] Add email notifications when new picks are generated
- [ ] Add Slack/Discord webhooks for pick alerts

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Clear old picks | `python clear_old_picks.py` |
| Generate new picks | `python generate_picks_from_models.py` |
| Do both | `REFRESH_PICKS.bat` |
| Check models | Open `model_performance_dashboard.html` |
| Check Firebase | `python check_firebase_models.py` |

