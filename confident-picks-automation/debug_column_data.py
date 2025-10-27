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

def debug_column_data():
    """Debug what's actually in the columns"""
    print("=" * 70)
    print("DEBUGGING COLUMN DATA")
    print("=" * 70)
    
    service = get_sheets_service()
    
    # Get the correct columns: AA, AY, AZ
    range_name = "upcoming_games!AA1:AZ10"  # First 10 rows including headers
    
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = result.get('values', [])
    
    if not values:
        print("No data found!")
        return
    
    headers = values[0]
    print("Headers:")
    print(f"AA (Column 27): {headers[26] if len(headers) > 26 else 'N/A'}")
    print(f"AY (Column 51): {headers[50] if len(headers) > 50 else 'N/A'}")
    print(f"AZ (Column 52): {headers[51] if len(headers) > 51 else 'N/A'}")
    
    print("\nFirst 10 rows of data:")
    print("-" * 70)
    
    for i, row in enumerate(values[1:11]):
        aa_val = row[26] if len(row) > 26 else "N/A"
        ay_val = row[50] if len(row) > 50 else "N/A"
        az_val = row[51] if len(row) > 51 else "N/A"
        
        print(f"Row {i+2}:")
        print(f"  AA (spread_line): '{aa_val}' (type: {type(aa_val)})")
        print(f"  AY (predicted_home_cover): '{ay_val}' (type: {type(ay_val)})")
        print(f"  AZ (Actual_Cover_Home): '{az_val}' (type: {type(az_val)})")
        print()

def check_actual_vs_predicted_logic():
    """Check the logic for actual vs predicted"""
    print("\n" + "=" * 70)
    print("CHECKING ACTUAL VS PREDICTED LOGIC")
    print("=" * 70)
    
    service = get_sheets_service()
    
    # Get columns: AA (spread_line), AY (predicted_home_cover), AZ (Actual_Cover_Home), K (home_score), I (away_score)
    range_name = "upcoming_games!I2:K110"  # away_score, home_score
    
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = result.get('values', [])
    
    if not values:
        print("No data found!")
        return
    
    print("Checking if we can calculate actual home cover from scores:")
    print("-" * 70)
    
    for i, row in enumerate(values[:10]):
        if len(row) >= 2:
            try:
                away_score = float(row[0])  # I column (away_score)
                home_score = float(row[1])  # K column (home_score)
                
                print(f"Row {i+2}: Away={away_score}, Home={home_score}")
                
            except (ValueError, TypeError) as e:
                print(f"Row {i+2}: Error processing scores - {e}")

if __name__ == "__main__":
    debug_column_data()
    check_actual_vs_predicted_logic()

