#!/usr/bin/env python3
"""Check detailed pick data in Firebase"""

import firebase_admin
from firebase_admin import credentials, firestore
import json

CREDS_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'

if not firebase_admin._apps:
    cred = credentials.Certificate(CREDS_FILE)
    firebase_admin.initialize_app(cred)

db = firestore.client()

docs = db.collection('all_picks').limit(2).stream()

print("SAMPLE PICK DATA:")
print("="*60)

for i, doc in enumerate(docs, 1):
    data = doc.to_dict()
    print(f"\nPick {i}: {doc.id}")
    print(json.dumps(data, indent=2, default=str))
    print("-"*60)

