#!/usr/bin/env python3
"""Check stats for a specific model"""

import firebase_admin
from firebase_admin import credentials, firestore
import sys

CREDS_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'

if not firebase_admin._apps:
    cred = credentials.Certificate(CREDS_FILE)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Search for the model
model_name = "NFL-ML-v50-Ra"
print(f"Searching for model: {model_name}")
print("="*60)

docs = db.collection('approved_models').stream()

found = False
for doc in docs:
    data = doc.to_dict()
    if data.get('model_name') == model_name or data.get('modelName') == model_name:
        found = True
        print(f"\nModel ID: {doc.id}")
        print(f"Model Name: {data.get('model_name', data.get('modelName', 'N/A'))}")
        print(f"Sport: {data.get('sport', 'N/A')}")
        print(f"Team: {data.get('team', 'N/A')}")
        print(f"Prop: {data.get('prop', 'N/A')}")
        print(f"\nAccuracy Stats:")
        print(f"  Historical Accuracy: {data.get('historicalAccuracy', data.get('historical_accuracy', 'N/A'))}%")
        print(f"  Current Season Accuracy: {data.get('currentAccuracy', data.get('current_accuracy', 'N/A'))}%")
        print(f"\nTraining Info:")
        print(f"  Training Samples: {data.get('trainingSamples', data.get('training_samples', 'N/A'))}")
        print(f"  Test Samples: {data.get('testSamples', data.get('test_samples', 'N/A'))}")
        print(f"  Model Type: {data.get('modelType', data.get('model_type', 'N/A'))}")
        print(f"  Version: {data.get('version', 'N/A')}")
        print(f"\nStatus:")
        print(f"  Approved: {data.get('approved', 'N/A')}")
        print(f"  Created: {data.get('createdAt', data.get('created_at', 'N/A'))}")
        print(f"  Updated: {data.get('updatedAt', data.get('updated_at', 'N/A'))}")
        print("\nAll Fields:")
        for key, value in sorted(data.items()):
            print(f"  {key}: {value}")
        print("="*60)

if not found:
    print(f"\n❌ Model '{model_name}' not found in approved_models collection")
    print("\nSearching all models to see what's available...")
    
    docs = db.collection('approved_models').limit(5).stream()
    print("\nSample models in database:")
    for doc in docs:
        data = doc.to_dict()
        print(f"  - {data.get('model_name', data.get('modelName', doc.id))}")

