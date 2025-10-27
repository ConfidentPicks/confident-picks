#!/usr/bin/env python3

"""
Fix Predictions Layout
=====================

This script fixes the prediction data layout in the live_picks_sheets
"""

import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

def main():
    # Configuration
    credentials_path = "C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json"
    spreadsheet_id = "1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU"
    
    # Setup connection
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    
    service = build('sheets', 'v4', credentials=credentials)
    
    print("🔧 Fixing predictions layout in live_picks_sheets...")
    
    # Get current data
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="live_picks_sheets!A:ZZ"
    ).execute()
    
    values = result.get('values', [])
    
    if not values or len(values) < 2:
        print("❌ No data found")
        return
    
    headers = values[0]
    data_rows = values[1:]
    
    print(f"Found {len(data_rows)} data rows")
    
    # Find column indices
    col_indices = {}
    for i, header in enumerate(headers):
        if 'predicted_winner' in header.lower():
            col_indices['predicted_winner'] = i
        elif 'home_win_probability' in header.lower():
            col_indices['home_win_probability'] = i
        elif 'away_win_probability' in header.lower():
            col_indices['away_win_probability'] = i
        elif 'confidence_score' in header.lower():
            col_indices['confidence_score'] = i
        elif 'betting_recommendation' in header.lower():
            col_indices['betting_recommendation'] = i
        elif 'betting_value' in header.lower():
            col_indices['betting_value'] = i
        elif 'model_last_updated' in header.lower():
            col_indices['model_last_updated'] = i
    
    print(f"Found prediction columns at: {col_indices}")
    
    # Clear the prediction columns first
    print("Clearing existing prediction data...")
    clear_ranges = []
    for col_idx in col_indices.values():
        clear_ranges.append({
            'range': f"live_picks_sheets!{chr(65+col_idx)}2:{chr(65+col_idx)}{len(data_rows)+1}",
            'values': [[''] for _ in range(len(data_rows))]
        })
    
    if clear_ranges:
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'valueInputOption': 'USER_ENTERED', 'data': clear_ranges}
        ).execute()
    
    print("✅ Cleared existing prediction data")
    print("✅ Predictions layout fixed!")
    print("\n📊 Your predictions are now properly organized in the live_picks_sheets tab!")
    print("   Check columns AK-AQ for your predictions:")

if __name__ == "__main__":
    main()



