#!/usr/bin/env python3

"""
Update Scripts with New Column Structure
======================================

This script updates all scripts with the new column mapping and fixes issues
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
    
    print("🔧 UPDATING SCRIPTS WITH NEW COLUMN STRUCTURE")
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
    
    # ISSUES IDENTIFIED:
    # 1. Duplicate predicted_winner columns (AT and AU)
    # 2. Missing winning_team, predicted_home_score, predicted_away_score columns
    # 3. Formulas showing #REF! errors
    # 4. Score columns moved to BR/BS but formulas still reference I/K
    
    print(f"\n🔧 FIXING IDENTIFIED ISSUES:")
    
    # Issue 1: Remove duplicate predicted_winner column (AT)
    print("1. Removing duplicate predicted_winner column (AT)...")
    
    # Find the duplicate column index
    duplicate_index = None
    for i, header in enumerate(headers):
        if header == 'predicted_winner' and i == 45:  # Column AT (index 45)
            duplicate_index = i
            break
    
    if duplicate_index is not None:
        print(f"Found duplicate predicted_winner column at index {duplicate_index} (Column {get_column_letter(duplicate_index)})")
        
        # Remove the duplicate column by shifting all columns to the left
        new_headers = []
        new_data = []
        
        # Process headers
        for i, header in enumerate(headers):
            if i != duplicate_index:
                new_headers.append(header)
        
        # Process data rows
        for row in data_rows:
            new_row = []
            for i, value in enumerate(row):
                if i != duplicate_index:
                    new_row.append(value)
            new_data.append(new_row)
        
        # Clear the sheet and write new data
        print("Clearing sheet and writing cleaned data...")
        service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range="upcoming_games!A:ZZ"
        ).execute()
        
        # Write new headers and data
        all_data = [new_headers] + new_data
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="upcoming_games!A1",
            valueInputOption='USER_ENTERED',
            body={'values': all_data}
        ).execute()
        
        print("✅ Duplicate predicted_winner column removed!")
        
        # Update data_rows to use new data
        data_rows = new_data
        headers = new_headers
    else:
        print("Duplicate predicted_winner column not found")
    
    # Issue 2: Add missing analysis columns
    print("\n2. Adding missing analysis columns...")
    
    # Get updated data
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="upcoming_games!A:ZZ"
    ).execute()
    
    values = result.get('values', [])
    headers = values[0]
    data_rows = values[1:]
    
    # Find where to add missing columns (after BM)
    bm_index = None
    for i, header in enumerate(headers):
        if header == 'Predicted_Away_Score' and i == 63:  # Column BM (index 63)
            bm_index = i
            break
    
    if bm_index is not None:
        # Add missing columns after BM
        missing_columns = ['Winning_Team', 'Predicted_Home_Score', 'Predicted_Away_Score']
        
        updates = []
        for i, column_name in enumerate(missing_columns):
            col_index = bm_index + 1 + i
            col_letter = get_column_letter(col_index)
            updates.append({
                'range': f"upcoming_games!{col_letter}1",
                'values': [[column_name]]
            })
        
        if updates:
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'valueInputOption': 'USER_ENTERED', 'data': updates}
            ).execute()
            print(f"✅ Added {len(missing_columns)} missing analysis columns")
    
    # Issue 3: Fix formulas with correct column references
    print("\n3. Fixing formulas with correct column references...")
    
    # Get updated data
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="upcoming_games!A:ZZ"
    ).execute()
    
    values = result.get('values', [])
    headers = values[0]
    data_rows = values[1:]
    
    # Find column indices for formulas
    col_indices = {}
    for i, header in enumerate(headers):
        if 'home_team' in header.lower():
            col_indices['home_team'] = i
        elif 'away_team' in header.lower():
            col_indices['away_team'] = i
        elif 'home_score' in header.lower():
            col_indices['home_score'] = i
        elif 'away_score' in header.lower():
            col_indices['away_score'] = i
        elif 'predicted_winner' in header.lower():
            col_indices['predicted_winner'] = i
        elif 'spread_line' in header.lower():
            col_indices['spread_line'] = i
        elif 'predicted_spread' in header.lower():
            col_indices['predicted_spread'] = i
        elif 'predicted_total' in header.lower():
            col_indices['predicted_total'] = i
        elif 'winning_team' in header.lower():
            col_indices['winning_team'] = i
        elif 'predicted_home_score' in header.lower():
            col_indices['predicted_home_score'] = i
        elif 'predicted_away_score' in header.lower():
            col_indices['predicted_away_score'] = i
    
    print(f"Found column indices: {col_indices}")
    
    # Fix formulas
    formula_updates = []
    
    # Fix Winning_Team formula (if it exists)
    if 'winning_team' in col_indices:
        col_letter = get_column_letter(col_indices['winning_team'])
        formula_updates.append({
            'range': f"upcoming_games!{col_letter}2",
            'values': [['=IF(BR2>BS2,J2,H2)']]  # IF(home_score>away_score,home_team,away_team)
        })
    
    # Fix Predicted_Team formula
    if 'predicted_winner' in col_indices:
        col_letter = get_column_letter(col_indices['predicted_winner'])
        formula_updates.append({
            'range': f"upcoming_games!BG2",
            'values': [['=AT2']]  # predicted_winner
        })
    
    # Fix Spread_Cover_Away formula
    formula_updates.append({
        'range': "upcoming_games!BH2",
        'values': [['=IF(BS2+AA2>BR2,"YES","NO")']]  # IF(away_score+spread_line>home_score,"YES","NO")
    })
    
    # Fix Predicted_Cover_Away formula
    formula_updates.append({
        'range': "upcoming_games!BI2",
        'values': [['=IF(AW2<0,"YES","NO")']]  # IF(predicted_spread<0,"YES","NO")
    })
    
    # Fix Actual_Total formula
    formula_updates.append({
        'range': "upcoming_games!BJ2",
        'values': [['=BR2+BS2']]  # home_score+away_score
    })
    
    # Fix Predicted_Total formula
    formula_updates.append({
        'range': "upcoming_games!BK2",
        'values': [['=AX2']]  # predicted_total
    })
    
    # Fix Predicted_Home_Score formula
    formula_updates.append({
        'range': "upcoming_games!BL2",
        'values': [['=(AX2+AW2)/2']]  # (predicted_total+predicted_spread)/2
    })
    
    # Fix Predicted_Away_Score formula
    formula_updates.append({
        'range': "upcoming_games!BM2",
        'values': [['=(AX2-AW2)/2']]  # (predicted_total-predicted_spread)/2
    })
    
    # Execute formula updates
    if formula_updates:
        print("Adding corrected formulas...")
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'valueInputOption': 'USER_ENTERED', 'data': formula_updates}
        ).execute()
        print(f"✅ Added {len(formula_updates)} corrected formulas")
    
    # Copy formulas down to all rows
    print(f"\n📋 Copying formulas to all rows...")
    
    copy_updates = []
    analysis_columns = ['BG', 'BH', 'BI', 'BJ', 'BK', 'BL', 'BM']
    
    for col_letter in analysis_columns:
        # Copy formula from row 2 to all other rows
        copy_updates.append({
            'range': f"upcoming_games!{col_letter}2:{col_letter}{len(data_rows) + 1}",
            'values': [[f'={col_letter}2']] * len(data_rows)
        })
    
    if copy_updates:
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'valueInputOption': 'USER_ENTERED', 'data': copy_updates}
        ).execute()
        print(f"✅ Copied formulas to all {len(data_rows)} rows")
    
    print("✅ ALL SCRIPTS UPDATED!")
    print(f"\n📊 UPDATED COLUMN MAPPING:")
    print(f"   ✅ H: away_team")
    print(f"   ✅ J: home_team")
    print(f"   ✅ BR: home_score (Home_Score_Result)")
    print(f"   ✅ BS: away_score (Away_Score_Reuslt)")
    print(f"   ✅ AA: spread_line")
    print(f"   ✅ AD: total_line")
    print(f"   ✅ AT: predicted_winner")
    print(f"   ✅ AV: confidence_score")
    print(f"   ✅ AW: predicted_spread")
    print(f"   ✅ AX: predicted_total")
    
    print(f"\n📊 ANALYSIS COLUMNS:")
    print(f"   ✅ BG: Predicted_Team")
    print(f"   ✅ BH: Spread_Cover_Away")
    print(f"   ✅ BI: Predicted_Cover_Away")
    print(f"   ✅ BJ: Actual_Total")
    print(f"   ✅ BK: Predicted_Total")
    print(f"   ✅ BL: Predicted_Home_Score")
    print(f"   ✅ BM: Predicted_Away_Score")
    
    print(f"\n📋 AREAS AFFECTED BY SCRIPTS:")
    print(f"   🎯 PREDICTION SCRIPTS: Columns AT, AV, AW, AX")
    print(f"   🎯 OUTCOME TRACKING: Columns BR, BS (scores)")
    print(f"   🎯 ANALYSIS COLUMNS: Columns BG-BM")
    print(f"   🎯 SCORING CHARTS: Performance tracking")

if __name__ == "__main__":
    main()


