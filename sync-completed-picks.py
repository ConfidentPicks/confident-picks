#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import firebase_admin
from firebase_admin import credentials, firestore
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from datetime import datetime, timezone
import csv

def sync_completed_picks_firebase_to_sheet():
    print('SYNCING COMPLETED PICKS FROM FIREBASE TO GOOGLE SHEET')
    print('=' * 60)
    
    try:
        # Initialize Firebase Admin
        cred = credentials.Certificate('C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json')
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        
        # Get all completed picks from Firebase
        completed_ref = db.collection('completed_picks')
        completed_docs = completed_ref.stream()
        
        # Prepare data for Google Sheet
        sheet_data = []
        
        # Add headers
        headers = [
            'ID', 'Game', 'Away Team', 'Home Team', 'Pick Type', 'Pick Team', 
            'Pick Description', 'Odds', 'Confidence', 'Result', 'Status',
            'Start Time', 'Settled At', 'League', 'Market Type', 'Reasoning',
            'Created At', 'Last Updated', 'Graded At', 'Notes',
            'Win Loss', 'Is Winner', 'Confidence Level', 'Is Enhanced', 'Source'
        ]
        sheet_data.append(headers)
        
        # Add data rows
        for doc in completed_docs:
            data = doc.to_dict()
            row = [
                doc.id,  # Use document ID as ID
                data.get('game', ''),
                data.get('away_team', ''),
                data.get('home_team', ''),
                data.get('pick_type', ''),
                data.get('pick_team', ''),
                data.get('pick_description', ''),
                data.get('odds', ''),
                data.get('confidence', ''),
                data.get('result', ''),
                data.get('status', ''),
                data.get('start_time', ''),
                data.get('settled_at', ''),
                data.get('league', ''),
                data.get('market_type', ''),
                data.get('reasoning', ''),
                data.get('created_at', ''),
                data.get('last_updated', ''),
                data.get('graded_at', ''),
                data.get('notes', ''),
                # Enhanced fields
                data.get('win_loss', ''),
                data.get('is_winner', ''),
                data.get('confidence_level', ''),
                data.get('is_enhanced', ''),
                data.get('source', '')
            ]
            sheet_data.append(row)
        
        # Write to CSV file
        csv_filename = 'completed_picks_sync_data.csv'
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(sheet_data)
        
        print(f'Exported {len(sheet_data)-1} completed picks to {csv_filename}')
        print(f'Data includes {len(sheet_data)-1} completed picks with enhanced fields')
        
        # Show sample of data
        print('\nSample data:')
        for i, row in enumerate(sheet_data[:3]):  # Show first 3 rows (header + 2 data rows)
            print(f'  Row {i+1}: {row[:5]}...')  # Show first 5 columns
        
        return True
        
    except Exception as e:
        print(f'Error syncing to CSV: {str(e)}')
        return False

def sync_completed_picks_sheet_to_firebase():
    print('SYNCING COMPLETED PICKS FROM GOOGLE SHEET TO FIREBASE')
    print('=' * 60)
    
    try:
        # Initialize Google Sheets API
        scope = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_file('C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json', scopes=scope)
        service = build('sheets', 'v4', credentials=creds)
        
        # Get the spreadsheet ID
        spreadsheet_id = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
        
        # Read from completed_picks tab
        range_name = 'completed_picks!A1:Z1000'  # Adjust range as needed
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print('No data found in completed_picks tab')
            return False
        
        # Get headers (first row)
        headers = values[0]
        print(f'Found headers: {headers[:10]}...')  # Show first 10 headers
        
        # Initialize Firebase Admin
        cred = credentials.Certificate('C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json')
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        completed_ref = db.collection('completed_picks')
        
        # Process each row
        updated_count = 0
        for i, row in enumerate(values[1:], 1):  # Skip header row
            if len(row) < len(headers):
                # Pad row with empty strings if it's shorter than headers
                row.extend([''] * (len(headers) - len(row)))
            
            pick_data = dict(zip(headers, row))
            
            # Get the ID from the first column
            pick_id = pick_data.get('ID', '')
            if not pick_id:
                continue
            
            # Create update data
            update_data = {
                'game': pick_data.get('Game', ''),
                'away_team': pick_data.get('Away Team', ''),
                'home_team': pick_data.get('Home Team', ''),
                'pick_type': pick_data.get('Pick Type', ''),
                'pick_team': pick_data.get('Pick Team', ''),
                'pick_description': pick_data.get('Pick Description', ''),
                'odds': pick_data.get('Odds', ''),
                'confidence': pick_data.get('Confidence', ''),
                'result': pick_data.get('Result', ''),
                'status': pick_data.get('Status', 'completed'),
                'start_time': pick_data.get('Start Time', ''),
                'settled_at': pick_data.get('Settled At', ''),
                'league': pick_data.get('League', 'NFL'),
                'market_type': pick_data.get('Market Type', ''),
                'reasoning': pick_data.get('Reasoning', ''),
                'notes': pick_data.get('Notes', ''),
                'graded_at': pick_data.get('Graded At', ''),
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'source': 'google_sheet_sync'
            }
            
            # Update enhanced fields if they exist
            if 'Win Loss' in pick_data:
                update_data['win_loss'] = pick_data.get('Win Loss', '')
            if 'Is Winner' in pick_data:
                update_data['is_winner'] = pick_data.get('Is Winner', '')
            if 'Confidence Level' in pick_data:
                update_data['confidence_level'] = pick_data.get('Confidence Level', '')
            
            # Update Firebase document
            doc_ref = completed_ref.document(pick_id)
            doc_ref.update(update_data)
            updated_count += 1
        
        print(f'Updated {updated_count} completed picks in Firebase')
        return True
        
    except Exception as e:
        print(f'Error syncing from sheet: {str(e)}')
        return False

def main():
    print('COMPLETED PICKS TWO-WAY SYNC')
    print('=' * 60)
    
    print('\nChoose sync direction:')
    print('1. Firebase -> Google Sheet (Export to CSV)')
    print('2. Google Sheet -> Firebase (Import from Sheet)')
    print('3. Both directions')
    
    choice = input('\nEnter choice (1/2/3): ').strip()
    
    if choice == '1':
        success = sync_completed_picks_firebase_to_sheet()
        if success:
            print('\nFirebase to Google Sheet sync completed!')
            print('Import the CSV file into your completed_picks tab.')
    elif choice == '2':
        success = sync_completed_picks_sheet_to_firebase()
        if success:
            print('\nGoogle Sheet to Firebase sync completed!')
    elif choice == '3':
        success1 = sync_completed_picks_firebase_to_sheet()
        success2 = sync_completed_picks_sheet_to_firebase()
        if success1 and success2:
            print('\nTwo-way sync completed!')
    else:
        print('Invalid choice. Exiting.')

if __name__ == "__main__":
    main()
