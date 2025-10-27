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

def check_actual_column_contents():
    """Check what's actually in the columns"""
    print("=" * 70)
    print("CHECKING ACTUAL COLUMN CONTENTS")
    print("=" * 70)
    
    service = get_sheets_service()
    
    # Check columns AA, AY, AZ (spread_line, predicted_home_cover, Actual_Cover_Home)
    range_name = "upcoming_games!AA1:AZ10"  # First 10 rows including headers
    
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = result.get('values', [])
    
    if not values:
        print("No data found!")
        return
    
    print("Column headers and first 10 rows:")
    print("-" * 70)
    
    headers = values[0]
    print(f"AA (Column 27): {headers[26] if len(headers) > 26 else 'N/A'}")
    print(f"AY (Column 51): {headers[50] if len(headers) > 50 else 'N/A'}")
    print(f"AZ (Column 52): {headers[51] if len(headers) > 51 else 'N/A'}")
    
    print("\nFirst 10 rows of data:")
    for i, row in enumerate(values[1:11]):
        aa_val = row[26] if len(row) > 26 else "N/A"
        ay_val = row[50] if len(row) > 50 else "N/A"
        az_val = row[51] if len(row) > 51 else "N/A"
        print(f"Row {i+2}: AA={aa_val}, AY={ay_val}, AZ={az_val}")

def check_all_columns_around_ay():
    """Check all columns around AY to see what's actually there"""
    print("\n" + "=" * 70)
    print("CHECKING ALL COLUMNS AROUND AY")
    print("=" * 70)
    
    service = get_sheets_service()
    
    # Check columns AX to BB (columns 49-54)
    range_name = "upcoming_games!AX1:BB10"  # First 10 rows including headers
    
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = result.get('values', [])
    
    if not values:
        print("No data found!")
        return
    
    headers = values[0]
    print("Column headers around AY:")
    print("-" * 70)
    
    for i in range(49, min(55, len(headers))):
        col_letter = chr(65 + i) if i < 26 else chr(65 + i // 26 - 1) + chr(65 + i % 26)
        print(f"{col_letter} (Column {i+1}): {headers[i] if i < len(headers) else 'N/A'}")
    
    print("\nFirst 5 rows of data:")
    for i, row in enumerate(values[1:6]):
        print(f"Row {i+2}:")
        for j in range(49, min(55, len(row))):
            col_letter = chr(65 + j) if j < 26 else chr(65 + j // 26 - 1) + chr(65 + j % 26)
            val = row[j] if j < len(row) else "N/A"
            print(f"  {col_letter}={val}")

if __name__ == "__main__":
    check_actual_column_contents()
    check_all_columns_around_ay()

