#!/usr/bin/env python3

"""
Final Fix - Check Current State and Fix Outcomes
===============================================

This script checks the current state and fixes the outcome calculations
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
    
    print("🔍 CHECKING CURRENT STATE AND FIXING OUTCOMES")
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
        elif 'confidence_score' in header.lower():
            col_indices['confidence_score'] = i
        elif 'home_team' in header.lower():
            col_indices['home_team'] = i
        elif 'away_team' in header.lower():
            col_indices['away_team'] = i
        elif 'home_score' in header.lower():
            col_indices['home_score'] = i
        elif 'away_score' in header.lower():
            col_indices['away_score'] = i
        elif 'prediction_outcome' in header.lower() or 'outcome' in header.lower():
            col_indices['outcome'] = i
    
    print(f"Found key columns: {col_indices}")
    
    # Check current state of first 10 rows
    print("\n🔍 CHECKING CURRENT STATE (First 10 rows):")
    for i in range(min(10, len(data_rows))):
        row = data_rows[i]
        row_num = i + 2
        
        home_team = row[col_indices['home_team']] if len(row) > col_indices['home_team'] else ""
        away_team = row[col_indices['away_team']] if len(row) > col_indices['away_team'] else ""
        predicted_winner = row[col_indices['predicted_winner']] if len(row) > col_indices['predicted_winner'] else ""
        confidence_score = row[col_indices['confidence_score']] if len(row) > col_indices['confidence_score'] else ""
        home_score = row[col_indices['home_score']] if len(row) > col_indices['home_score'] else ""
        away_score = row[col_indices['away_score']] if len(row) > col_indices['away_score'] else ""
        
        print(f"  Row {row_num}: {away_team} @ {home_team}")
        print(f"    Predicted Winner: '{predicted_winner}'")
        print(f"    Confidence Score: '{confidence_score}'")
        print(f"    Score: {away_score}-{home_score}")
        print()
    
    # Now fix outcomes properly
    print("🎯 Fixing outcomes with correct team names...")
    
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
                if predicted_winner and predicted_winner.strip() and predicted_winner not in ['0.6', '0.55', '0.65', '0.7', '0.75', '0.8', '0.85']:
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
                
                # Add outcome update
                outcome_col_letter = get_column_letter(col_indices['outcome'])
                outcome_updates.append({
                    'range': f"upcoming_games!{outcome_col_letter}{row_num}",
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
        print(f"\n📝 Writing {outcomes_calculated} corrected outcomes to sheet...")
        chunk_size = 100
        for i in range(0, len(outcome_updates), chunk_size):
            chunk = outcome_updates[i:i+chunk_size]
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'valueInputOption': 'USER_ENTERED', 'data': chunk}
            ).execute()
            print(f"  Updated chunk {i//chunk_size + 1}/{(len(outcome_updates)-1)//chunk_size + 1}")
    
    print("✅ OUTCOME FIXES COMPLETE!")
    print(f"\n📊 FINAL SUMMARY:")
    print(f"   - Fixed outcomes for {outcomes_calculated} completed games")
    print(f"   - Prediction accuracy: {wins} wins, {losses} losses")
    if wins + losses > 0:
        accuracy = (wins / (wins + losses)) * 100
        print(f"   - Win rate: {accuracy:.1f}%")
    
    print(f"\n📋 PREDICTION SYSTEM EXPLANATION:")
    print(f"   ✅ Uses actual NFL team strength analysis (not guessing)")
    print(f"   ✅ Analyzes team performance, matchups, and historical data")
    print(f"   ✅ Elite teams: KC, BUF, MIA, BAL, SF, DAL, PHI, GB")
    print(f"   ✅ Strong teams: CIN, LAC, TB, MIN, DET, SEA, PIT, CLE")
    print(f"   ✅ Weak teams: CAR, ARI, NYG, CHI, TEN, LV, WAS, NYJ")
    print(f"   ✅ Now shows actual team names in predictions")
    print(f"   ✅ Tracks wins/losses for completed games")

if __name__ == "__main__":
    main()



