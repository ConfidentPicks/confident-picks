#!/usr/bin/env python3

"""
Enhanced Predictions with Wins/Losses Tracking
============================================

This script adds wins/losses tracking and fixes predictions for future games only
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
    
    print("🏈 Enhanced NFL Predictions with Wins/Losses Tracking")
    print("=" * 70)
    
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
    
    # Find column indices
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
    
    # Add wins/losses column if it doesn't exist
    if 'prediction_result' not in [h.lower() for h in headers]:
        print("📊 Adding prediction_result column...")
        # Add new column header
        new_headers = headers + ['prediction_result']
        
        # Update headers
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="upcoming_games!1:1",
            valueInputOption='USER_ENTERED',
            body={'values': [new_headers]}
        ).execute()
        
        # Update col_indices
        col_indices['prediction_result'] = len(headers)
        print("✅ Added prediction_result column")
    
    # Make predictions for FUTURE GAMES ONLY
    print("🎯 Making predictions for FUTURE games only...")
    
    updates = []
    predictions_made = 0
    future_games = 0
    
    for idx, row in enumerate(data_rows):
        # Get team names and game info
        home_team = row[10] if len(row) > 10 else ""
        away_team = row[7] if len(row) > 7 else ""
        game_date = row[4] if len(row) > 4 else ""  # gameday column
        result = row[12] if len(row) > 12 else ""  # result column
        
        if home_team and away_team:
            row_num = idx + 2  # +2 because row 1 is headers
            
            # Check if game is in the future (no result yet)
            is_future_game = result == '' or result == '0'
            
            if is_future_game:
                future_games += 1
                
                # Enhanced prediction logic
                elite_teams = ['KC', 'BUF', 'MIA', 'BAL', 'SF', 'DAL', 'PHI', 'GB']
                strong_teams = ['CIN', 'LAC', 'TB', 'MIN', 'DET', 'SEA', 'PIT', 'CLE']
                weak_teams = ['CAR', 'ARI', 'NYG', 'CHI', 'TEN', 'LV', 'WAS', 'NYJ']
                
                # Calculate prediction based on team strength
                if home_team in elite_teams and away_team in weak_teams:
                    predicted_winner = home_team
                    confidence = 0.85
                    predicted_spread = -7.5
                    predicted_total = 48.5
                    value_rating = 5
                elif away_team in elite_teams and home_team in weak_teams:
                    predicted_winner = away_team
                    confidence = 0.80
                    predicted_spread = 7.0
                    predicted_total = 47.0
                    value_rating = 4
                elif home_team in strong_teams and away_team in weak_teams:
                    predicted_winner = home_team
                    confidence = 0.75
                    predicted_spread = -5.5
                    predicted_total = 46.0
                    value_rating = 4
                elif away_team in strong_teams and home_team in weak_teams:
                    predicted_winner = away_team
                    confidence = 0.70
                    predicted_spread = 5.0
                    predicted_total = 45.5
                    value_rating = 3
                elif home_team in elite_teams:
                    predicted_winner = home_team
                    confidence = 0.65
                    predicted_spread = -3.5
                    predicted_total = 47.5
                    value_rating = 3
                elif away_team in elite_teams:
                    predicted_winner = away_team
                    confidence = 0.60
                    predicted_spread = 3.0
                    predicted_total = 46.5
                    value_rating = 2
                else:
                    predicted_winner = home_team  # Default to home team
                    confidence = 0.55
                    predicted_spread = -1.5
                    predicted_total = 45.0
                    value_rating = 1
                
                home_win_prob = confidence if predicted_winner == home_team else (1 - confidence)
                away_win_prob = 1 - home_win_prob
                
                # Enhanced betting recommendations
                if confidence > 0.75:
                    recommendation = f"BET {predicted_winner}"
                elif confidence > 0.65:
                    recommendation = f"LEAN {predicted_winner}"
                elif confidence > 0.55:
                    recommendation = f"SLIGHT LEAN {predicted_winner}"
                else:
                    recommendation = "NO BET"
                
                # Calculate edge vs line
                edge_vs_line = round(confidence - 0.5, 2)
                
                # Add updates for future games only
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
                    updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [["0"]]})
                if 'sharp_money' in col_indices:
                    col_letter = get_column_letter(col_indices['sharp_money'])
                    updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [["TBD"]]})
                if 'public_percentage' in col_indices:
                    col_letter = get_column_letter(col_indices['public_percentage'])
                    updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [["TBD"]]})
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
                print(f"  ✓ {away_team} @ {home_team}: {predicted_winner} ({confidence:.1%} confidence) - {recommendation}")
            
            else:
                # For completed games, check if prediction was correct
                actual_winner = ""
                if len(row) > 10 and len(row) > 7:  # Check if we have scores
                    home_score = row[9] if len(row) > 9 else ""
                    away_score = row[8] if len(row) > 8 else ""
                    
                    if home_score and away_score:
                        try:
                            home_score_num = float(home_score)
                            away_score_num = float(away_score)
                            actual_winner = home_team if home_score_num > away_score_num else away_team
                        except:
                            pass
                
                # Update prediction result for completed games
                if 'prediction_result' in col_indices and actual_winner:
                    col_letter = get_column_letter(col_indices['prediction_result'])
                    # Get the predicted winner from the sheet
                    predicted_winner = row[col_indices['predicted_winner']] if len(row) > col_indices['predicted_winner'] else ""
                    
                    if predicted_winner:
                        result_text = "WIN" if predicted_winner == actual_winner else "LOSS"
                        updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [[result_text]]})
    
    # Execute updates
    print(f"\n📝 Writing {predictions_made} predictions for {future_games} future games...")
    
    if updates:
        chunk_size = 100
        for i in range(0, len(updates), chunk_size):
            chunk = updates[i:i+chunk_size]
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'valueInputOption': 'USER_ENTERED', 'data': chunk}
            ).execute()
            print(f"  Updated chunk {i//chunk_size + 1}/{(len(updates)-1)//chunk_size + 1}")
    
    print("✅ Enhanced predictions successfully written!")
    print(f"\n📊 SUMMARY:")
    print(f"   - Future games predicted: {predictions_made}")
    print(f"   - Total future games: {future_games}")
    print(f"   - Added prediction_result column for wins/losses tracking")
    print(f"   - Predictions now only show for FUTURE games")

if __name__ == "__main__":
    main()



