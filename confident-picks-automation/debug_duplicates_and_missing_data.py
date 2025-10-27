#!/usr/bin/env python3

"""
Debug Duplicate Columns and Missing Game Results
===============================================

This script checks for duplicate columns and missing game results from nflreadpy
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
    
    print("🔍 DEBUGGING DUPLICATE COLUMNS AND MISSING GAME RESULTS")
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
    
    # Check for duplicate columns
    print("\n🔍 CHECKING FOR DUPLICATE COLUMNS:")
    column_counts = {}
    for i, header in enumerate(headers):
        if header in column_counts:
            column_counts[header].append(i)
        else:
            column_counts[header] = [i]
    
    duplicates_found = False
    for header, indices in column_counts.items():
        if len(indices) > 1:
            duplicates_found = True
            col_letters = [get_column_letter(idx) for idx in indices]
            print(f"  ❌ DUPLICATE: '{header}' found at columns {col_letters}")
    
    if not duplicates_found:
        print("  ✅ No duplicate columns found")
    
    # Print all headers to see what we have
    print(f"\n📋 ALL COLUMN HEADERS:")
    for i, header in enumerate(headers):
        col_letter = get_column_letter(i)
        print(f"  {col_letter}: {header}")
    
    # Check for missing game results
    print(f"\n🔍 CHECKING FOR MISSING GAME RESULTS:")
    
    # Find key columns
    col_indices = {}
    for i, header in enumerate(headers):
        if 'home_score' in header.lower():
            col_indices['home_score'] = i
        elif 'away_score' in header.lower():
            col_indices['away_score'] = i
        elif 'result' in header.lower():
            col_indices['result'] = i
        elif 'home_team' in header.lower():
            col_indices['home_team'] = i
        elif 'away_team' in header.lower():
            col_indices['away_team'] = i
        elif 'gameday' in header.lower():
            col_indices['gameday'] = i
    
    print(f"Found key columns: {col_indices}")
    
    # Check first 20 rows for missing data
    print(f"\n📊 CHECKING FIRST 20 ROWS FOR MISSING DATA:")
    missing_scores = 0
    missing_results = 0
    completed_games = 0
    
    for i in range(min(20, len(data_rows))):
        row = data_rows[i]
        row_num = i + 2
        
        home_team = row[col_indices['home_team']] if len(row) > col_indices['home_team'] else ""
        away_team = row[col_indices['away_team']] if len(row) > col_indices['away_team'] else ""
        home_score = row[col_indices['home_score']] if len(row) > col_indices['home_score'] else ""
        away_score = row[col_indices['away_score']] if len(row) > col_indices['away_score'] else ""
        result = row[col_indices['result']] if len(row) > col_indices['result'] else ""
        gameday = row[col_indices['gameday']] if len(row) > col_indices['gameday'] else ""
        
        print(f"  Row {row_num}: {away_team} @ {home_team}")
        print(f"    Gameday: {gameday}")
        print(f"    Scores: {away_score}-{home_score}")
        print(f"    Result: {result}")
        
        if not home_score or not away_score or home_score.strip() == "" or away_score.strip() == "":
            missing_scores += 1
            print(f"    ❌ MISSING SCORES")
        else:
            completed_games += 1
            print(f"    ✅ HAS SCORES")
        
        if not result or result.strip() == "":
            missing_results += 1
            print(f"    ❌ MISSING RESULT")
        else:
            print(f"    ✅ HAS RESULT")
        print()
    
    print(f"📊 SUMMARY:")
    print(f"   - Completed games (with scores): {completed_games}/20")
    print(f"   - Missing scores: {missing_scores}/20")
    print(f"   - Missing results: {missing_results}/20")
    
    # Check if we need to run nflreadpy data collection
    if missing_scores > 0 or missing_results > 0:
        print(f"\n⚠️ ISSUES FOUND:")
        print(f"   - Missing game scores/results from nflreadpy")
        print(f"   - Need to run data collection to get actual game results")
        print(f"   - Current data appears to be incomplete")
    else:
        print(f"\n✅ DATA LOOKS COMPLETE:")
        print(f"   - All games have scores and results")
        print(f"   - nflreadpy data appears to be properly loaded")

if __name__ == "__main__":
    main()


