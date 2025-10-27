#!/usr/bin/env python3
"""Quick script to check NFL sheet column names"""

from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
NFL_SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU'

def get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('sheets', 'v4', credentials=creds)

def check_columns():
    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=NFL_SPREADSHEET_ID, 
        range='historical_game_results_2021_2024!A1:Z1'
    ).execute()
    
    headers = result.get('values', [[]])[0]
    
    print("=" * 60)
    print("NFL SHEET COLUMNS")
    print("=" * 60)
    print(f"\nTotal columns: {len(headers)}\n")
    
    for i, col in enumerate(headers, 1):
        print(f"{i:3d}. {col}")
    
    print("\n" + "=" * 60)
    print("LOOKING FOR DATE COLUMN...")
    print("=" * 60)
    
    date_cols = [col for col in headers if 'date' in col.lower()]
    if date_cols:
        print(f"\nFound date-related columns: {date_cols}")
    else:
        print("\n❌ No 'date' column found!")
        print("Possible alternatives:")
        for col in headers[:10]:  # Show first 10 columns
            print(f"  - {col}")

if __name__ == '__main__':
    check_columns()


