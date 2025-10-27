#!/usr/bin/env python3

"""
SYNC SHEET CHANGES TO FIREBASE
==============================

This script reads changes from the Google Sheet and pushes them to Firebase.
Use this when you've made edits in the "Firebase Picks" sheet and want to sync them.

USAGE:
- Run manually: python sync_sheet_to_firebase.py
- Integrate: Import and call sync_sheet_changes_to_firebase()
"""

import pandas as pd
import numpy as np
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import firebase_admin
from firebase_admin import credentials, firestore
import warnings
warnings.filterwarnings('ignore')

# Configuration
SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU'
SERVICE_ACCOUNT_FILE = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_sheets_service():
    """Get Google Sheets service"""
    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('sheets', 'v4', credentials=credentials)

def get_firestore_client():
    """Get Firestore client"""
    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
        firebase_admin.initialize_app(cred)
    return firestore.client()

def sync_sheet_changes_to_firebase():
    """Read changes from Google Sheet and push to Firebase"""
    print("=" * 80)
    print("SYNCING SHEET CHANGES TO FIREBASE")
    print("=" * 80)
    
    service = get_sheets_service()
    db = get_firestore_client()
    
    try:
        # Read data from Firebase Picks sheet
        range_name = "Firebase Picks!A2:P1000"  # Skip header row
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
        data = result.get('values', [])
        
        if not data:
            print("No data found in Firebase Picks sheet")
            return
        
        print(f"Found {len(data)} rows in Firebase Picks sheet")
        
        updated_count = 0
        error_count = 0
        
        for i, row in enumerate(data):
            if len(row) < 16:  # Ensure we have all columns
                print(f"Row {i+2}: Insufficient data, skipping")
                continue
            
            doc_id = row[0] if len(row) > 0 else ""
            if not doc_id:
                continue
            
            try:
                # Create pick card object from sheet data
                pick_card = {
                    'game': row[1] if len(row) > 1 else "",
                    'away_team': row[2] if len(row) > 2 else "",
                    'home_team': row[3] if len(row) > 3 else "",
                    'pick_type': row[4] if len(row) > 4 else "",
                    'pick_team': row[5] if len(row) > 5 else "",
                    'confidence_level': row[6] if len(row) > 6 else "",
                    'model_confidence': row[7] if len(row) > 7 else "",
                    'team_accuracy': float(row[8]) if len(row) > 8 and row[8] else 0,
                    'reasoning_part1': row[9] if len(row) > 9 else "",
                    'reasoning_part2': row[10] if len(row) > 10 else "",
                    'reasoning_part3': row[11] if len(row) > 11 else "",
                    'game_date': row[12] if len(row) > 12 else "",
                    'status': row[13] if len(row) > 13 else "test",
                    'last_updated': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Update Firebase
                doc_ref = db.collection('test_picks').document(doc_id)
                doc_ref.set(pick_card)
                
                print(f"Updated Firebase: {pick_card['game']} - {pick_card['pick_team']} {pick_card['pick_type']}")
                updated_count += 1
                
                # Update Firebase Status in sheet
                status_range = f"Firebase Picks!P{i+2}"
                service.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=status_range,
                    valueInputOption='RAW',
                    body={'values': [['Updated']]}
                ).execute()
                
            except Exception as e:
                print(f"Error updating row {i+2}: {str(e)}")
                error_count += 1
                
                # Update Firebase Status in sheet to show error
                status_range = f"Firebase Picks!P{i+2}"
                service.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=status_range,
                    valueInputOption='RAW',
                    body={'values': [['Error: ' + str(e)[:50]]]}
                ).execute()
        
        print(f"\n{'='*80}")
        print("SYNC SUMMARY")
        print(f"{'='*80}")
        print(f"Successfully updated: {updated_count}")
        print(f"Errors: {error_count}")
        print(f"Total rows processed: {len(data)}")
        
        if error_count > 0:
            print(f"\n{error_count} rows had errors. Check the Firebase Status column in the sheet.")
        else:
            print(f"\nAll changes successfully synced to Firebase!")
            
    except Exception as e:
        print(f"Error reading from sheet: {str(e)}")

if __name__ == "__main__":
    sync_sheet_changes_to_firebase()