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
    """Convert 0-indexed column number to A1-style column letter"""
    letter = ''
    while col_idx >= 0:
        letter = chr(col_idx % 26 + ord('A')) + letter
        col_idx = col_idx // 26 - 1
    return letter

def load_sheet_data(spreadsheet_id, sheet_name):
    """Load data from Google Sheets"""
    service = get_sheets_service()
    range_name = f"'{sheet_name}'!A:CZ"
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])

    if not values:
        return pd.DataFrame()

    headers = values[0]
    data = values[1:]

    max_cols = len(headers)
    for row in data:
        if len(row) > max_cols:
            max_cols = len(row)
    
    headers_extended = headers + [f'col_{i}' for i in range(len(headers), max_cols)]
    
    data_aligned = []
    for row in data:
        aligned_row = row + [None] * (max_cols - len(row))
        data_aligned.append(aligned_row)

    df = pd.DataFrame(data_aligned, columns=headers_extended)
    return df

def main():
    print("🔍 CHECKING FPI AND PREDICTION COLUMNS")
    print("=" * 60)
    
    # Load upcoming_games data
    print("📊 Loading upcoming_games data...")
    df = load_sheet_data(SPREADSHEET_ID, 'upcoming_games')
    
    if df.empty:
        print("❌ No data available!")
        return False
    
    print(f"✅ Loaded {len(df)} games with {len(df.columns)} columns")
    
    # Show ALL columns with indices
    print(f"\n📋 ALL COLUMNS:")
    for i, col in enumerate(df.columns):
        print(f"   {col_to_a1(i)} ({i}): {col}")
    
    # Check specific columns
    print(f"\n🔍 CHECKING PREDICTION COLUMNS:")
    
    # Check AX (predicted_winner)
    ax_idx = 49  # AX
    if ax_idx < len(df.columns):
        print(f"\n   Column AX ({ax_idx}): {df.columns[ax_idx]}")
        print(f"   Sample values:")
        for i in range(min(5, len(df))):
            print(f"      Row {i+2}: '{df.iloc[i, ax_idx]}'")
    
    # Check AZ (winner_confidence)
    az_idx = 51  # AZ
    if az_idx < len(df.columns):
        print(f"\n   Column AZ ({az_idx}): {df.columns[az_idx]}")
        print(f"   Sample values:")
        for i in range(min(5, len(df))):
            print(f"      Row {i+2}: '{df.iloc[i, az_idx]}'")
    
    # Check BA (winner_confidence_fpi)
    ba_idx = 52  # BA
    if ba_idx < len(df.columns):
        print(f"\n   Column BA ({ba_idx}): {df.columns[ba_idx]}")
        print(f"   Sample values:")
        for i in range(min(5, len(df))):
            print(f"      Row {i+2}: '{df.iloc[i, ba_idx]}'")
    
    # Check for ESPN/FPI columns
    print(f"\n🔍 CHECKING ESPN/FPI DATA:")
    espn_cols = [col for col in df.columns if 'espn' in str(col).lower() or 'fpi' in str(col).lower()]
    
    for col_name in espn_cols:
        col_idx = df.columns.get_loc(col_name)
        print(f"\n   Column {col_to_a1(col_idx)} ({col_idx}): {col_name}")
        print(f"   Sample values:")
        for i in range(min(5, len(df))):
            val = df.iloc[i, col_idx]
            if pd.notna(val) and val != '':
                print(f"      Row {i+2}: '{val}'")
    
    # Check teams
    print(f"\n🔍 CHECKING TEAM COLUMNS:")
    print(f"\n   Away Team (H):")
    for i in range(min(5, len(df))):
        print(f"      Row {i+2}: '{df.iloc[i]['away_team']}'")
    
    print(f"\n   Home Team (J):")
    for i in range(min(5, len(df))):
        print(f"      Row {i+2}: '{df.iloc[i]['home_team']}'")

if __name__ == "__main__":
    main()


