#!/usr/bin/env python3

"""
Add Comprehensive Prediction Analysis Columns - Fixed Version
===========================================================

This script adds detailed analysis columns after column BE with formulas
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
    
    print("📊 ADDING COMPREHENSIVE PREDICTION ANALYSIS COLUMNS")
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
    
    # Find column BE index
    be_index = None
    for i, header in enumerate(headers):
        if i == 56:  # Column BE (index 56)
            be_index = i
            break
    
    if be_index is None:
        print("❌ Column BE not found")
        return
    
    print(f"Found column BE at index {be_index}")
    
    # Define new columns to add after BE
    new_columns = [
        "Winning_Team",
        "Predicted_Team", 
        "Spread_Cover_Away",
        "Predicted_Cover_Away",
        "Actual_Total",
        "Predicted_Total",
        "Predicted_Home_Score",
        "Predicted_Away_Score"
    ]
    
    # Add new column headers
    print(f"\n📝 Adding {len(new_columns)} new analysis columns...")
    
    updates = []
    
    # Add headers starting after column BE
    for i, column_name in enumerate(new_columns):
        col_index = be_index + 1 + i
        col_letter = get_column_letter(col_index)
        updates.append({
            'range': f"upcoming_games!{col_letter}1",
            'values': [[column_name]]
        })
    
    # Execute header updates
    if updates:
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'valueInputOption': 'USER_ENTERED', 'data': updates}
        ).execute()
        print(f"✅ Added {len(new_columns)} column headers")
    
    # Now add formulas for each column
    print(f"\n🧮 Adding formulas for analysis columns...")
    
    # Get updated data to find column indices
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="upcoming_games!A:ZZ"
    ).execute()
    
    values = result.get('values', [])
    headers = values[0]
    
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
        elif 'total_line' in header.lower():
            col_indices['total_line'] = i
        elif 'predicted_total' in header.lower():
            col_indices['predicted_total'] = i
    
    print(f"Found column indices: {col_indices}")
    
    # Add formulas for each new column
    formula_updates = []
    
    # 1. Winning_Team formula
    col_letter = get_column_letter(be_index + 1)  # BF
    formula = f'=IF({get_column_letter(col_indices["home_score"])}2>{get_column_letter(col_indices["away_score"])}2,{get_column_letter(col_indices["home_team"])}2,{get_column_letter(col_indices["away_team"])}2)'
    formula_updates.append({
        'range': f"upcoming_games!{col_letter}2",
        'values': [[formula]]
    })
    
    # 2. Predicted_Team formula (just copy from predicted_winner)
    col_letter = get_column_letter(be_index + 2)  # BG
    formula = f'={get_column_letter(col_indices["predicted_winner"])}2'
    formula_updates.append({
        'range': f"upcoming_games!{col_letter}2",
        'values': [[formula]]
    })
    
    # 3. Spread_Cover_Away formula
    col_letter = get_column_letter(be_index + 3)  # BH
    formula = f'=IF({get_column_letter(col_indices["away_score"])}2+{get_column_letter(col_indices["spread_line"])}2>{get_column_letter(col_indices["home_score"])}2,"YES","NO")'
    formula_updates.append({
        'range': f"upcoming_games!{col_letter}2",
        'values': [[formula]]
    })
    
    # 4. Predicted_Cover_Away formula (simplified)
    col_letter = get_column_letter(be_index + 4)  # BI
    formula = f'=IF({get_column_letter(col_indices["predicted_spread"])}2<0,"YES","NO")'
    formula_updates.append({
        'range': f"upcoming_games!{col_letter}2",
        'values': [[formula]]
    })
    
    # 5. Actual_Total formula
    col_letter = get_column_letter(be_index + 5)  # BJ
    formula = f'={get_column_letter(col_indices["home_score"])}2+{get_column_letter(col_indices["away_score"])}2'
    formula_updates.append({
        'range': f"upcoming_games!{col_letter}2",
        'values': [[formula]]
    })
    
    # 6. Predicted_Total formula (copy from predicted_total)
    col_letter = get_column_letter(be_index + 6)  # BK
    formula = f'={get_column_letter(col_indices["predicted_total"])}2'
    formula_updates.append({
        'range': f"upcoming_games!{col_letter}2",
        'values': [[formula]]
    })
    
    # 7. Predicted_Home_Score formula
    col_letter = get_column_letter(be_index + 7)  # BL
    formula = f'=({get_column_letter(col_indices["predicted_total"])}2+{get_column_letter(col_indices["predicted_spread"])}2)/2'
    formula_updates.append({
        'range': f"upcoming_games!{col_letter}2",
        'values': [[formula]]
    })
    
    # 8. Predicted_Away_Score formula
    col_letter = get_column_letter(be_index + 8)  # BM
    formula = f'=({get_column_letter(col_indices["predicted_total"])}2-{get_column_letter(col_indices["predicted_spread"])}2)/2'
    formula_updates.append({
        'range': f"upcoming_games!{col_letter}2",
        'values': [[formula]]
    })
    
    # Execute formula updates
    if formula_updates:
        print("Adding formulas...")
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'valueInputOption': 'USER_ENTERED', 'data': formula_updates}
        ).execute()
        print(f"✅ Added {len(formula_updates)} formulas")
    
    # Copy formulas down to all rows
    print(f"\n📋 Copying formulas to all rows...")
    
    copy_updates = []
    for i in range(len(new_columns)):
        col_index = be_index + 1 + i
        col_letter = get_column_letter(col_index)
        
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
    
    print("✅ ALL ANALYSIS COLUMNS ADDED!")
    print(f"\n📊 NEW COLUMNS ADDED AFTER BE:")
    print(f"   ✅ BF: Winning_Team - Actual winner based on scores")
    print(f"   ✅ BG: Predicted_Team - Team we predicted would win")
    print(f"   ✅ BH: Spread_Cover_Away - Did away team cover the spread?")
    print(f"   ✅ BI: Predicted_Cover_Away - Did we predict away team would cover?")
    print(f"   ✅ BJ: Actual_Total - Sum of actual scores")
    print(f"   ✅ BK: Predicted_Total - Our predicted total points")
    print(f"   ✅ BL: Predicted_Home_Score - Our predicted home team score")
    print(f"   ✅ BM: Predicted_Away_Score - Our predicted away team score")
    
    print(f"\n📋 FORMULA EXPLANATIONS:")
    print(f"   - Winning_Team: =IF(home_score>away_score,home_team,away_team)")
    print(f"   - Predicted_Team: =predicted_winner")
    print(f"   - Spread_Cover_Away: =IF(away_score+spread_line>home_score,\"YES\",\"NO\")")
    print(f"   - Predicted_Cover_Away: =IF(predicted_spread<0,\"YES\",\"NO\")")
    print(f"   - Actual_Total: =home_score+away_score")
    print(f"   - Predicted_Total: =predicted_total")
    print(f"   - Predicted_Home_Score: =(predicted_total+predicted_spread)/2")
    print(f"   - Predicted_Away_Score: =(predicted_total-predicted_spread)/2")

if __name__ == "__main__":
    main()


