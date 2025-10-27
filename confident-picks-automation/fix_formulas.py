#!/usr/bin/env python3

"""
Fix Analysis Column Formulas
===========================

This script fixes the formulas in the analysis columns with correct references
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
    
    print("🔧 FIXING ANALYSIS COLUMN FORMULAS")
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
    
    # Based on the column structure, here are the correct column indices:
    # H: away_team (index 7)
    # I: away_score (index 8) 
    # J: home_team (index 9)
    # K: home_score (index 10)
    # AA: spread_line (index 26)
    # AD: total_line (index 29)
    # AT: predicted_winner (index 45)
    # AV: predicted_spread (index 47)
    # AW: predicted_total (index 48)
    
    # Analysis columns:
    # BF: Winning_Team (index 57)
    # BG: Predicted_Team (index 58)
    # BH: Spread_Cover_Away (index 59)
    # BI: Predicted_Cover_Away (index 60)
    # BJ: Actual_Total (index 61)
    # BK: Predicted_Total (index 62)
    # BL: Predicted_Home_Score (index 63)
    # BM: Predicted_Away_Score (index 64)
    
    print("\n🔧 Fixing formulas with correct column references...")
    
    formula_updates = []
    
    # 1. Winning_Team formula (BF) - Compare home_score vs away_score
    formula_updates.append({
        'range': "upcoming_games!BF2",
        'values': [['=IF(K2>I2,J2,H2)']]  # IF(home_score>away_score,home_team,away_team)
    })
    
    # 2. Predicted_Team formula (BG) - Copy from predicted_winner
    formula_updates.append({
        'range': "upcoming_games!BG2",
        'values': [['=AT2']]  # predicted_winner
    })
    
    # 3. Spread_Cover_Away formula (BH) - Check if away team covered the spread
    formula_updates.append({
        'range': "upcoming_games!BH2",
        'values': [['=IF(I2+AA2>K2,"YES","NO")']]  # IF(away_score+spread_line>home_score,"YES","NO")
    })
    
    # 4. Predicted_Cover_Away formula (BI) - Check if we predicted away team would cover
    formula_updates.append({
        'range': "upcoming_games!BI2",
        'values': [['=IF(AV2<0,"YES","NO")']]  # IF(predicted_spread<0,"YES","NO")
    })
    
    # 5. Actual_Total formula (BJ) - Sum of actual scores
    formula_updates.append({
        'range': "upcoming_games!BJ2",
        'values': [['=K2+I2']]  # home_score+away_score
    })
    
    # 6. Predicted_Total formula (BK) - Copy from predicted_total
    formula_updates.append({
        'range': "upcoming_games!BK2",
        'values': [['=AW2']]  # predicted_total
    })
    
    # 7. Predicted_Home_Score formula (BL) - Calculate from predicted_total and predicted_spread
    formula_updates.append({
        'range': "upcoming_games!BL2",
        'values': [['=(AW2+AV2)/2']]  # (predicted_total+predicted_spread)/2
    })
    
    # 8. Predicted_Away_Score formula (BM) - Calculate from predicted_total and predicted_spread
    formula_updates.append({
        'range': "upcoming_games!BM2",
        'values': [['=(AW2-AV2)/2']]  # (predicted_total-predicted_spread)/2
    })
    
    # Execute formula updates
    print("Adding corrected formulas...")
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'valueInputOption': 'USER_ENTERED', 'data': formula_updates}
    ).execute()
    print(f"✅ Added {len(formula_updates)} corrected formulas")
    
    # Copy formulas down to all rows
    print(f"\n📋 Copying formulas to all rows...")
    
    copy_updates = []
    analysis_columns = ['BF', 'BG', 'BH', 'BI', 'BJ', 'BK', 'BL', 'BM']
    
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
    
    print("✅ ALL FORMULAS FIXED!")
    print(f"\n📊 CORRECTED FORMULAS:")
    print(f"   ✅ BF (Winning_Team): =IF(K2>I2,J2,H2)")
    print(f"   ✅ BG (Predicted_Team): =AT2")
    print(f"   ✅ BH (Spread_Cover_Away): =IF(I2+AA2>K2,\"YES\",\"NO\")")
    print(f"   ✅ BI (Predicted_Cover_Away): =IF(AV2<0,\"YES\",\"NO\")")
    print(f"   ✅ BJ (Actual_Total): =K2+I2")
    print(f"   ✅ BK (Predicted_Total): =AW2")
    print(f"   ✅ BL (Predicted_Home_Score): =(AW2+AV2)/2")
    print(f"   ✅ BM (Predicted_Away_Score): =(AW2-AV2)/2")
    
    print(f"\n📋 COLUMN REFERENCE GUIDE:")
    print(f"   - H: away_team")
    print(f"   - I: away_score")
    print(f"   - J: home_team")
    print(f"   - K: home_score")
    print(f"   - AA: spread_line")
    print(f"   - AD: total_line")
    print(f"   - AT: predicted_winner")
    print(f"   - AV: predicted_spread")
    print(f"   - AW: predicted_total")

if __name__ == "__main__":
    main()


