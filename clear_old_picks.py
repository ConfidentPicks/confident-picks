#!/usr/bin/env python3
"""Clear old picks from Firebase collections"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase
CREDS_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'

if not firebase_admin._apps:
    cred = credentials.Certificate(CREDS_FILE)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def clear_collection(collection_name):
    """Delete all documents from a collection"""
    print(f"\n{'='*60}")
    print(f"Clearing: {collection_name}")
    print(f"{'='*60}")
    
    docs = db.collection(collection_name).stream()
    deleted = 0
    
    for doc in docs:
        print(f"  Deleting: {doc.id}")
        doc.reference.delete()
        deleted += 1
    
    print(f"\n✅ Deleted {deleted} documents from {collection_name}")
    return deleted

def main():
    print("\n" + "="*60)
    print("CLEARING OLD PICKS FROM FIREBASE")
    print("="*60)
    
    # Collections that might have old picks
    collections_to_clear = [
        'all_picks',
        'live_picks',
        'test_picks',
        'nhl_test_picks',
        # Add more if needed
    ]
    
    total_deleted = 0
    
    for collection in collections_to_clear:
        try:
            deleted = clear_collection(collection)
            total_deleted += deleted
        except Exception as e:
            print(f"❌ Error clearing {collection}: {e}")
    
    print("\n" + "="*60)
    print(f"TOTAL DELETED: {total_deleted} picks")
    print("="*60)
    print("\n✅ All old picks cleared!")
    print("Now you can generate fresh picks with your new models.")

if __name__ == '__main__':
    confirm = input("\n⚠️  This will DELETE all picks from Firebase. Continue? (yes/no): ")
    if confirm.lower() == 'yes':
        main()
    else:
        print("Cancelled.")

