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

def check_confidence_columns():
    """Check what's in the confidence columns"""
    print("=" * 70)
    print("CHECKING CONFIDENCE COLUMNS")
    print("=" * 70)
    
    service = get_sheets_service()
    
    # Check columns: DB (Away_Cover_Confidence), BJ (home_score_confidence)
    range_name = "upcoming_games!DB1:BJ10"  # First 10 rows including headers
    
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = result.get('values', [])
    
    if not values:
        print("No data found!")
        return
    
    headers = values[0]
    print("Column headers:")
    print(f"DB (Column 56): {headers[55] if len(headers) > 55 else 'N/A'}")
    print(f"BJ (Column 62): {headers[61] if len(headers) > 61 else 'N/A'}")
    
    print("\nFirst 10 rows of data:")
    print("-" * 70)
    
    for i, row in enumerate(values[1:11]):
        db_val = row[55] if len(row) > 55 else "N/A"
        bj_val = row[61] if len(row) > 61 else "N/A"
        
        print(f"Row {i+2}:")
        print(f"  DB (Away_Cover_Confidence): '{db_val}'")
        print(f"  BJ (home_score_confidence): '{bj_val}'")
        print()

def check_all_confidence_columns():
    """Check all confidence-related columns"""
    print("\n" + "=" * 70)
    print("CHECKING ALL CONFIDENCE COLUMNS")
    print("=" * 70)
    
    service = get_sheets_service()
    
    # Get a larger range to find all confidence columns
    range_name = "upcoming_games!A1:BM5"  # First 5 rows, columns A to BM
    
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = result.get('values', [])
    
    if not values:
        print("No data found!")
        return
    
    headers = values[0]
    
    print("Looking for confidence-related columns:")
    print("-" * 70)
    
    # Find columns that might contain confidence data
    for i, header in enumerate(headers):
        if header and 'confidence' in header.lower():
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
    check_confidence_columns()
    check_all_confidence_columns()

