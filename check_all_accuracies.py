#!/usr/bin/env python3
"""Check accuracies of all models in Firebase"""

import firebase_admin
from firebase_admin import credentials, firestore

CREDS_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'

if not firebase_admin._apps:
    cred = credentials.Certificate(CREDS_FILE)
    firebase_admin.initialize_app(cred)

db = firestore.client()

docs = db.collection('approved_models').stream()

print("ALL MODEL ACCURACIES:")
print("="*80)

count_by_accuracy = {}
for doc in docs:
    data = doc.to_dict()
    sport = data.get('sport', 'UNKNOWN')
    team = data.get('team', 'UNKNOWN')
    prop = data.get('prop', 'UNKNOWN')
    current = data.get('currentAccuracy', 0)
    historical = data.get('historicalAccuracy', 0)
    
    key = f"{current}%"
    if key not in count_by_accuracy:
        count_by_accuracy[key] = []
    count_by_accuracy[key].append(f"{sport}-{team}-{prop}")

print("\nMODELS GROUPED BY ACCURACY:")
for accuracy in sorted(count_by_accuracy.keys(), key=lambda x: float(x.replace('%', '')), reverse=True):
    models = count_by_accuracy[accuracy]
    print(f"\n{accuracy}: {len(models)} models")
    for model in models[:3]:  # Show first 3
        print(f"  - {model}")
    if len(models) > 3:
        print(f"  ... and {len(models)-3} more")

print("\n" + "="*80)
print(f"Total models: {sum(len(v) for v in count_by_accuracy.values())}")

