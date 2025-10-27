#!/usr/bin/env python3
"""
Move Completed Picks to Scoring Collection
==========================================
This script automatically moves completed games from all_picks to scoring collection
Run this script every 5-10 minutes to keep the picks section clean.

Schedule this script to run every 5-10 minutes:
- Windows Task Scheduler
- Or setup a cron job
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone
import sys

# Firebase setup
CREDS_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'

if not firebase_admin._apps:
    cred = credentials.Certificate(CREDS_FILE)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def move_completed_picks():
    """Move completed picks from all_picks to scoring collection"""
    print("=" * 60)
    print("MOVING COMPLETED PICKS TO SCORING")
    print("=" * 60)
    
    try:
        # Get current time
        now = datetime.now(timezone.utc)
        print(f"Current time: {now.isoformat()}")
        
        # Query all active picks
        all_picks_ref = db.collection('all_picks')
        active_picks = all_picks_ref.where('status', '==', 'active').stream()
        
        completed_picks = []
        for doc in active_picks:
            data = doc.to_dict()
            
            # Check if game has started
            commence_time = data.get('commenceTime') or data.get('startTime') or data.get('gameTime')
            if not commence_time:
                continue
            
            # Convert to datetime
            if isinstance(commence_time, str):
                game_time = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
            elif hasattr(commence_time, 'timestamp'):
                game_time = commence_time
            else:
                continue
            
            # If game time is in the past, mark as completed
            if game_time < now:
                completed_picks.append({
                    'id': doc.id,
                    'data': data
                })
        
        print(f"Found {len(completed_picks)} completed picks")
        
        if len(completed_picks) == 0:
            print("✅ No completed picks to move")
            return 0
        
        # Move completed picks to scoring collection
        moved_count = 0
        for pick in completed_picks:
            try:
                # Create document in scoring collection
                scoring_data = {
                    **pick['data'],
                    'status': 'pending',
                    'movedToScoringAt': now.isoformat(),
                    'originalCollection': 'all_picks',
                    'originalDocId': pick['id']
                }
                
                # Copy to scoring collection
                db.collection('scoring').document(pick['id']).set(scoring_data)
                
                # Update status in all_picks to 'completed'
                db.collection('all_picks').document(pick['id']).update({
                    'status': 'completed',
                    'completedAt': now.isoformat()
                })
                
                moved_count += 1
                print(f"✅ Moved pick: {pick['id']}")
                
            except Exception as e:
                print(f"❌ Error moving pick {pick['id']}: {e}")
        
        print(f"✅ Successfully moved {moved_count} picks to scoring")
        return moved_count
        
    except Exception as e:
        print(f"❌ Error in move_completed_picks: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    print("\n🚀 Starting completed picks migration...\n")
    moved = move_completed_picks()
    print(f"\n✅ Migration complete! Moved {moved} picks.")
    sys.exit(0 if moved >= 0 else 1)


