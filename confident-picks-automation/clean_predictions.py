#!/usr/bin/env python3

"""
Clean Predictions for Organized Sheet
===================================

This script adds predictions to the clean, organized upcoming_games sheet
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
    
    print("🏈 Clean NFL Predictions for Organized Sheet")
    print("=" * 60)
    
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
    print(f"✅ Clean structure with {len(headers)} columns")
    
    # Find prediction column indices in the clean structure
    col_indices = {}
    for i, header in enumerate(headers):
        if 'predicted_winner' in header.lower():
            col_indices['predicted_winner'] = i
        elif 'confidence_score' in header.lower():
            col_indices['confidence_score'] = i
        elif 'predicted_spread' in header.lower():
            col_indices['predicted_spread'] = i
        elif 'predicted_total' in header.lower():
            col_indices['predicted_total'] = i
        elif 'edge_vs_line' in header.lower():
            col_indices['edge_vs_line'] = i
        elif 'line_movement' in header.lower():
            col_indices['line_movement'] = i
        elif 'sharp_money' in header.lower():
            col_indices['sharp_money'] = i
        elif 'public_percentage' in header.lower():
            col_indices['public_percentage'] = i
        elif 'value_rating' in header.lower():
            col_indices['value_rating'] = i
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
    
    # Make predictions for ALL games
    print("🎯 Making predictions for ALL games...")
    
    updates = []
    predictions_made = 0
    
    for idx, row in enumerate(data_rows):
        # Get team names
        home_team = row[10] if len(row) > 10 else ""
        away_team = row[7] if len(row) > 7 else ""
        
        if home_team and away_team:
            row_num = idx + 2  # +2 because row 1 is headers
            
            # Enhanced prediction logic
            elite_teams = ['KC', 'BUF', 'MIA', 'BAL', 'SF', 'DAL', 'PHI', 'GB']
            strong_teams = ['CIN', 'LAC', 'TB', 'MIN', 'DET', 'SEA', 'PIT', 'CLE']
            weak_teams = ['CAR', 'ARI', 'NYG', 'CHI', 'TEN', 'LV', 'WAS', 'NYJ']
            
            # Calculate base confidence and prediction
            if home_team in elite_teams and away_team in weak_teams:
                predicted_winner = home_team
                confidence = 0.85
                predicted_spread = -7.5
                predicted_total = 48.5
            elif away_team in elite_teams and home_team in weak_teams:
                predicted_winner = away_team
                confidence = 0.80
                predicted_spread = 7.0
                predicted_total = 47.0
            elif home_team in strong_teams and away_team in weak_teams:
                predicted_winner = home_team
                confidence = 0.75
                predicted_spread = -5.5
                predicted_total = 46.0
            elif away_team in strong_teams and home_team in weak_teams:
                predicted_winner = away_team
                confidence = 0.70
                predicted_spread = 5.0
                predicted_total = 45.5
            elif home_team in elite_teams:
                predicted_winner = home_team
                confidence = 0.65
                predicted_spread = -3.5
                predicted_total = 47.5
            elif away_team in elite_teams:
                predicted_winner = away_team
                confidence = 0.60
                predicted_spread = 3.0
                predicted_total = 46.5
            else:
                predicted_winner = home_team  # Default to home team
                confidence = 0.55
                predicted_spread = -1.5
                predicted_total = 45.0
            
            home_win_prob = confidence if predicted_winner == home_team else (1 - confidence)
            away_win_prob = 1 - home_win_prob
            
            # Betting recommendations
            if confidence > 0.75:
                recommendation = f"BET {predicted_winner}"
                value_rating = 5
            elif confidence > 0.65:
                recommendation = f"LEAN {predicted_winner}"
                value_rating = 3
            else:
                recommendation = "NO BET"
                value_rating = 1
            
            # Calculate edge vs line (simplified)
            edge_vs_line = round(confidence - 0.5, 2)
            
            # Add updates with correct column naming
            if 'predicted_winner' in col_indices:
                col_letter = get_column_letter(col_indices['predicted_winner'])
                updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [[predicted_winner]]})
            if 'confidence_score' in col_indices:
                col_letter = get_column_letter(col_indices['confidence_score'])
                updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [[round(confidence, 3)]]})
            if 'predicted_spread' in col_indices:
                col_letter = get_column_letter(col_indices['predicted_spread'])
                updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [[predicted_spread]]})
            if 'predicted_total' in col_indices:
                col_letter = get_column_letter(col_indices['predicted_total'])
                updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [[predicted_total]]})
            if 'edge_vs_line' in col_indices:
                col_letter = get_column_letter(col_indices['edge_vs_line'])
                updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [[edge_vs_line]]})
            if 'line_movement' in col_indices:
                col_letter = get_column_letter(col_indices['line_movement'])
                updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [["0"]]})  # Placeholder
            if 'sharp_money' in col_indices:
                col_letter = get_column_letter(col_indices['sharp_money'])
                updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [["TBD"]]})  # Placeholder
            if 'public_percentage' in col_indices:
                col_letter = get_column_letter(col_indices['public_percentage'])
                updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [["TBD"]]})  # Placeholder
            if 'value_rating' in col_indices:
                col_letter = get_column_letter(col_indices['value_rating'])
                updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [[value_rating]]})
            if 'home_win_probability' in col_indices:
                col_letter = get_column_letter(col_indices['home_win_probability'])
                updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [[round(home_win_prob, 3)]]})
            if 'away_win_probability' in col_indices:
                col_letter = get_column_letter(col_indices['away_win_probability'])
                updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [[round(away_win_prob, 3)]]})
            if 'betting_recommendation' in col_indices:
                col_letter = get_column_letter(col_indices['betting_recommendation'])
                updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [[recommendation]]})
            if 'betting_value' in col_indices:
                col_letter = get_column_letter(col_indices['betting_value'])
                updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [[round(confidence - 0.5, 3)]]})
            if 'model_last_updated' in col_indices:
                col_letter = get_column_letter(col_indices['model_last_updated'])
                updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [[datetime.now().strftime('%Y-%m-%d %H:%M:%S')]]})
            
            predictions_made += 1
            print(f"  ✓ {away_team} @ {home_team}: {predicted_winner} ({confidence:.1%} confidence)")
    
    # Execute updates
    print(f"\n📝 Writing {predictions_made} predictions to clean sheet...")
    
    if updates:
        chunk_size = 100  # Larger chunks for efficiency
        for i in range(0, len(updates), chunk_size):
            chunk = updates[i:i+chunk_size]
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'valueInputOption': 'USER_ENTERED', 'data': chunk}
            ).execute()
            print(f"  Updated chunk {i//chunk_size + 1}/{(len(updates)-1)//chunk_size + 1}")
    
    print("✅ ALL predictions successfully written to clean sheet!")
    print("\n📋 Your upcoming_games sheet is now clean and organized!")
    print("   - Columns 1-45: Original game data")
    print("   - Columns 46-59: Complete prediction data")
    print("   - Columns 60-61: Status information")
    print(f"   - Total predictions: {predictions_made}")

if __name__ == "__main__":
    main()



