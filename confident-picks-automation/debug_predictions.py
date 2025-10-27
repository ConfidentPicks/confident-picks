#!/usr/bin/env python3

"""
Debug Why Predictions Aren't Showing
===================================

This script checks exactly what's in the sheet and why predictions aren't visible
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

def get_column_letter(col_index):
    """Convert column index to Google Sheets column letter (supports beyond Z)"""
    result = ""
    while col_index >= 0:
        result = chr(65 + (col_index % 26)) + result
        col_index = col_index // 26 - 1
    return result

def main():
    # Configuration
    credentials_path = "C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json"
    spreadsheet_id = "1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU"
    
    # Setup connection
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    
    service = build('sheets', 'v4', credentials=credentials)
    
    print("🔍 DEBUGGING WHY PREDICTIONS AREN'T SHOWING")
    print("=" * 60)
    
    # Get current data
    print("📊 Loading current sheet data...")
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="upcoming_games!A:ZZ"
    ).execute()
    
    values = result.get('values', [])
    if not values or len(values) < 2:
        print("❌ No data found")
        return
    
    headers = values[0]
    data_rows = values[1:]
    
    print(f"✅ Found {len(data_rows)} rows with {len(headers)} columns")
    print(f"✅ Total games: {len(data_rows)}")
    
    # Print all headers to see what we have
    print(f"\n📋 ALL COLUMN HEADERS:")
    for i, header in enumerate(headers):
        col_letter = get_column_letter(i)
        print(f"  {col_letter}: {header}")
    
    # Check if prediction columns exist
    prediction_columns = []
    for i, header in enumerate(headers):
        if any(keyword in header.lower() for keyword in ['predicted', 'confidence', 'betting', 'value', 'probability']):
            prediction_columns.append((i, header))
    
    print(f"\n🎯 PREDICTION COLUMNS FOUND:")
    for col_idx, header in prediction_columns:
        col_letter = get_column_letter(col_idx)
        print(f"  {col_letter}: {header}")
    
    # Check sample data in prediction columns
    print(f"\n📊 SAMPLE DATA IN PREDICTION COLUMNS:")
    for col_idx, header in prediction_columns[:5]:  # Check first 5 prediction columns
        col_letter = get_column_letter(col_idx)
        print(f"\n{col_letter} ({header}):")
        for i in range(min(10, len(data_rows))):  # Check first 10 rows
            value = data_rows[i][col_idx] if len(data_rows[i]) > col_idx else "MISSING"
            home_team = data_rows[i][10] if len(data_rows[i]) > 10 else "MISSING"
            away_team = data_rows[i][7] if len(data_rows[i]) > 7 else "MISSING"
            print(f"  Row {i+2}: {away_team} @ {home_team} = '{value}'")
    
    # Check if there are any non-empty prediction values
    print(f"\n🔍 CHECKING FOR ANY NON-EMPTY PREDICTIONS:")
    has_predictions = False
    for col_idx, header in prediction_columns:
        for i, row in enumerate(data_rows):
            if len(row) > col_idx and row[col_idx] and row[col_idx].strip():
                has_predictions = True
                col_letter = get_column_letter(col_idx)
                home_team = row[10] if len(row) > 10 else "MISSING"
                away_team = row[7] if len(row) > 7 else "MISSING"
                print(f"  Found prediction in {col_letter} ({header}) Row {i+2}: {away_team} @ {home_team} = '{row[col_idx]}'")
                break
        if has_predictions:
            break
    
    if not has_predictions:
        print("  ❌ NO PREDICTIONS FOUND - All prediction columns are empty!")
    
    # Check specific rows that user mentioned (110+)
    print(f"\n🔍 CHECKING ROWS 110+ SPECIFICALLY:")
    for i in range(109, min(115, len(data_rows))):  # Check rows 110-115
        row = data_rows[i]
        home_team = row[10] if len(row) > 10 else "MISSING"
        away_team = row[7] if len(row) > 7 else "MISSING"
        print(f"  Row {i+2}: {away_team} @ {home_team}")
        
        # Check prediction columns for this row
        for col_idx, header in prediction_columns[:3]:  # Check first 3 prediction columns
            col_letter = get_column_letter(col_idx)
            value = row[col_idx] if len(row) > col_idx else "MISSING"
            print(f"    {col_letter} ({header}): '{value}'")

if __name__ == "__main__":
    main()



