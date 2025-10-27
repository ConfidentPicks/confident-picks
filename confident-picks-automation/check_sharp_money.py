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

def col_to_a1(col_idx):
    """Converts a 0-indexed column number to an A1-style column letter."""
    letter = ''
    while col_idx >= 0:
        letter = chr(col_idx % 26 + ord('A')) + letter
        col_idx = col_idx // 26 - 1
    return letter

def main():
    print("🔍 FINDING SHARP_MONEY COLUMN")
    print("=" * 70)
    
    service = get_sheets_service()
    sheet_name = "upcoming_games"
    
    # Get headers
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, 
        range=f"'{sheet_name}'!A1:BZ1"
    ).execute()
    headers = result.get('values', [[]])[0]
    
    print(f"\n📋 ALL COLUMNS ({len(headers)} total):")
    for i, header in enumerate(headers):
        print(f"  {col_to_a1(i)}: {header}")
    
    # Find sharp_money column
    sharp_money_idx = None
    for i, header in enumerate(headers):
        if 'sharp' in header.lower():
            sharp_money_idx = i
            print(f"\n🎯 FOUND: sharp_money at column {col_to_a1(i)} (index {i})")
            
            # Get sample data
            result = service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID, 
                range=f"'{sheet_name}'!{col_to_a1(i)}1:{col_to_a1(i)}20"
            ).execute()
            values = result.get('values', [])
            
            print(f"\n📊 SAMPLE DATA (first 20 rows):")
            for j, row in enumerate(values):
                content = row[0] if row else "(empty)"
                print(f"  Row {j+1}: '{content}'")
            break
    
    if sharp_money_idx is None:
        print("\n✅ No sharp_money column found - already removed!")
    else:
        print(f"\n❌ sharp_money column still exists at {col_to_a1(sharp_money_idx)}")
        print(f"\n💡 This column contains dummy values (0.1, 0.05) - not real sharp money data")

if __name__ == "__main__":
    main()



