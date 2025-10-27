#!/usr/bin/env python3

"""
Check Live Picks Sheet Columns
=============================

This script checks the column names in the live_picks_sheets tab
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
    
    # Get headers from live_picks_sheets
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="live_picks_sheets!1:1"
    ).execute()
    
    headers = result.get('values', [[]])[0]
    
    print("Live Picks Sheets Headers:")
    print("=" * 50)
    for i, header in enumerate(headers):
        print(f"{chr(65+i):>3}: {header}")
    
    # Look for prediction-related columns
    print("\nPrediction-related columns:")
    print("=" * 30)
    for i, header in enumerate(headers):
        if any(word in header.lower() for word in ['predicted', 'confidence', 'win', 'betting', 'recommendation']):
            print(f"{chr(65+i):>3}: {header}")

if __name__ == "__main__":
    main()



