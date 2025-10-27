#!/usr/bin/env python3
"""Check what models are actually in Firebase"""
import firebase_admin
from firebase_admin import credentials, firestore
import os

SERVICE_ACCOUNT_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'

# Initialize Firebase
cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("\n" + "="*80)
print("CHECKING FIREBASE APPROVED_MODELS COLLECTION")
print("="*80)

# Get all documents from approved_models
models_ref = db.collection('approved_models')
docs = models_ref.stream()

count = 0
for doc in docs:
    count += 1
    data = doc.to_dict()
    print(f"\n{count}. Document ID: {doc.id}")
    print(f"   Sport: {data.get('sport', 'N/A')}")
    print(f"   Team: {data.get('team', 'N/A')}")
    print(f"   Prop: {data.get('prop', 'N/A')}")
    print(f"   Model Name: {data.get('modelName', 'N/A')}")
    print(f"   Historical: {data.get('historicalAccuracy', 'N/A')}")
    print(f"   Current: {data.get('currentAccuracy', 'N/A')}")
    print(f"   Status: {data.get('status', 'N/A')}")

print(f"\n{'='*80}")
print(f"TOTAL MODELS IN FIREBASE: {count}")
print("="*80)

if count == 0:
    print("\n⚠️  No models found in Firebase!")
    print("The exhaustive testing scripts need to save models to Firebase when they find 70%+ accuracy.")
else:
    print(f"\n✅ Found {count} models in Firebase")
    print("\nIf these look like mock/test data, we need to:")
    print("1. Clear the collection")
    print("2. Ensure exhaustive testing scripts save to Firebase")


