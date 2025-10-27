#!/usr/bin/env python3
"""Check for models with 100% accuracy"""

import firebase_admin
from firebase_admin import credentials, firestore

CREDS_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'

if not firebase_admin._apps:
    cred = credentials.Certificate(CREDS_FILE)
    firebase_admin.initialize_app(cred)

db = firestore.client()

docs = db.collection('approved_models').stream()

perfect_models = []
for doc in docs:
    data = doc.to_dict()
    sport = data.get('sport', '')
    team = data.get('team', '')
    prop = data.get('prop', '')
    
    # Check both field name variations
    current_acc = data.get('currentAccuracy', data.get('current_accuracy', 0))
    historical_acc = data.get('historicalAccuracy', data.get('historical_accuracy', 0))
    
    if current_acc == 100.0 or historical_acc == 100.0:
        perfect_models.append({
            'id': doc.id,
            'sport': sport,
            'team': team,
            'prop': prop,
            'current': current_acc,
            'historical': historical_acc
        })

print(f"Models with 100% accuracy: {len(perfect_models)}")
if perfect_models:
    print("\nModels to delete:")
    for model in perfect_models:
        print(f"  {model['sport']}-{model['team']}-{model['prop']}: Current={model['current']}%, Historical={model['historical']}%")

