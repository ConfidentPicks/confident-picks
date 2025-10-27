#!/usr/bin/env python3
"""Check if today's NHL teams have 70%+ models"""

import firebase_admin
from firebase_admin import credentials, firestore

CREDS_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'

if not firebase_admin._apps:
    cred = credentials.Certificate(CREDS_FILE)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Teams playing today
todays_teams = ['COL', 'NJD', 'VGK', 'TBL', 'SJS', 'MIN', 'LAK', 'CHI', 'DAL', 'NSH', 'NYR', 'CGY', 'EDM', 'VAN', 'WPG']

print("NHL MODELS FOR TODAY'S TEAMS:")
print("="*60)

docs = db.collection('approved_models').where(filter=firestore.FieldFilter('status', '==', 'approved')).stream()

for doc in docs:
    data = doc.to_dict()
    if data.get('sport', '').upper() == 'NHL':
        team = data.get('team', '').upper()
        if team in todays_teams:
            prop = data.get('prop', '')
            accuracy = data.get('current_accuracy', 0)
            
            status = "READY" if accuracy >= 70 else "TOO LOW"
            print(f"{team} - {prop}: {accuracy}% [{status}]")

print("\n" + "="*60)
print("Only models with 70%+ will generate picks")

