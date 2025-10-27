#!/usr/bin/env python3
"""Check what's in the NHL upcoming_games tab"""

from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
NHL_SHEET_ID = '1Hel-NsCxmk07nM0AH4VkJFB9hSK23X7XOxtA4wyRNRo'

def get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build('sheets', 'v4', credentials=creds)

service = get_sheets_service()

# Check what tabs exist
sheet_metadata = service.spreadsheets().get(spreadsheetId=NHL_SHEET_ID).execute()
sheets = sheet_metadata.get('sheets', [])

print("NHL SHEET TABS:")
for sheet in sheets:
    print(f"  - {sheet['properties']['title']}")

# Try to read upcoming_games
print("\nTrying to read 'upcoming_games' tab...")
try:
    result = service.spreadsheets().values().get(
        spreadsheetId=NHL_SHEET_ID,
        range='upcoming_games!A1:N1'
    ).execute()
    
    values = result.get('values', [])
    if values:
        print("\nColumn headers in 'upcoming_games':")
        for i, col in enumerate(values[0]):
            print(f"  Column {chr(65+i)}: {col}")
    
    # Check how many rows
    result2 = service.spreadsheets().values().get(
        spreadsheetId=NHL_SHEET_ID,
        range='upcoming_games!A:A'
    ).execute()
    
    values2 = result2.get('values', [])
    print(f"\nTotal rows in upcoming_games: {len(values2)}")
    
    # Sample data
    result3 = service.spreadsheets().values().get(
        spreadsheetId=NHL_SHEET_ID,
        range='upcoming_games!A2:N2'
    ).execute()
    
    values3 = result3.get('values', [])
    if values3:
        print("\nSample data (row 2):")
        for i, val in enumerate(values3[0] if len(values3) > 0 else []):
            if i < len(values[0]):
                print(f"  {values[0][i]}: {val}")
    
except Exception as e:
    print(f"Error: {e}")

