#!/usr/bin/env python3
"""Check which NHL teams have 70%+ models"""

import firebase_admin
from firebase_admin import credentials, firestore

CREDS_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'

if not firebase_admin._apps:
    cred = credentials.Certificate(CREDS_FILE)
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("NHL TEAMS WITH 70%+ MODELS:")
print("="*60)

docs = db.collection('approved_models').where(filter=firestore.FieldFilter('status', '==', 'approved')).stream()

ready_teams = set()
for doc in docs:
    data = doc.to_dict()
    if data.get('sport', '').upper() == 'NHL':
        team = data.get('team', '').upper()
        prop = data.get('prop', '')
        accuracy = data.get('current_accuracy', 0)
        
        if accuracy >= 70:
            ready_teams.add(team)
            print(f"{team} - {prop}: {accuracy}%")

print("\n" + "="*60)
print(f"Total teams with 70%+ models: {len(ready_teams)}")
print(f"Teams: {', '.join(sorted(ready_teams))}")

