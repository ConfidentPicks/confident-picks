#!/usr/bin/env python3

"""
Check Current Column Structure and Data
======================================

This script checks the current column structure to build proper formulas
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
    
    print("🔍 CHECKING CURRENT COLUMN STRUCTURE AND DATA")
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
    
    # Print all headers with their column letters
    print(f"\n📋 ALL COLUMN HEADERS:")
    for i, header in enumerate(headers):
        col_letter = get_column_letter(i)
        print(f"  {col_letter}: {header}")
    
    # Check sample data in key columns
    print(f"\n📊 SAMPLE DATA IN KEY COLUMNS:")
    
    # Find key columns
    key_columns = {}
    for i, header in enumerate(headers):
        if 'home_team' in header.lower():
            key_columns['home_team'] = i
        elif 'away_team' in header.lower():
            key_columns['away_team'] = i
        elif 'home_score' in header.lower():
            key_columns['home_score'] = i
        elif 'away_score' in header.lower():
            key_columns['away_score'] = i
        elif 'predicted_winner' in header.lower():
            key_columns['predicted_winner'] = i
        elif 'spread_line' in header.lower():
            key_columns['spread_line'] = i
        elif 'predicted_spread' in header.lower():
            key_columns['predicted_spread'] = i
        elif 'total_line' in header.lower():
            key_columns['total_line'] = i
        elif 'predicted_total' in header.lower():
            key_columns['predicted_total'] = i
        elif 'winning_team' in header.lower():
            key_columns['winning_team'] = i
        elif 'predicted_team' in header.lower():
            key_columns['predicted_team'] = i
        elif 'spread_cover_away' in header.lower():
            key_columns['spread_cover_away'] = i
        elif 'predicted_cover_away' in header.lower():
            key_columns['predicted_cover_away'] = i
        elif 'actual_total' in header.lower():
            key_columns['actual_total'] = i
        elif 'predicted_home_score' in header.lower():
            key_columns['predicted_home_score'] = i
        elif 'predicted_away_score' in header.lower():
            key_columns['predicted_away_score'] = i
    
    print(f"Found key columns: {key_columns}")
    
    # Show sample data for first 5 rows
    for i in range(min(5, len(data_rows))):
        row = data_rows[i]
        row_num = i + 2
        print(f"\n  Row {row_num}:")
        
        for col_name, col_index in key_columns.items():
            col_letter = get_column_letter(col_index)
            value = row[col_index] if len(row) > col_index else "MISSING"
            print(f"    {col_letter} ({col_name}): '{value}'")
    
    # Check what formulas are currently in the analysis columns
    print(f"\n🔍 CHECKING CURRENT FORMULAS IN ANALYSIS COLUMNS:")
    
    analysis_columns = ['winning_team', 'predicted_team', 'spread_cover_away', 'predicted_cover_away', 'actual_total', 'predicted_total', 'predicted_home_score', 'predicted_away_score']
    
    for col_name in analysis_columns:
        if col_name in key_columns:
            col_index = key_columns[col_name]
            col_letter = get_column_letter(col_index)
            
            # Get the formula from row 2
            if len(data_rows) > 0 and len(data_rows[0]) > col_index:
                formula = data_rows[0][col_index] if len(data_rows[0]) > col_index else "MISSING"
                print(f"    {col_letter} ({col_name}): '{formula}'")
    
    print(f"\n📋 WHAT I NEED TO BUILD PROPER FORMULAS:")
    print(f"   1. Exact column letters for each data source")
    print(f"   2. Sample data to verify column contents")
    print(f"   3. Current formula errors to fix")
    print(f"   4. Confirmation of which columns contain what data")

if __name__ == "__main__":
    main()


