#!/usr/bin/env python3

"""
Check Google Sheets Column Structure
===================================

This script checks what columns are actually in your Google Sheets
so we can fix the prediction system.
"""

import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

def check_sheet_columns():
    """Check the column structure of your Google Sheets"""
    
    # Configuration
    credentials_path = "C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json"
    spreadsheet_id = "1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU"
    
    # Setup Google Sheets connection
    try:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        service = build('sheets', 'v4', credentials=credentials)
        print("✅ Google Sheets connection established")
        
    except Exception as e:
        print(f"❌ Error connecting to Google Sheets: {e}")
        return
    
    # Check different sheets
    sheets_to_check = [
        "historical_game_results_2021_2024",
        "historical_team_stats_2021_2024", 
        "upcoming_games",
        "live_picks_sheets"
    ]
    
    for sheet_name in sheets_to_check:
        print(f"\n📊 Checking {sheet_name}:")
        print("-" * 40)
        
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A1:Z10"
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                print(f"  ⚠️ No data found")
                continue
            
            # Show headers
            headers = values[0]
            print(f"  Columns ({len(headers)}):")
            for i, header in enumerate(headers):
                print(f"    {i+1:2d}. {header}")
            
            # Show sample data
            if len(values) > 1:
                print(f"  Sample data (first row):")
                sample_data = values[1]
                for i, (header, value) in enumerate(zip(headers, sample_data)):
                    print(f"    {header}: {value}")
            
        except Exception as e:
            print(f"  ❌ Error reading {sheet_name}: {e}")

if __name__ == "__main__":
    check_sheet_columns()



