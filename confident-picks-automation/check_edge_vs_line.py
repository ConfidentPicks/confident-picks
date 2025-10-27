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
    print("🔍 CHECKING COLUMN AY (edge_vs_line)")
    print("=" * 70)
    
    service = get_sheets_service()
    
    # Get headers first
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, 
        range='upcoming_games!A1:AZ1'
    ).execute()
    headers = result.get('values', [[]])[0]
    
    print("\n📋 FINDING RELEVANT COLUMNS:")
    for i, header in enumerate(headers):
        if any(term in header.lower() for term in ['spread', 'edge', 'line', 'predicted']):
            print(f"  {col_to_a1(i)} ({i}): {header}")
    
    # Get column AY data (index 50)
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, 
        range='upcoming_games!AY1:AY15'
    ).execute()
    ay_values = result.get('values', [])
    
    print(f"\n📊 COLUMN AY (edge_vs_line) - First 15 rows:")
    for i, row in enumerate(ay_values):
        content = row[0] if row else "(empty)"
        print(f"  Row {i+1}: '{content}'")
    
    # Get the data for predicted_spread and spread_line columns
    # Based on previous scripts, these should be around columns X-AB
    result2 = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, 
        range='upcoming_games!A2:AZ10'
    ).execute()
    data = result2.get('values', [])
    
    if data and len(data) > 0:
        print(f"\n📊 SAMPLE DATA (Rows 2-10):")
        print(f"   Headers available: {len(headers)} columns")
        
        # Find spread_line and predicted_spread columns
        spread_line_idx = next((i for i, h in enumerate(headers) if 'spread_line' in h.lower()), None)
        predicted_spread_idx = next((i for i, h in enumerate(headers) if 'predicted_spread' in h.lower()), None)
        edge_idx = next((i for i, h in enumerate(headers) if 'edge_vs_line' in h.lower()), None)
        
        if spread_line_idx is not None:
            print(f"   spread_line found at column {col_to_a1(spread_line_idx)}")
        if predicted_spread_idx is not None:
            print(f"   predicted_spread found at column {col_to_a1(predicted_spread_idx)}")
        if edge_idx is not None:
            print(f"   edge_vs_line found at column {col_to_a1(edge_idx)}")
        
        print(f"\n   Sample rows:")
        for i, row in enumerate(data[:8]):
            row_num = i + 2
            spread_line = row[spread_line_idx] if spread_line_idx and len(row) > spread_line_idx else "N/A"
            predicted_spread = row[predicted_spread_idx] if predicted_spread_idx and len(row) > predicted_spread_idx else "N/A"
            edge = row[edge_idx] if edge_idx and len(row) > edge_idx else "N/A"
            
            away_team = row[7] if len(row) > 7 else "?"  # Column H
            home_team = row[9] if len(row) > 9 else "?"  # Column J
            
            print(f"   Row {row_num}: {away_team} @ {home_team}")
            print(f"      Vegas spread_line: {spread_line}")
            print(f"      Predicted spread: {predicted_spread}")
            print(f"      Edge vs line: {edge}")
            print(f"      Expected edge: {predicted_spread} - ({spread_line}) = ?")
            print()

if __name__ == "__main__":
    main()

