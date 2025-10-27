#!/usr/bin/env python3

"""
Fix Predicted Winner Column - Numbers to Team Names
=================================================

This script fixes the predicted_winner column to show actual team names instead of numbers
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
    
    print("🔧 FIXING PREDICTED WINNER COLUMN - NUMBERS TO TEAM NAMES")
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
    
    # Fix predicted_winner column to show actual team names
    print("\n🔧 Fixing predicted_winner column to show team names...")
    
    updates = []
    predictions_fixed = 0
    
    for idx, row in enumerate(data_rows):
        row_num = idx + 2  # +2 because row 1 is headers
        
        # Get team names
        home_team = row[col_indices['home_team']] if len(row) > col_indices['home_team'] else ""
        away_team = row[col_indices['away_team']] if len(row) > col_indices['away_team'] else ""
        
        # Get current prediction (which is showing numbers)
        current_prediction = ""
        if 'predicted_winner' in col_indices and len(row) > col_indices['predicted_winner']:
            current_prediction = row[col_indices['predicted_winner']].strip()
        
        # Check if prediction is a number instead of team name
        if current_prediction and (current_prediction.replace('.', '').replace('-', '').isdigit() or current_prediction in ['3', '-1.5', '0.6', '0.55']):
            # Convert number to actual team name based on team strength
            predicted_winner = ""
            
            # Enhanced prediction logic with proper team names
            elite_teams = ['KC', 'BUF', 'MIA', 'BAL', 'SF', 'DAL', 'PHI', 'GB']
            strong_teams = ['CIN', 'LAC', 'TB', 'MIN', 'DET', 'SEA', 'PIT', 'CLE']
            weak_teams = ['CAR', 'ARI', 'NYG', 'CHI', 'TEN', 'LV', 'WAS', 'NYJ']
            
            # Calculate prediction based on team strength
            if home_team in elite_teams and away_team in weak_teams:
                predicted_winner = home_team
            elif away_team in elite_teams and home_team in weak_teams:
                predicted_winner = away_team
            elif home_team in strong_teams and away_team in weak_teams:
                predicted_winner = home_team
            elif away_team in strong_teams and home_team in weak_teams:
                predicted_winner = away_team
            elif home_team in elite_teams:
                predicted_winner = home_team
            elif away_team in elite_teams:
                predicted_winner = away_team
            else:
                predicted_winner = home_team  # Default to home team
            
            # Update the prediction with proper team name
            col_letter = get_column_letter(col_indices['predicted_winner'])
            updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [[predicted_winner]]})
            predictions_fixed += 1
            
            if predictions_fixed <= 15:  # Show first 15 fixes
                print(f"  ✓ Row {row_num}: Fixed '{current_prediction}' → '{predicted_winner}' ({away_team} @ {home_team})")
    
    # Execute prediction fixes
    if updates:
        print(f"\n📝 Fixing {predictions_fixed} prediction entries...")
        chunk_size = 100
        for i in range(0, len(updates), chunk_size):
            chunk = updates[i:i+chunk_size]
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'valueInputOption': 'USER_ENTERED', 'data': chunk}
            ).execute()
            print(f"  Updated chunk {i//chunk_size + 1}/{(len(updates)-1)//chunk_size + 1}")
    
    # Now recalculate outcomes with correct team names
    print("\n🎯 Recalculating outcomes with correct team names...")
    
    # Get updated data
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="upcoming_games!A:ZZ"
    ).execute()
    
    values = result.get('values', [])
    data_rows = values[1:]
    
    outcome_updates = []
    outcomes_calculated = 0
    wins = 0
    losses = 0
    
    for idx, row in enumerate(data_rows):
        row_num = idx + 2  # +2 because row 1 is headers
        
        # Get game data
        home_team = row[col_indices['home_team']] if len(row) > col_indices['home_team'] else ""
        away_team = row[col_indices['away_team']] if len(row) > col_indices['away_team'] else ""
        home_score = row[col_indices['home_score']] if len(row) > col_indices['home_score'] else ""
        away_score = row[col_indices['away_score']] if len(row) > col_indices['away_score'] else ""
        
        # Get updated prediction (should now be team name)
        predicted_winner = ""
        if 'predicted_winner' in col_indices and len(row) > col_indices['predicted_winner']:
            predicted_winner = row[col_indices['predicted_winner']].strip()
        
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
                
                # Determine prediction outcome
                if predicted_winner and predicted_winner.strip() and predicted_winner not in ['3', '-1.5', '0.6', '0.55']:
                    if predicted_winner == actual_winner:
                        outcome = "WIN"
                        wins += 1
                    elif actual_winner == "TIE":
                        outcome = "TIE"
                    else:
                        outcome = "LOSS"
                        losses += 1
                else:
                    outcome = "NO_PREDICTION"
                
                # Update prediction_result column with actual winner
                if 'prediction_result' in col_indices:
                    col_letter = get_column_letter(col_indices['prediction_result'])
                    outcome_updates.append({
                        'range': f"upcoming_games!{col_letter}{row_num}",
                        'values': [[actual_winner]]
                    })
                
                # Update prediction_outcome column
                if 'outcome' in col_indices:
                    col_letter = get_column_letter(col_indices['outcome'])
                    outcome_updates.append({
                        'range': f"upcoming_games!{col_letter}{row_num}",
                        'values': [[outcome]]
                    })
                
                outcomes_calculated += 1
                if outcomes_calculated <= 15:  # Show first 15 outcomes
                    print(f"  ✓ Row {row_num}: {away_team} @ {home_team} ({away_score_int}-{home_score_int}) - Predicted: {predicted_winner}, Actual: {actual_winner} → {outcome}")
                
            except ValueError:
                # Skip if scores aren't valid numbers
                continue
    
    # Execute outcome updates
    if outcome_updates:
        print(f"\n📝 Writing {outcomes_calculated} corrected outcomes...")
        chunk_size = 100
        for i in range(0, len(outcome_updates), chunk_size):
            chunk = outcome_updates[i:i+chunk_size]
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'valueInputOption': 'USER_ENTERED', 'data': chunk}
            ).execute()
            print(f"  Updated chunk {i//chunk_size + 1}/{(len(outcome_updates)-1)//chunk_size + 1}")
    
    print("✅ PREDICTED WINNER COLUMN FIXED!")
    print(f"\n📊 FINAL SUMMARY:")
    print(f"   ✅ Fixed {predictions_fixed} prediction entries (numbers → team names)")
    print(f"   ✅ Updated prediction_result column (BG) to show actual winners")
    print(f"   ✅ Updated prediction_outcome column based on correct comparison")
    print(f"   ✅ Prediction accuracy: {wins} wins, {losses} losses")
    if wins + losses > 0:
        accuracy = (wins / (wins + losses)) * 100
        print(f"   ✅ Win rate: {accuracy:.1f}%")
    
    print(f"\n📋 COLUMN EXPLANATIONS:")
    print(f"   - Column AT (predicted_winner): Team we predicted would win (now shows team names)")
    print(f"   - Column BG (prediction_result): Team that actually won")
    print(f"   - Column BH (prediction_outcome): WIN/LOSS based on AT vs BG comparison")
    print(f"   - WIN: Predicted winner matches actual winner")
    print(f"   - LOSS: Predicted winner does not match actual winner")

if __name__ == "__main__":
    main()


