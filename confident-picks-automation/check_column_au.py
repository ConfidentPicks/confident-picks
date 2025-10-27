import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = '../confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'
SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU'

def get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

def main():
    print("🔍 CHECKING COLUMN AU (actual_winner)")
    print("=" * 60)
    
    service = get_sheets_service()
    
    # Get column AU data
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, 
        range='upcoming_games!AU1:AU15'
    ).execute()
    values = result.get('values', [])
    
    print("\n📊 COLUMN AU - First 15 rows:")
    for i, row in enumerate(values):
        content = row[0] if row else "(empty)"
        print(f"  Row {i+1}: '{content}'")
    
    # Get corresponding data from other columns
    result2 = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, 
        range='upcoming_games!H2:K15'
    ).execute()
    values2 = result2.get('values', [])
    
    print("\n📊 CORRESPONDING TEAM & SCORE DATA (Rows 2-15):")
    for i, row in enumerate(values2):
        if len(row) >= 4:
            away_team = row[0] if len(row) > 0 else ""
            away_score = row[1] if len(row) > 1 else ""
            home_team = row[2] if len(row) > 2 else ""
            home_score = row[3] if len(row) > 3 else ""
            print(f"  Row {i+2}: {away_team} ({away_score}) @ {home_team} ({home_score})")

if __name__ == "__main__":
    main()

