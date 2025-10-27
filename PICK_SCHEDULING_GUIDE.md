# Pick Scheduling and Automation Guide

## Overview
This guide explains how to set up automated pick generation and completion tracking for the Confident Picks application.

## Scripts Created

### 1. `move_completed_picks_to_scoring.py`
**Purpose**: Automatically moves completed games from `all_picks` to `scoring` collection  
**Frequency**: Every 5-10 minutes  
**Location**: `confident-picks-automation/move_completed_picks_to_scoring.py`

**What it does:**
- Queries all active picks in `all_picks` collection
- Finds picks where `commenceTime` is in the past
- Moves them to `scoring` collection with status 'pending'
- Updates status in `all_picks` to 'completed'

### 2. `generate_picks_smart.py`
**Purpose**: Generates new picks from approved models  
**Frequency**: 2-3 times per day (see schedule below)  
**Location**: Root directory (`generate_picks_smart.py`)

**What it does:**
- Fetches approved models from Firebase (excludes 100% models - data leakage)
- Gets upcoming games from Google Sheets (NFL, NHL)
- Generates picks based on model confidence (70%+ required)
- Saves picks to `all_picks` collection with status 'active'

### 3. `run_pick_workflow.bat`
**Purpose**: Runs both scripts in sequence  
**Usage**: Double-click or schedule via Task Scheduler

## Recommended Schedule

### Best Times to Generate Picks

#### Morning Generation (Recommended)
- **Time**: 7:00 AM ET
- **Reason**: Early morning before games start
- **Covers**: Today's games + next day
- **Run**: `python generate_picks_smart.py`

#### Afternoon Update
- **Time**: 2:00 PM ET  
- **Reason**: Final update before evening games
- **Covers**: Tonight's games (MLB, NBA, NHL)
- **Run**: `python generate_picks_smart.py`

#### Late Evening Update (Optional)
- **Time**: 11:00 PM ET
- **Reason**: Update for next day's games
- **Covers**: Tomorrow's games
- **Run**: `python generate_picks_smart.py`

### Automated Cleanup (Every 5-10 minutes)
- **Frequency**: Every 5 minutes during game hours
- **Run**: `python move_completed_picks_to_scoring.py`
- **Covers**: Moving completed games to scoring

## Setting Up Windows Task Scheduler

### For Pick Generation (Morning/Afternoon)

1. Open Windows Task Scheduler
2. Create Basic Task
3. Name: "Generate Confident Picks - Morning"
4. Trigger: Daily at 7:00 AM
5. Action: Start a program
6. Program: `C:\Users\durel\Documents\confident-picks-restored\generate_picks_smart.py`
7. Arguments: (leave empty)
8. Start in: `C:\Users\durel\Documents\confident-picks-restored`

Repeat for afternoon (2:00 PM) and optionally evening (11:00 PM).

### For Completed Picks Migration (Every 5 minutes)

1. Create Basic Task
2. Name: "Move Completed Picks"
3. Trigger: Repeating every 5 minutes
4. Duration: Indefinitely
5. Action: Start a program
6. Program: `C:\Users\durel\Documents\confident-picks-restored\confident-picks-automation\move_completed_picks_to_scoring.py`
7. Arguments: (leave empty)
8. Start in: `C:\Users\durel\Documents\confident-picks-restored\confident-picks-automation`

## Alternative: Using run_pick_workflow.bat

If you prefer to run both scripts together:
1. Schedule `run_pick_workflow.bat` to run at your desired times
2. This runs both migration and generation in sequence

## What Happens With the Workflow

### 1. Completed Games → Scoring Collection
- Completed games automatically removed from Picks view
- They appear in Scorecard section for grading
- Original picks preserved in `all_picks` with 'completed' status

### 2. New Picks → All Picks Collection  
- Generated picks appear in Picks section immediately
- Only include games scheduled for today or future
- Automatically filtered for 70%+ confidence

### 3. User Experience
- Users see only upcoming games in Picks
- Completed games appear in Scorecard for grading
- No manual intervention needed

## Monitoring the System

### Check Script Success
- Scripts output results to console
- Check Windows Event Viewer for Task Scheduler logs
- Monitor Firebase Console for new documents in `all_picks` and `scoring`

### Test Manually
Run each script individually to verify:
```bash
# Test completed picks migration
python confident-picks-automation/move_completed_picks_to_scoring.py

# Test pick generation
python generate_picks_smart.py
```

## Troubleshooting

### Scripts not running on schedule
- Check Windows Task Scheduler status
- Verify Python path in Task Scheduler
- Check credentials file path is correct

### No picks generated
- Verify approved models exist in Firebase
- Check Google Sheets have upcoming games
- Ensure models have 70%+ confidence

### Completed games not moving
- Check `commenceTime` field in Firebase documents
- Verify script ran (check console output)
- Check Firebase permissions

## Next Steps

1. Run `generate_picks_smart.py` manually to test
2. Set up Task Scheduler for morning and afternoon generation
3. Set up Task Scheduler for every 5 minutes for cleanup
4. Monitor for 24 hours to ensure everything works
5. Adjust timing as needed

