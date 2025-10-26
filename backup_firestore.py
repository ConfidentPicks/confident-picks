#!/usr/bin/env python3
"""
Automated Firestore Backup Script
Exports all Firestore collections to JSON files
Run daily via Task Scheduler or cron
"""

import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
from datetime import datetime
import shutil

# Firebase credentials
CREDS_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'

# Backup directory
BACKUP_DIR = r'C:\Users\durel\Documents\confident-picks-backups'

# Collections to backup
COLLECTIONS = [
    'approved_models',
    'all_picks',
    'nfl_picks',
    'nhl_picks',
    'nhl_test_picks',
    'nhl_completed_picks',
    'users',
    'subscriptions',
]

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        cred = credentials.Certificate(CREDS_FILE)
        firebase_admin.initialize_app(cred)
    return firestore.client()

def create_backup_directory():
    """Create backup directory with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_path = os.path.join(BACKUP_DIR, timestamp)
    os.makedirs(backup_path, exist_ok=True)
    return backup_path

def backup_collection(db, collection_name, backup_path):
    """Backup a single collection to JSON"""
    print(f"Backing up collection: {collection_name}")
    
    try:
        # Get all documents
        docs = db.collection(collection_name).stream()
        
        # Convert to list of dicts
        data = []
        count = 0
        for doc in docs:
            doc_data = doc.to_dict()
            doc_data['_id'] = doc.id  # Preserve document ID
            data.append(doc_data)
            count += 1
        
        # Save to JSON file
        filename = os.path.join(backup_path, f'{collection_name}.json')
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"   [OK] Backed up {count} documents to {collection_name}.json")
        return count
        
    except Exception as e:
        print(f"   [ERROR] Error backing up {collection_name}: {e}")
        return 0

def create_backup_summary(backup_path, stats):
    """Create a summary file for the backup"""
    summary = {
        'backup_date': datetime.now().isoformat(),
        'total_documents': sum(stats.values()),
        'collections': stats,
    }
    
    filename = os.path.join(backup_path, '_backup_summary.json')
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nBackup Summary:")
    print(f"   Total Documents: {summary['total_documents']}")
    for collection, count in stats.items():
        print(f"   - {collection}: {count} documents")

def cleanup_old_backups(keep_days=30):
    """Delete backups older than specified days"""
    print(f"\nCleaning up backups older than {keep_days} days...")
    
    if not os.path.exists(BACKUP_DIR):
        return
    
    current_time = datetime.now()
    deleted = 0
    
    for backup_folder in os.listdir(BACKUP_DIR):
        backup_path = os.path.join(BACKUP_DIR, backup_folder)
        
        if not os.path.isdir(backup_path):
            continue
        
        # Get folder creation time
        folder_time = datetime.fromtimestamp(os.path.getctime(backup_path))
        age_days = (current_time - folder_time).days
        
        if age_days > keep_days:
            try:
                shutil.rmtree(backup_path)
                print(f"   [DELETED] Backup: {backup_folder} (age: {age_days} days)")
                deleted += 1
            except Exception as e:
                print(f"   [ERROR] Error deleting {backup_folder}: {e}")
    
    if deleted == 0:
        print(f"   [OK] No old backups to delete")
    else:
        print(f"   [OK] Deleted {deleted} old backup(s)")

def main():
    """Main backup function"""
    print("=" * 60)
    print("FIRESTORE BACKUP STARTING")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    try:
        # Initialize Firebase
        db = initialize_firebase()
        
        # Create backup directory
        backup_path = create_backup_directory()
        print(f"Backup location: {backup_path}")
        print("")
        
        # Backup each collection
        stats = {}
        for collection in COLLECTIONS:
            count = backup_collection(db, collection, backup_path)
            stats[collection] = count
        
        # Create summary
        create_backup_summary(backup_path, stats)
        
        # Cleanup old backups
        cleanup_old_backups(keep_days=30)
        
        print("")
        print("=" * 60)
        print("[SUCCESS] BACKUP COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    except Exception as e:
        print("")
        print("=" * 60)
        print(f"[FAILED] BACKUP FAILED: {e}")
        print("=" * 60)
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())

