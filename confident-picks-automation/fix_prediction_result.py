#!/usr/bin/env python3

"""
Fix Prediction Result Column
===========================

This script fixes the prediction_result column to show actual winners
and updates the prediction_outcome based on comparison with predicted_winner
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
    
    print("🔧 FIXING PREDICTION RESULT COLUMN")
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
    
    # Find column indices
    col_indices = {}
    for i, header in enumerate(headers):
        if 'predicted_winner' in header.lower():
            col_indices['predicted_winner'] = i
        elif 'prediction_result' in header.lower():
            col_indices['prediction_result'] = i
        elif 'prediction_outcome' in header.lower() or 'outcome' in header.lower():
            col_indices['outcome'] = i
        elif 'home_team' in header.lower():
            col_indices['home_team'] = i
        elif 'away_team' in header.lower():
            col_indices['away_team'] = i
        elif 'home_score' in header.lower():
            col_indices['home_score'] = i
        elif 'away_score' in header.lower():
            col_indices['away_score'] = i
    
    print(f"Found key columns: {col_indices}")
    
    # Fix prediction_result column and update outcomes
    print("\n🔧 Fixing prediction_result column...")
    
    updates = []
    games_processed = 0
    
    for idx, row in enumerate(data_rows):
        row_num = idx + 2  # +2 because row 1 is headers
        
        # Get game data
        home_team = row[col_indices['home_team']] if len(row) > col_indices['home_team'] else ""
        away_team = row[col_indices['away_team']] if len(row) > col_indices['away_team'] else ""
        home_score = row[col_indices['home_score']] if len(row) > col_indices['home_score'] else ""
        away_score = row[col_indices['away_score']] if len(row) > col_indices['away_score'] else ""
        predicted_winner = row[col_indices['predicted_winner']] if len(row) > col_indices['predicted_winner'] else ""
        
        # Check if game is completed (has scores)
        if home_score and away_score and home_score.strip() and away_score.strip():
            try:
                home_score_int = int(home_score)
                away_score_int = int(away_score)
                
                # Determine actual winner
                if home_score_int > away_score_int:
                    actual_winner = home_team
                elif away_score_int > home_score_int:
                    actual_winner = away_team
                else:
                    actual_winner = "TIE"
                
                # Update prediction_result column with actual winner
                if 'prediction_result' in col_indices:
                    col_letter = get_column_letter(col_indices['prediction_result'])
                    updates.append({
                        'range': f"upcoming_games!{col_letter}{row_num}",
                        'values': [[actual_winner]]
                    })
                
                # Determine prediction outcome by comparing predicted vs actual
                if predicted_winner and predicted_winner.strip():
                    if predicted_winner == actual_winner:
                        outcome = "WIN"
                    elif actual_winner == "TIE":
                        outcome = "TIE"
                    else:
                        outcome = "LOSS"
                else:
                    outcome = "NO_PREDICTION"
                
                # Update prediction_outcome column
                if 'outcome' in col_indices:
                    col_letter = get_column_letter(col_indices['outcome'])
                    updates.append({
                        'range': f"upcoming_games!{col_letter}{row_num}",
                        'values': [[outcome]]
                    })
                
                games_processed += 1
                if games_processed <= 15:  # Show first 15 games
                    print(f"  ✓ Row {row_num}: {away_team} @ {home_team} ({away_score_int}-{home_score_int})")
                    print(f"    Predicted: {predicted_winner}, Actual: {actual_winner} → {outcome}")
                
            except ValueError:
                # Skip if scores aren't valid numbers
                continue
    
    # Execute updates
    if updates:
        print(f"\n📝 Writing {games_processed} prediction results and outcomes...")
        chunk_size = 100
        for i in range(0, len(updates), chunk_size):
            chunk = updates[i:i+chunk_size]
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'valueInputOption': 'USER_ENTERED', 'data': chunk}
            ).execute()
            print(f"  Updated chunk {i//chunk_size + 1}/{(len(updates)-1)//chunk_size + 1}")
    
    print("✅ PREDICTION RESULT COLUMN FIXED!")
    print(f"\n📊 SUMMARY:")
    print(f"   ✅ Updated prediction_result column (BG) to show actual winners")
    print(f"   ✅ Updated prediction_outcome column based on predicted vs actual comparison")
    print(f"   ✅ Processed {games_processed} completed games")
    
    print(f"\n📋 COLUMN EXPLANATIONS:")
    print(f"   - Column AT (predicted_winner): Team we predicted would win")
    print(f"   - Column BG (prediction_result): Team that actually won")
    print(f"   - Column BH (prediction_outcome): WIN/LOSS based on AT vs BG comparison")
    print(f"   - WIN: Predicted winner matches actual winner")
    print(f"   - LOSS: Predicted winner does not match actual winner")

if __name__ == "__main__":
    main()


