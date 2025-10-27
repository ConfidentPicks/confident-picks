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

def a1_to_col(a1):
    """Converts A1 notation to column index."""
    col_idx = 0
    for char in a1:
        col_idx = col_idx * 26 + (ord(char) - ord('A') + 1)
    return col_idx - 1

def main():
    print("🔍 SCANNING NEW SPREADSHEET STRUCTURE")
    print("=" * 80)
    
    service = get_sheets_service()
    sheet_name = "upcoming_games"
    
    # Get headers up to column BZ
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, 
        range=f"'{sheet_name}'!A1:BZ1"
    ).execute()
    headers = result.get('values', [[]])[0]
    
    print(f"\n📋 FULL COLUMN STRUCTURE ({len(headers)} columns):\n")
    
    # Define the columns I'm allowed to modify
    allowed_columns = {
        'AU': 'predicted_total',
        'AV': 'edge_vs_line',
        'AW': 'total_confidence',
        'AX': 'predicted_winner',
        'AZ': 'winner_confidence',
        'BA': 'Predicted_Cover_Home',
        'BC': 'home_cover_ confidence',
        'BD': 'Predicted_Cover_Away',
        'BF': 'away_cover_confidence',
        'BG': 'Predicted_Total',
        'BJ': 'total_confidence',
        'BK': 'Predicted_Home_Score',
        'BN': 'Predicted_Away_Score'
    }
    
    # Print all columns with markers for allowed ones
    for i, header in enumerate(headers):
        col_letter = col_to_a1(i)
        
        # Check if this is an allowed column
        if col_letter in allowed_columns:
            marker = "✅ EDITABLE"
            expected_name = allowed_columns[col_letter]
            match = "✓" if expected_name.lower() in header.lower() or header.lower() in expected_name.lower() else f"⚠️ Expected: {expected_name}"
        else:
            marker = "🔒 READ-ONLY"
            match = ""
        
        print(f"  {col_letter:4s} ({i:3d}): {header:40s} {marker:15s} {match}")
    
    # Get sample data for the editable columns
    print("\n" + "=" * 80)
    print("\n📊 SAMPLE DATA FROM EDITABLE COLUMNS (First 5 games):\n")
    
    # Get a few rows of data
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, 
        range=f"'{sheet_name}'!A1:BZ10"
    ).execute()
    data = result.get('values', [])
    
    if len(data) > 1:
        for row_idx in range(1, min(6, len(data))):
            row = data[row_idx]
            row_padded = row + [''] * (len(headers) - len(row))
            
            # Get game info
            away_team = row_padded[7] if len(row_padded) > 7 else "?"
            home_team = row_padded[9] if len(row_padded) > 9 else "?"
            
            print(f"Row {row_idx + 1}: {away_team} @ {home_team}")
            
            # Show values in each editable column
            for col_letter, expected_name in allowed_columns.items():
                col_idx = a1_to_col(col_letter)
                value = row_padded[col_idx] if len(row_padded) > col_idx else "(empty)"
                actual_header = headers[col_idx] if col_idx < len(headers) else "N/A"
                print(f"   {col_letter} ({actual_header}): '{value}'")
            print()
    
    # Create a mapping file for future reference
    print("\n" + "=" * 80)
    print("\n💾 SAVING COLUMN MAPPING...")
    
    mapping = {
        'allowed_columns': {},
        'readonly_columns': {}
    }
    
    for i, header in enumerate(headers):
        col_letter = col_to_a1(i)
        if col_letter in allowed_columns:
            mapping['allowed_columns'][col_letter] = {
                'index': i,
                'header': header,
                'expected': allowed_columns[col_letter]
            }
        else:
            mapping['readonly_columns'][col_letter] = {
                'index': i,
                'header': header
            }
    
    import json
    with open('column_mapping.json', 'w') as f:
        json.dump(mapping, f, indent=2)
    
    print("✅ Saved to column_mapping.json")
    
    print("\n" + "=" * 80)
    print("\n📝 SUMMARY:")
    print(f"   ✅ Found {len(headers)} total columns")
    print(f"   ✅ {len(allowed_columns)} columns are EDITABLE")
    print(f"   🔒 {len(headers) - len(allowed_columns)} columns are READ-ONLY")
    print(f"\n⚠️  I will ONLY modify the {len(allowed_columns)} editable columns from now on!")

if __name__ == "__main__":
    main()



