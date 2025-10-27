#!/usr/bin/env python3
"""Delete NFL models with 100% accuracy (data leakage)"""

import firebase_admin
from firebase_admin import credentials, firestore

CREDS_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'

if not firebase_admin._apps:
    cred = credentials.Certificate(CREDS_FILE)
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("="*60)
print("DELETING NFL MODELS WITH 100% ACCURACY (DATA LEAKAGE)")
print("="*60)

docs = db.collection('approved_models').stream()

deleted = 0
for doc in docs:
    data = doc.to_dict()
    sport = data.get('sport', '')
    team = data.get('team', '')
    prop = data.get('prop', '')
    accuracy = data.get('currentAccuracy', 0)
    
    # Delete NFL models with 100% accuracy (data leakage)
    if sport == 'NFL' and accuracy == 100.0:
        print(f"Deleting: {sport}-{team}-{prop} ({accuracy}%)")
        doc.reference.delete()
        deleted += 1

print("\n" + "="*60)
print(f"Deleted {deleted} models with data leakage")
print("="*60)

