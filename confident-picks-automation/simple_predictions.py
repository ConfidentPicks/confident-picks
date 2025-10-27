#!/usr/bin/env python3

"""
Simple Predictions Script
========================

This script adds predictions to the upcoming_games tab in a simple way
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Google Sheets integration
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ML Libraries
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import xgboost as xgb

# Data processing
from datetime import datetime

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
    
    print("🏈 Simple NFL Predictions")
    print("=" * 40)
    
    # Load historical data
    print("📊 Loading historical data...")
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="historical_game_results_2021_2024!A:ZZ"
    ).execute()
    
    values = result.get('values', [])
    if not values:
        print("❌ No historical data found")
        return
    
    # Convert to DataFrame
    headers = values[0]
    data_rows = []
    for row in values[1:]:
        padded_row = row + [''] * (len(headers) - len(row))
        data_rows.append(padded_row)
    
    games_df = pd.DataFrame(data_rows, columns=headers)
    print(f"✅ Loaded {len(games_df)} historical games")
    
    # Simple team strength calculation
    print("📊 Calculating team strengths...")
    team_strengths = {}
    all_teams = set(games_df['home_team'].unique()) | set(games_df['away_team'].unique())
    
    for team in all_teams:
        team_games = games_df[(games_df['home_team'] == team) | (games_df['away_team'] == team)]
        if len(team_games) > 0:
            wins = 0
            total_games = len(team_games)
            for _, game in team_games.iterrows():
                home_score = pd.to_numeric(game['home_score'], errors='coerce')
                away_score = pd.to_numeric(game['away_score'], errors='coerce')
                if not pd.isna(home_score) and not pd.isna(away_score):
                    if game['home_team'] == team and home_score > away_score:
                        wins += 1
                    elif game['away_team'] == team and away_score > home_score:
                        wins += 1
            win_pct = wins / total_games if total_games > 0 else 0.5
            team_strengths[team] = max(0.1, min(0.9, win_pct))
        else:
            team_strengths[team] = 0.5
    
    print(f"✅ Calculated strengths for {len(team_strengths)} teams")
    
    # Load upcoming games
    print("🔮 Loading upcoming games...")
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="upcoming_games!A:ZZ"
    ).execute()
    
    values = result.get('values', [])
    if not values:
        print("❌ No upcoming games found")
        return
    
    headers = values[0]
    data_rows = []
    for row in values[1:]:
        padded_row = row + [''] * (len(headers) - len(row))
        data_rows.append(padded_row)
    
    upcoming_df = pd.DataFrame(data_rows, columns=headers)
    print(f"✅ Loaded {len(upcoming_df)} upcoming games")
    
    # Make simple predictions
    print("🎯 Making predictions...")
    
    predictions = []
    for idx, game in upcoming_df.iterrows():
        home_team = game.get('home_team', '')
        away_team = game.get('away_team', '')
        
        # Skip games with results already
        if game.get('result', '') != '' and game.get('result', '') != '0':
            continue
        
        # Simple prediction based on team strength
        home_strength = team_strengths.get(home_team, 0.5)
        away_strength = team_strengths.get(away_team, 0.5)
        
        # Add home field advantage
        home_advantage = 0.05
        home_win_prob = (home_strength + home_advantage) / (home_strength + away_strength + home_advantage)
        away_win_prob = 1 - home_win_prob
        
        predicted_winner = home_team if home_win_prob > 0.5 else away_team
        confidence = max(home_win_prob, away_win_prob)
        
        # Simple betting recommendation
        if confidence > 0.65:
            recommendation = f"BET {predicted_winner}"
        else:
            recommendation = "NO BET"
        
        predictions.append({
            'row': idx + 2,  # +2 because row 1 is headers
            'predicted_winner': predicted_winner,
            'confidence_score': round(confidence, 3),
            'home_win_probability': round(home_win_prob, 3),
            'away_win_probability': round(away_win_prob, 3),
            'betting_recommendation': recommendation,
            'betting_value': round(confidence - 0.5, 3),
            'model_last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        print(f"  ✓ {away_team} @ {home_team}: {predicted_winner} ({confidence:.1%} confidence)")
    
    # Update the sheet with predictions
    print(f"\n📝 Writing {len(predictions)} predictions to sheet...")
    
    # Find column indices
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
    
    print(f"Found columns: {col_indices}")
    
    # Update predictions
    updates = []
    for pred in predictions:
        row_num = pred['row']
        
        for col_name, col_idx in col_indices.items():
            if col_name == 'predicted_winner':
                updates.append({'range': f"upcoming_games!{chr(65+col_idx)}{row_num}", 'values': [[pred['predicted_winner']]]})
            elif col_name == 'confidence_score':
                updates.append({'range': f"upcoming_games!{chr(65+col_idx)}{row_num}", 'values': [[pred['confidence_score']]]})
            elif col_name == 'home_win_probability':
                updates.append({'range': f"upcoming_games!{chr(65+col_idx)}{row_num}", 'values': [[pred['home_win_probability']]]})
            elif col_name == 'away_win_probability':
                updates.append({'range': f"upcoming_games!{chr(65+col_idx)}{row_num}", 'values': [[pred['away_win_probability']]]})
            elif col_name == 'betting_recommendation':
                updates.append({'range': f"upcoming_games!{chr(65+col_idx)}{row_num}", 'values': [[pred['betting_recommendation']]]})
            elif col_name == 'betting_value':
                updates.append({'range': f"upcoming_games!{chr(65+col_idx)}{row_num}", 'values': [[pred['betting_value']]]})
            elif col_name == 'model_last_updated':
                updates.append({'range': f"upcoming_games!{chr(65+col_idx)}{row_num}", 'values': [[pred['model_last_updated']]]})
    
    # Execute updates in chunks
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

if __name__ == "__main__":
    main()



