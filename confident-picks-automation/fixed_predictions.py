#!/usr/bin/env python3

"""
Fixed Predictions Script
=======================

This script adds predictions with correct column naming for columns beyond Z
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
    
    print("🏈 Fixed NFL Predictions")
    print("=" * 40)
    
    # Get upcoming games data
    print("🔮 Loading upcoming games...")
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="upcoming_games!A:ZZ"
    ).execute()
    
    values = result.get('values', [])
    if not values or len(values) < 2:
        print("❌ No upcoming games found")
        return
    
    headers = values[0]
    data_rows = values[1:]
    
    print(f"✅ Found {len(data_rows)} upcoming games")
    
    # Find prediction column indices
    col_indices = {}
    for i, header in enumerate(headers):
        if 'predicted_winner' in header.lower():
            col_indices['predicted_winner'] = i
        elif 'confidence_score' in header.lower():
            col_indices['confidence_score'] = i
        elif 'home_win_probability' in header.lower():
            col_indices['home_win_probability'] = i
        elif 'away_win_probability' in header.lower():
            col_indices['away_win_probability'] = i
        elif 'betting_recommendation' in header.lower():
            col_indices['betting_recommendation'] = i
        elif 'betting_value' in header.lower():
            col_indices['betting_value'] = i
        elif 'model_last_updated' in header.lower():
            col_indices['model_last_updated'] = i
    
    print(f"Found prediction columns: {col_indices}")
    
    # Make simple predictions
    print("🎯 Making predictions...")
    
    updates = []
    predictions_made = 0
    
    for idx, row in enumerate(data_rows):
        # Skip if no teams
        if len(row) < 11:
            continue
            
        home_team = row[10] if len(row) > 10 else ""
        away_team = row[7] if len(row) > 7 else ""
        
        # Skip games with results already
        if len(row) > 12 and row[12] != '' and row[12] != '0':
            continue
        
        if home_team and away_team:
            row_num = idx + 2  # +2 because row 1 is headers
            
            # Simple prediction logic
            strong_teams = ['KC', 'BUF', 'MIA', 'BAL', 'SF', 'DAL', 'PHI', 'GB', 'CIN', 'LAC']
            
            if home_team in strong_teams and away_team not in strong_teams:
                predicted_winner = home_team
                confidence = 0.75
            elif away_team in strong_teams and home_team not in strong_teams:
                predicted_winner = away_team
                confidence = 0.70
            else:
                predicted_winner = home_team  # Default to home team
                confidence = 0.60
            
            home_win_prob = confidence if predicted_winner == home_team else (1 - confidence)
            away_win_prob = 1 - home_win_prob
            
            if confidence > 0.65:
                recommendation = f"BET {predicted_winner}"
            else:
                recommendation = "NO BET"
            
            # Add updates with correct column naming
            if 'predicted_winner' in col_indices:
                col_letter = get_column_letter(col_indices['predicted_winner'])
                updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [[predicted_winner]]})
            if 'confidence_score' in col_indices:
                col_letter = get_column_letter(col_indices['confidence_score'])
                updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [[confidence]]})
            if 'home_win_probability' in col_indices:
                col_letter = get_column_letter(col_indices['home_win_probability'])
                updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [[home_win_prob]]})
            if 'away_win_probability' in col_indices:
                col_letter = get_column_letter(col_indices['away_win_probability'])
                updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [[away_win_prob]]})
            if 'betting_recommendation' in col_indices:
                col_letter = get_column_letter(col_indices['betting_recommendation'])
                updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [[recommendation]]})
            if 'betting_value' in col_indices:
                col_letter = get_column_letter(col_indices['betting_value'])
                updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [[confidence - 0.5]]})
            if 'model_last_updated' in col_indices:
                col_letter = get_column_letter(col_indices['model_last_updated'])
                updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [[datetime.now().strftime('%Y-%m-%d %H:%M:%S')]]})
            
            predictions_made += 1
            print(f"  ✓ {away_team} @ {home_team}: {predicted_winner} ({confidence:.1%} confidence)")
    
    # Execute updates
    print(f"\n📝 Writing {predictions_made} predictions to sheet...")
    
    if updates:
        chunk_size = 50
        for i in range(0, len(updates), chunk_size):
            chunk = updates[i:i+chunk_size]
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'valueInputOption': 'USER_ENTERED', 'data': chunk}
            ).execute()
            print(f"  Updated chunk {i//chunk_size + 1}/{(len(updates)-1)//chunk_size + 1}")
    
    print("✅ Predictions successfully written to upcoming_games!")
    print("\n📋 Check your upcoming_games tab for predictions!")
    print("   Look for columns: predicted_winner, confidence_score, etc.")

if __name__ == "__main__":
    main()



