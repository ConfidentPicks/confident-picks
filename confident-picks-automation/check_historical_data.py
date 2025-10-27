import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'
SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU'
HISTORICAL_SPREADSHEET_ID = '1-zXtCyhmjk40R_1mEW_v59j26Q0OpM1zNY6NL1YrTyA'

def get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

def check_historical_spreadsheet():
    """Check what sheets are available in the historical spreadsheet"""
    print("🔍 Checking historical spreadsheet...")
    
    service = get_sheets_service()
    
    try:
        # Get sheet metadata
        result = service.spreadsheets().get(spreadsheetId=HISTORICAL_SPREADSHEET_ID).execute()
        sheets = result.get('sheets', [])
        
        print(f"✅ Found {len(sheets)} sheets in historical spreadsheet:")
        for sheet in sheets:
            sheet_name = sheet['properties']['title']
            print(f"   - {sheet_name}")
        
        return [sheet['properties']['title'] for sheet in sheets]
        
    except Exception as e:
        print(f"❌ Could not access historical spreadsheet: {e}")
        return []

def check_current_spreadsheet():
    """Check what sheets are available in the current spreadsheet"""
    print("🔍 Checking current spreadsheet...")
    
    service = get_sheets_service()
    
    try:
        # Get sheet metadata
        result = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = result.get('sheets', [])
        
        print(f"✅ Found {len(sheets)} sheets in current spreadsheet:")
        for sheet in sheets:
            sheet_name = sheet['properties']['title']
            print(f"   - {sheet_name}")
        
        return [sheet['properties']['title'] for sheet in sheets]
        
    except Exception as e:
        print(f"❌ Could not access current spreadsheet: {e}")
        return []

def main():
    print("🔍 CHECKING AVAILABLE DATA SOURCES")
    print("=" * 60)
    
    # Check historical spreadsheet
    historical_sheets = check_historical_spreadsheet()
    
    print()
    
    # Check current spreadsheet
    current_sheets = check_current_spreadsheet()
    
    print("\n📊 SUMMARY:")
    print(f"   Historical sheets: {len(historical_sheets)}")
    print(f"   Current sheets: {len(current_sheets)}")
    
    # Look for any sheets that might contain historical data
    all_sheets = historical_sheets + current_sheets
    historical_candidates = [sheet for sheet in all_sheets if any(year in sheet.lower() for year in ['2021', '2022', '2023', '2024', 'historical'])]
    
    print(f"\n🎯 Potential historical data sources:")
    for sheet in historical_candidates:
        print(f"   - {sheet}")

if __name__ == "__main__":
    main()


