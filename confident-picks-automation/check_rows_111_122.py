#!/usr/bin/env python3

import pandas as pd
import numpy as np
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
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

def check_rows_111_122():
    """Check what's actually in rows 111-122"""
    print("=" * 70)
    print("CHECKING WHAT'S IN ROWS 111-122")
    print("=" * 70)
    
    service = get_sheets_service()
    
    # Get specific rows 111-122
    range_name = "upcoming_games!A111:K122"  # Rows 111-122
    
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = result.get('values', [])
    
    if not values:
        print("No data found!")
        return
    
    print("Raw data in rows 111-122:")
    print("-" * 70)
    
    for i, row in enumerate(values):
        row_number = 111 + i  # Actual row number in sheet
        print(f"Row {row_number}: {row}")
        
        if len(row) >= 11:
            try:
                game_date = row[4] if len(row) > 4 else ""  # Column E
                home_team = row[9] if len(row) > 9 else ""  # Column J
                away_team = row[8] if len(row) > 8 else ""  # Column I
                
                print(f"  -> Date: '{game_date}', Away: '{away_team}', Home: '{home_team}'")
                
            except Exception as e:
                print(f"  -> Error parsing row: {e}")
        print()

if __name__ == "__main__":
    check_rows_111_122()

