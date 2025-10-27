#!/usr/bin/env python3
"""Check if picks exist in Firebase all_picks collection"""

import firebase_admin
from firebase_admin import credentials, firestore

CREDS_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'

if not firebase_admin._apps:
    cred = credentials.Certificate(CREDS_FILE)
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("="*60)
print("CHECKING FIREBASE all_picks COLLECTION")
print("="*60)

docs = db.collection('all_picks').stream()

picks = []
for doc in docs:
    data = doc.to_dict()
    picks.append({
        'id': doc.id,
        'game': data.get('game', 'N/A'),
        'pick': data.get('pick', 'N/A'),
        'confidence': data.get('confidence', 0)
    })

print(f"\nTotal picks in Firebase: {len(picks)}")

if picks:
    print("\nPicks found:")
    for pick in picks[:10]:  # Show first 10
        print(f"  {pick['game']} - {pick['pick']} ({pick['confidence']*100:.1f}%)")
    if len(picks) > 10:
        print(f"  ... and {len(picks)-10} more")
else:
    print("\n❌ NO PICKS FOUND IN FIREBASE!")
    print("The all_picks collection is empty.")

print("\n" + "="*60)

