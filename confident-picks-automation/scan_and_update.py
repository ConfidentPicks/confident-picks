#!/usr/bin/env python3

"""
Scan Current Sheet and Update Scripts
===================================

This script scans the current sheet to see all changes and updates scripts accordingly
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
    
    print("🔍 SCANNING CURRENT SHEET AND UPDATING SCRIPTS")
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
    print(f"\n📋 CURRENT COLUMN STRUCTURE:")
    for i, header in enumerate(headers):
        col_letter = get_column_letter(i)
        print(f"  {col_letter}: {header}")
    
    # Find key columns for scripts
    print(f"\n🔍 IDENTIFYING KEY COLUMNS FOR SCRIPTS:")
    
    key_columns = {}
    for i, header in enumerate(headers):
        col_letter = get_column_letter(i)
        
        # Game data columns
        if 'game_id' in header.lower():
            key_columns['game_id'] = {'index': i, 'letter': col_letter, 'name': header}
        elif 'home_team' in header.lower():
            key_columns['home_team'] = {'index': i, 'letter': col_letter, 'name': header}
        elif 'away_team' in header.lower():
            key_columns['away_team'] = {'index': i, 'letter': col_letter, 'name': header}
        elif 'home_score' in header.lower():
            key_columns['home_score'] = {'index': i, 'letter': col_letter, 'name': header}
        elif 'away_score' in header.lower():
            key_columns['away_score'] = {'index': i, 'letter': col_letter, 'name': header}
        elif 'spread_line' in header.lower():
            key_columns['spread_line'] = {'index': i, 'letter': col_letter, 'name': header}
        elif 'total_line' in header.lower():
            key_columns['total_line'] = {'index': i, 'letter': col_letter, 'name': header}
        elif 'result' in header.lower():
            key_columns['result'] = {'index': i, 'letter': col_letter, 'name': header}
        
        # Prediction columns
        elif 'predicted_winner' in header.lower():
            key_columns['predicted_winner'] = {'index': i, 'letter': col_letter, 'name': header}
        elif 'confidence_score' in header.lower():
            key_columns['confidence_score'] = {'index': i, 'letter': col_letter, 'name': header}
        elif 'predicted_spread' in header.lower():
            key_columns['predicted_spread'] = {'index': i, 'letter': col_letter, 'name': header}
        elif 'predicted_total' in header.lower():
            key_columns['predicted_total'] = {'index': i, 'letter': col_letter, 'name': header}
        elif 'prediction_result' in header.lower():
            key_columns['prediction_result'] = {'index': i, 'letter': col_letter, 'name': header}
        elif 'prediction_outcome' in header.lower() or 'outcome' in header.lower():
            key_columns['prediction_outcome'] = {'index': i, 'letter': col_letter, 'name': header}
        
        # Analysis columns
        elif 'winning_team' in header.lower():
            key_columns['winning_team'] = {'index': i, 'letter': col_letter, 'name': header}
        elif 'predicted_team' in header.lower():
            key_columns['predicted_team'] = {'index': i, 'letter': col_letter, 'name': header}
        elif 'spread_cover_away' in header.lower():
            key_columns['spread_cover_away'] = {'index': i, 'letter': col_letter, 'name': header}
        elif 'predicted_cover_away' in header.lower():
            key_columns['predicted_cover_away'] = {'index': i, 'letter': col_letter, 'name': header}
        elif 'actual_total' in header.lower():
            key_columns['actual_total'] = {'index': i, 'letter': col_letter, 'name': header}
        elif 'predicted_home_score' in header.lower():
            key_columns['predicted_home_score'] = {'index': i, 'letter': col_letter, 'name': header}
        elif 'predicted_away_score' in header.lower():
            key_columns['predicted_away_score'] = {'index': i, 'letter': col_letter, 'name': header}
    
    # Display found columns
    for col_name, col_info in key_columns.items():
        print(f"  ✅ {col_info['letter']}: {col_info['name']}")
    
    # Check for missing columns
    required_columns = ['home_team', 'away_team', 'home_score', 'away_score', 'predicted_winner', 'predicted_spread', 'predicted_total']
    missing_columns = []
    for col in required_columns:
        if col not in key_columns:
            missing_columns.append(col)
    
    if missing_columns:
        print(f"\n⚠️ MISSING REQUIRED COLUMNS:")
        for col in missing_columns:
            print(f"  ❌ {col}")
    else:
        print(f"\n✅ ALL REQUIRED COLUMNS FOUND")
    
    # Check analysis columns
    analysis_columns = ['winning_team', 'predicted_team', 'spread_cover_away', 'predicted_cover_away', 'actual_total', 'predicted_home_score', 'predicted_away_score']
    found_analysis = []
    missing_analysis = []
    
    for col in analysis_columns:
        if col in key_columns:
            found_analysis.append(col)
        else:
            missing_analysis.append(col)
    
    print(f"\n📊 ANALYSIS COLUMNS STATUS:")
    print(f"  ✅ Found: {found_analysis}")
    if missing_analysis:
        print(f"  ❌ Missing: {missing_analysis}")
    
    # Check sample data in key columns
    print(f"\n📊 SAMPLE DATA CHECK:")
    for i in range(min(3, len(data_rows))):
        row = data_rows[i]
        row_num = i + 2
        print(f"  Row {row_num}:")
        
        for col_name, col_info in key_columns.items():
            if col_info['index'] < len(row):
                value = row[col_info['index']]
                print(f"    {col_info['letter']} ({col_name}): '{value}'")
            else:
                print(f"    {col_info['letter']} ({col_name}): MISSING")
    
    # Generate updated script configuration
    print(f"\n🔧 UPDATED SCRIPT CONFIGURATION:")
    print(f"# Updated column mapping based on current sheet structure")
    print(f"COLUMN_MAPPING = {{")
    for col_name, col_info in key_columns.items():
        print(f"    '{col_name}': {{'index': {col_info['index']}, 'letter': '{col_info['letter']}', 'name': '{col_info['name']}'}},")
    print(f"}}")
    
    # Identify areas affected by scripts
    print(f"\n📋 AREAS AFFECTED BY SCRIPTS:")
    print(f"  🎯 PREDICTION SCRIPTS:")
    print(f"    - Columns: {key_columns.get('predicted_winner', {}).get('letter', 'N/A')}, {key_columns.get('confidence_score', {}).get('letter', 'N/A')}, {key_columns.get('predicted_spread', {}).get('letter', 'N/A')}, {key_columns.get('predicted_total', {}).get('letter', 'N/A')}")
    print(f"    - Purpose: Add predictions to games")
    
    print(f"  🎯 OUTCOME TRACKING SCRIPTS:")
    print(f"    - Columns: {key_columns.get('prediction_result', {}).get('letter', 'N/A')}, {key_columns.get('prediction_outcome', {}).get('letter', 'N/A')}")
    print(f"    - Purpose: Track wins/losses")
    
    print(f"  🎯 ANALYSIS COLUMNS:")
    analysis_letters = [key_columns[col]['letter'] for col in found_analysis if col in key_columns]
    print(f"    - Columns: {', '.join(analysis_letters)}")
    print(f"    - Purpose: Detailed prediction analysis")
    
    print(f"  🎯 SCORING CHARTS:")
    print(f"    - Purpose: Performance tracking (wins/losses/win rates)")
    
    print(f"\n✅ SCAN COMPLETE - Scripts can be updated with new column mapping!")

if __name__ == "__main__":
    main()


