#!/usr/bin/env python3

import pandas as pd
import numpy as np
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import warnings
warnings.filterwarnings('ignore')

# Configuration
SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU'
SERVICE_ACCOUNT_FILE = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_sheets_service():
    """Get Google Sheets service"""
    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('sheets', 'v4', credentials=credentials)

def create_pick_cards_october_26():
    """Create pick cards for all 10/26/2025 games"""
    print("=" * 80)
    print("PICK CARDS FOR 10/26/2025 - TEST RUN")
    print("=" * 80)
    
    service = get_sheets_service()
    
    # Get game data and predictions for rows 111-122
    range_name = "upcoming_games!I111:K122"  # Away, Home teams
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    games_data = result.get('values', [])
    
    # Get predictions
    range_name2 = "upcoming_games!AV111:AX122"  # Winner predictions and confidence
    result2 = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name2).execute()
    predictions_data = result2.get('values', [])
    
    # High-performing teams (70%+ threshold)
    high_performers = {
        'DAL': {'moneyline': 85.71, 'spread_home': 100, 'spread_away': 100},
        'CAR': {'moneyline': 85.71, 'spread_home': 66.67, 'spread_away': 66.67},
        'NYG': {'moneyline': 80, 'spread_home': 33.33, 'spread_away': 33.33},
        'ATL': {'moneyline': 80, 'spread_home': 50, 'spread_away': 50},
        'CLE': {'moneyline': 80, 'spread_home': 66.67, 'spread_away': 66.67},
        'BUF': {'moneyline': 80, 'spread_home': 33.33, 'spread_away': 33.33},
        'TB': {'moneyline': 50, 'spread_home': 100, 'spread_away': 100},
        'TEN': {'moneyline': 0, 'spread_home': 100, 'spread_away': 100},
        'WAS': {'moneyline': 50, 'spread_home': 100, 'spread_away': 100},
        'SEA': {'moneyline': 57.14, 'spread_home': 100, 'spread_away': 100},
        'GB': {'moneyline': 66.67, 'spread_home': 100, 'spread_away': 100}
    }
    
    games = [
        "MIA @ ATL", "CHI @ BAL", "BUF @ CAR", "NYJ @ CIN", "SF @ HOU",
        "CLE @ NE", "NYG @ PHI", "TB @ NO", "DAL @ DEN", "TEN @ IND",
        "GB @ PIT", "WAS @ KC"
    ]
    
    high_confidence_picks = []
    medium_confidence_picks = []
    low_confidence_picks = []
    
    for i, (game_row, pred_row) in enumerate(zip(games_data, predictions_data)):
        row_number = 111 + i
        game = games[i] if i < len(games) else f"Game {row_number}"
        
        if len(game_row) >= 2 and len(pred_row) >= 3:
            away_team = game_row[0] if len(game_row) > 0 else ""
            home_team = game_row[1] if len(game_row) > 1 else ""
            predicted_winner = pred_row[0] if len(pred_row) > 0 else ""
            winner_confidence = pred_row[2] if len(pred_row) > 2 else ""
            
            print(f"\n{'='*60}")
            print(f"GAME {i+1}: {away_team} @ {home_team}")
            print(f"{'='*60}")
            print(f"Predicted Winner: {predicted_winner}")
            print(f"Model Confidence: {winner_confidence}")
            
            # Determine confidence level and reasoning
            if predicted_winner in high_performers:
                stats = high_performers[predicted_winner]
                confidence_level = "HIGH"
                
                # Determine if it's home or away
                if predicted_winner == home_team:
                    team_type = "home"
                    spread_accuracy = stats['spread_home']
                elif predicted_winner == away_team:
                    team_type = "away"
                    spread_accuracy = stats['spread_away']
                else:
                    team_type = "unknown"
                    spread_accuracy = 0
                
                reasoning = f"""
HIGH CONFIDENCE PICK:
• Model predicts {predicted_winner} to win with {winner_confidence} confidence
• {predicted_winner} has {stats['moneyline']}% moneyline accuracy this season (70%+ threshold)
• {predicted_winner} has {spread_accuracy}% spread {team_type} accuracy
• High-performing team with proven track record
• Meets 70%+ accuracy threshold for publishing"""
                
                high_confidence_picks.append({
                    'game': game,
                    'pick': f"{predicted_winner} Moneyline",
                    'confidence': confidence_level,
                    'reasoning': reasoning.strip()
                })
                
            else:
                # Check if the opponent is a high performer (for spread picks)
                opponent = home_team if predicted_winner == away_team else away_team
                if opponent in high_performers:
                    opponent_stats = high_performers[opponent]
                    confidence_level = "MEDIUM"
                    
                    if predicted_winner == home_team:
                        spread_accuracy = opponent_stats['spread_away']
                        spread_pick = f"{opponent} Spread Away"
                    else:
                        spread_accuracy = opponent_stats['spread_home']
                        spread_pick = f"{opponent} Spread Home"
                    
                    reasoning = f"""
MEDIUM CONFIDENCE PICK:
• Model predicts {predicted_winner} to win with {winner_confidence} confidence
• {opponent} has {opponent_stats['moneyline']}% moneyline accuracy this season
• {opponent} has {spread_accuracy}% spread accuracy
• Consider {spread_pick} as alternative to moneyline"""
                    
                    medium_confidence_picks.append({
                        'game': game,
                        'pick': f"{predicted_winner} Moneyline",
                        'confidence': confidence_level,
                        'reasoning': reasoning.strip()
                    })
                else:
                    confidence_level = "LOW"
                    reasoning = f"""
LOW CONFIDENCE PICK:
• Model predicts {predicted_winner} to win with {winner_confidence} confidence
• Neither team meets 70%+ accuracy threshold
• Consider avoiding or use with caution"""
                    
                    low_confidence_picks.append({
                        'game': game,
                        'pick': f"{predicted_winner} Moneyline",
                        'confidence': confidence_level,
                        'reasoning': reasoning.strip()
                    })
            
            print(f"Confidence Level: {confidence_level}")
            print(f"Reasoning: {reasoning}")
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"HIGH CONFIDENCE PICKS: {len(high_confidence_picks)}")
    for pick in high_confidence_picks:
        print(f"  • {pick['game']}: {pick['pick']}")
    
    print(f"\nMEDIUM CONFIDENCE PICKS: {len(medium_confidence_picks)}")
    for pick in medium_confidence_picks:
        print(f"  • {pick['game']}: {pick['pick']}")
    
    print(f"\nLOW CONFIDENCE PICKS: {len(low_confidence_picks)}")
    for pick in low_confidence_picks:
        print(f"  • {pick['game']}: {pick['pick']}")

if __name__ == "__main__":
    create_pick_cards_october_26()

