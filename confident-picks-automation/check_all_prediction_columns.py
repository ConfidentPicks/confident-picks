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
    print("🔍 CHECKING COLUMNS BA, BB, BC")
    print("=" * 70)
    
    service = get_sheets_service()
    sheet_name = "upcoming_games"
    
    # Get columns BA through BC
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, 
        range=f"'{sheet_name}'!BA1:BC20"
    ).execute()
    values = result.get('values', [])
    
    print(f"\n📊 COLUMNS BA, BB, BC - First 20 rows:")
    print(f"{'Row':<6} | {'BA (sharp_money)':<25} | {'BB (public_%)':<25} | {'BC (value_rating)':<25}")
    print("-" * 90)
    
    for i, row in enumerate(values):
        row_num = i + 1
        col_ba = row[0] if len(row) > 0 else "(empty)"
        col_bb = row[1] if len(row) > 1 else "(empty)"
        col_bc = row[2] if len(row) > 2 else "(empty)"
        
        print(f"{row_num:<6} | {col_ba:<25} | {col_bb:<25} | {col_bc:<25}")
    
    # Analysis
    if len(values) > 1:
        ba_values = [row[0] for row in values[1:] if len(row) > 0 and row[0]]
        bb_values = [row[1] for row in values[1:] if len(row) > 1 and row[1]]
        bc_values = [row[2] for row in values[1:] if len(row) > 2 and row[2]]
        
        print(f"\n📊 ANALYSIS:")
        print(f"   BA unique values: {set(ba_values) if ba_values else 'None'}")
        print(f"   BB unique values: {set(bb_values) if bb_values else 'None'}")
        print(f"   BC unique values: {set(bc_values) if bc_values else 'None'}")

if __name__ == "__main__":
    main()



