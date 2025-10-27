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

def find_correct_columns():
    """Find the correct columns for home spread predictions"""
    print("=" * 70)
    print("FINDING CORRECT COLUMNS FOR HOME SPREAD")
    print("=" * 70)
    
    service = get_sheets_service()
    
    # Get a larger range to find the columns
    range_name = "upcoming_games!A1:BM5"  # First 5 rows, columns A to BM
    
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = result.get('values', [])
    
    if not values:
        print("No data found!")
        return
    
    headers = values[0]
    
    print("Looking for home spread related columns:")
    print("-" * 70)
    
    # Find columns that might contain home spread data
    for i, header in enumerate(headers):
        if header and ('home' in header.lower() or 'cover' in header.lower() or 'spread' in header.lower()):
            col_letter = chr(65 + i) if i < 26 else chr(65 + i // 26 - 1) + chr(65 + i % 26)
            print(f"{col_letter} (Column {i+1}): {header}")
            
            # Show sample data
            if len(values) > 1:
                sample_data = []
                for j in range(1, min(6, len(values))):
                    if i < len(values[j]):
                        sample_data.append(values[j][i])
                    else:
                        sample_data.append("N/A")
                print(f"  Sample data: {sample_data}")
                print()

def check_spread_line_column():
    """Find the spread line column"""
    print("\n" + "=" * 70)
    print("FINDING SPREAD LINE COLUMN")
    print("=" * 70)
    
    service = get_sheets_service()
    
    # Get a larger range to find the columns
    range_name = "upcoming_games!A1:BM5"  # First 5 rows, columns A to BM
    
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = result.get('values', [])
    
    if not values:
        print("No data found!")
        return
    
    headers = values[0]
    
    print("Looking for spread line column:")
    print("-" * 70)
    
    # Find columns that might contain spread line data
    for i, header in enumerate(headers):
        if header and ('spread' in header.lower() and 'line' in header.lower()):
            col_letter = chr(65 + i) if i < 26 else chr(65 + i // 26 - 1) + chr(65 + i % 26)
            print(f"{col_letter} (Column {i+1}): {header}")
            
            # Show sample data
            if len(values) > 1:
                sample_data = []
                for j in range(1, min(6, len(values))):
                    if i < len(values[j]):
                        sample_data.append(values[j][i])
                    else:
                        sample_data.append("N/A")
                print(f"  Sample data: {sample_data}")
                print()

if __name__ == "__main__":
    find_correct_columns()
    check_spread_line_column()

