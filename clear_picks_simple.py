#!/usr/bin/env python3
"""Clear all picks from Firebase"""

import firebase_admin
from firebase_admin import credentials, firestore

CREDS_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'

if not firebase_admin._apps:
    cred = credentials.Certificate(CREDS_FILE)
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("Clearing all_picks collection...")
docs = db.collection('all_picks').stream()
deleted = 0
for doc in docs:
    doc.reference.delete()
    deleted += 1

print(f"Deleted {deleted} picks")

