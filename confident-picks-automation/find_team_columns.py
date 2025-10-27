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

def find_team_columns():
    """Find which columns contain team names"""
    print("=" * 80)
    print("FINDING TEAM COLUMNS")
    print("=" * 80)
    
    service = get_sheets_service()
    
    # Check a wider range to find team names
    range_name = "upcoming_games!A111:Z122"  # Check columns A-Z
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    data = result.get('values', [])
    
    print("Checking columns A-Z for rows 111-122:")
    print("-" * 80)
    
    # Print headers first
    headers = []
    for col in range(26):  # A-Z
        col_letter = chr(65 + col)
        headers.append(col_letter)
    
    print("Columns:", " ".join(headers))
    print("-" * 80)
    
    # Print first few rows to see the data
    for i, row in enumerate(data[:3]):  # First 3 rows
        row_data = []
        for col in range(26):
            if col < len(row):
                row_data.append(row[col] if row[col] else "")
            else:
                row_data.append("")
        print(f"Row {111+i}: {' | '.join(row_data)}")
    
    print("\n" + "="*80)
    print("LOOKING FOR SPECIFIC TEAMS")
    print("="*80)
    
    # Look for specific teams we know should be there
    target_teams = ['BUF', 'CAR', 'DAL', 'DEN', 'GB', 'PIT', 'TB', 'NO', 'CLE', 'NE']
    
    for i, row in enumerate(data):
        row_num = 111 + i
        print(f"\nRow {row_num}:")
        for col_idx, cell in enumerate(row):
            if cell in target_teams:
                col_letter = chr(65 + col_idx)
                print(f"  Found {cell} in column {col_letter}")

if __name__ == "__main__":
    find_team_columns()

