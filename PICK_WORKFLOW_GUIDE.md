# Pick Workflow Guide

## Current System Status

### What's Working ✅

1. **Frontend Date Filtering**: The `loadFirebaseData()` function now filters picks to show only future games (games that haven't started yet)
   - Completed games are automatically excluded from the Picks view
   - All games for today and tomorrow will be displayed in the Picks section

### What Needs to Be Automated 🔧

The system needs an automated workflow to move completed games from `all_picks` collection to the `scoring` collection when games start. Currently, this is not implemented.

## Recommended Workflow

### Option 1: Firebase Cloud Function (Recommended)
Create a Cloud Function that runs periodically (every 1 minute) to:
1. Query `all_picks` collection for picks with `status: 'active'` and `commenceTime < now`
2. Move these picks to the `scoring` collection with `status: 'pending'`
3. Update the pick in `all_picks` to `status: 'completed'` or remove it

### Option 2: Client-Side Check (Current Implemented but Not Used)
The function `moveCompletedGamesToScoring()` exists in `index.html` but is not actively being called. This could be:
- Called periodically when the app loads
- Called on user action (refresh button)
- Triggered by a webhook when games start

### Option 3: Backend Script (Scheduled Task)
Create a Python script that:
1. Runs every 1-5 minutes (using Windows Task Scheduler)
2. Queries Firebase for completed games
3. Moves them to the scoring collection
4. Updates their status

## Implementation Steps

### Immediate Fix for Date Filtering
The frontend now filters to show only future games, so users will see:
- Games scheduled for today (Oct 26, 2025)
- Games scheduled for tomorrow (Oct 27, 2025)
- No completed games

### Next Steps for Complete Workflow

1. **Create a migration script** to move existing completed games from `all_picks` to `scoring`
2. **Set up automated monitoring** (Cloud Function, scheduled script, or client-side refresh)
3. **Test the workflow** with a few completed games to ensure data integrity

## Testing the Current Changes

1. Refresh the app - you should now see only future games in the Picks section
2. Check the browser console for logs showing:
   - `✅ Including future game:` for games being shown
   - `⏭️ Skipping completed game:` for games being hidden
3. Verify that completed games from Oct 26 (if any have already started) are not displayed

## Questions for User

1. Do we want to create a Cloud Function for automatic migration?
2. Should we implement a manual "Refresh Picks" button for admin users?
3. Do we need to migrate existing completed games from `all_picks` to `scoring` immediately?

