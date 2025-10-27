import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'
SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU'

def get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

def main():
    print("🔍 INSPECTING ESPN FPI RANGE (BY5:CI113)")
    print("=" * 60)
    
    service = get_sheets_service()
    
    # Load the full FPI range
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range='upcoming_games!BY1:CI120'
    ).execute()
    
    values = result.get('values', [])
    
    print(f"✅ Loaded {len(values)} rows from BY1:CI120")
    
    # Show first 20 rows to understand structure
    print(f"\n📋 FIRST 20 ROWS OF FPI DATA:")
    for i, row in enumerate(values[:20], start=1):
        print(f"   Row {i}: {row}")
    
    print(f"\n📋 ROWS AROUND ROW 5 (where FPI data starts):")
    for i in range(max(0, 4-2), min(len(values), 4+10)):
        print(f"   Row {i+1}: {values[i]}")
    
    # Check if there are multiple tables
    print(f"\n📋 CHECKING FOR DIFFERENT SECTIONS:")
    for i, row in enumerate(values, start=1):
        if row and any('team' in str(cell).lower() or 'game' in str(cell).lower() or 'matchup' in str(cell).lower() for cell in row):
            print(f"   Row {i}: {row[:5]}...")  # Show first 5 cells

if __name__ == "__main__":
    main()


