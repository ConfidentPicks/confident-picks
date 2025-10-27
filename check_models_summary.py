#!/usr/bin/env python3
"""Check what models we have in Firebase"""

import firebase_admin
from firebase_admin import credentials, firestore

CREDS_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'

if not firebase_admin._apps:
    cred = credentials.Certificate(CREDS_FILE)
    firebase_admin.initialize_app(cred)

db = firestore.client()

docs = db.collection('approved_models').where(filter=firestore.FieldFilter('status', '==', 'approved')).stream()

models_by_sport = {}
for doc in docs:
    data = doc.to_dict()
    sport = data.get('sport', 'UNKNOWN')
    team = data.get('team', 'UNKNOWN')
    prop = data.get('prop', 'UNKNOWN')
    
    if sport not in models_by_sport:
        models_by_sport[sport] = []
    models_by_sport[sport].append(f"{team} - {prop}")

print("APPROVED MODELS BY SPORT:")
print("="*60)
for sport, models in models_by_sport.items():
    print(f"\n{sport}: {len(models)} models")
    for model in sorted(models)[:5]:  # Show first 5
        print(f"  - {model}")
    if len(models) > 5:
        print(f"  ... and {len(models)-5} more")

