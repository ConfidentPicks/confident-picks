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
    print("🔍 CHECKING PUBLIC_PERCENTAGE COLUMN")
    print("=" * 70)
    
    service = get_sheets_service()
    sheet_name = "upcoming_games"
    
    # Get column BB data
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, 
        range=f"'{sheet_name}'!BB1:BB30"
    ).execute()
    values = result.get('values', [])
    
    print(f"\n📊 COLUMN BB (public_percentage) - First 30 rows:")
    for i, row in enumerate(values):
        content = row[0] if row else "(empty)"
        print(f"  Row {i+1}: '{content}'")
    
    # Check if all values are the same
    if len(values) > 1:
        data_values = [row[0] for row in values[1:] if row and row[0]]
        unique_values = set(data_values)
        
        print(f"\n📊 ANALYSIS:")
        print(f"   Total data rows: {len(data_values)}")
        print(f"   Unique values: {unique_values}")
        
        if len(unique_values) <= 3:
            print(f"\n❌ PROBLEM: Only {len(unique_values)} unique values - this is DUMMY DATA!")
            print(f"   Real public percentages would range from 0-100%")
        else:
            print(f"\n✅ Multiple unique values found - might be real data")

if __name__ == "__main__":
    main()



