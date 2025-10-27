import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import numpy as np

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
    print("🔧 FIXING COLUMN AY (edge_vs_line)")
    print("=" * 70)
    
    service = get_sheets_service()
    sheet_name = "upcoming_games"
    
    # Get all data
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, 
        range=f"'{sheet_name}'!A1:AZ1000"
    ).execute()
    values = result.get('values', [])
    
    if not values:
        print("❌ Sheet is empty")
        return
    
    headers = values[0]
    data = values[1:]
    
    # Find column indices
    spread_line_idx = next((i for i, h in enumerate(headers) if 'spread_line' in h.lower()), None)
    predicted_spread_idx = next((i for i, h in enumerate(headers) if 'predicted_spread' in h.lower()), None)
    edge_idx = next((i for i, h in enumerate(headers) if 'edge_vs_line' in h.lower()), None)
    
    if spread_line_idx is None or predicted_spread_idx is None or edge_idx is None:
        print("❌ Could not find required columns")
        return
    
    print(f"✅ Found columns:")
    print(f"   spread_line: {col_to_a1(spread_line_idx)} (index {spread_line_idx})")
    print(f"   predicted_spread: {col_to_a1(predicted_spread_idx)} (index {predicted_spread_idx})")
    print(f"   edge_vs_line: {col_to_a1(edge_idx)} (index {edge_idx})")
    
    # Calculate edge_vs_line for all rows
    print(f"\n🔢 CALCULATING EDGE VS LINE FOR {len(data)} GAMES...")
    
    edge_values = []
    examples_shown = 0
    
    for i, row in enumerate(data):
        # Pad row to ensure we have enough columns
        row_padded = row + [''] * (max(spread_line_idx, predicted_spread_idx) + 1 - len(row))
        
        spread_line = row_padded[spread_line_idx] if len(row_padded) > spread_line_idx else ''
        predicted_spread = row_padded[predicted_spread_idx] if len(row_padded) > predicted_spread_idx else ''
        
        # Try to convert to numbers
        try:
            spread_line_num = float(spread_line) if spread_line and spread_line != '' else None
            predicted_spread_num = float(predicted_spread) if predicted_spread and predicted_spread != '' else None
            
            if spread_line_num is not None and predicted_spread_num is not None:
                edge = predicted_spread_num - spread_line_num
                edge_values.append([f"{edge:.1f}"])
                
                if examples_shown < 10:
                    away_team = row_padded[7] if len(row_padded) > 7 else "?"
                    home_team = row_padded[9] if len(row_padded) > 9 else "?"
                    print(f"   Row {i+2}: {away_team} @ {home_team}")
                    print(f"      Vegas: {spread_line_num:+.1f} | Predicted: {predicted_spread_num:+.1f} | Edge: {edge:+.1f}")
                    examples_shown += 1
            else:
                edge_values.append([''])
        except (ValueError, TypeError):
            edge_values.append([''])
    
    # Update the sheet
    print(f"\n📝 UPDATING COLUMN AY...")
    range_to_update = f"'{sheet_name}'!{col_to_a1(edge_idx)}2:{col_to_a1(edge_idx)}{len(data) + 1}"
    
    body = {
        'values': edge_values
    }
    
    try:
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_to_update,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        print(f"✅ UPDATED {len(edge_values)} ROWS!")
        
        # Count non-empty values
        non_empty = sum(1 for v in edge_values if v[0] != '')
        print(f"\n📊 SUMMARY:")
        print(f"   ✅ {non_empty} games with calculated edge")
        print(f"   ✅ {len(edge_values) - non_empty} games without enough data")
        print(f"\n💡 WHAT THE NUMBERS MEAN:")
        print(f"   Positive (+) = Your model predicts bigger margin than Vegas")
        print(f"   Negative (-) = Your model predicts smaller margin than Vegas")
        print(f"   Large values (±4+) = Strong disagreement with Vegas (betting opportunity!)")
        
    except Exception as e:
        print(f"❌ Error updating sheet: {e}")

if __name__ == "__main__":
    main()



