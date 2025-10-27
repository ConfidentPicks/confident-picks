#!/usr/bin/env python3
"""Check actual field names in Firebase approved_models"""

import firebase_admin
from firebase_admin import credentials, firestore

CREDS_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'

if not firebase_admin._apps:
    cred = credentials.Certificate(CREDS_FILE)
    firebase_admin.initialize_app(cred)

db = firestore.client()

docs = db.collection('approved_models').limit(1).stream()

for doc in docs:
    data = doc.to_dict()
    print("FIREBASE FIELD NAMES:")
    print("="*60)
    for key, value in data.items():
        print(f"  {key}: {value}")
    break

