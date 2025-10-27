#!/usr/bin/env python3
"""Monitor Firebase approved_models collection in real-time"""
import firebase_admin
from firebase_admin import credentials, firestore
import time
import os

SERVICE_ACCOUNT_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("\n" + "="*80)
print("MONITORING FIREBASE APPROVED_MODELS COLLECTION")
print("="*80)
print("Watching for new models being saved...")
print("Press Ctrl+C to stop")
print("="*80 + "\n")

last_count = 0

try:
    while True:
        # Get all documents from approved_models
        models_ref = db.collection('approved_models')
        docs = list(models_ref.stream())
        
        current_count = len(docs)
        
        if current_count != last_count:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n" + "="*80)
            print(f"FIREBASE MODELS: {current_count} total")
            print("="*80)
            
            # Group by sport and prop
            by_sport_prop = {}
            for doc in docs:
                data = doc.to_dict()
                sport = data.get('sport', 'Unknown')
                prop = data.get('prop', 'Unknown')
                key = f"{sport} - {prop}"
                if key not in by_sport_prop:
                    by_sport_prop[key] = []
                by_sport_prop[key].append(data)
            
            # Display summary
            for key, models in sorted(by_sport_prop.items()):
                print(f"\n{key}: {len(models)} teams")
                for model in sorted(models, key=lambda x: x.get('historicalAccuracy', 0), reverse=True)[:10]:
                    team = model.get('team', 'Unknown')
                    hist = model.get('historicalAccuracy', 0)
                    curr = model.get('currentAccuracy', 0)
                    status = model.get('status', 'Unknown')
                    print(f"  • {team:5s} - Historical: {hist:5.1f}% | Current: {curr:5.1f}% | {status}")
            
            print("\n" + "="*80)
            print(f"Last updated: {time.strftime('%I:%M:%S %p')}")
            print("="*80)
            
            last_count = current_count
        
        time.sleep(5)  # Check every 5 seconds
        
except KeyboardInterrupt:
    print("\n\nMonitoring stopped.")


