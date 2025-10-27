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

def check_predictions_for_october_26():
    """Check predictions for 10/26/2025 games"""
    print("=" * 70)
    print("CHECKING PREDICTIONS FOR 10/26/2025 GAMES")
    print("=" * 70)
    
    service = get_sheets_service()
    
    # Get predictions for rows 111-122 (10/26/2025 games)
    range_name = "upcoming_games!AV111:AY122"  # Winner predictions and confidence
    
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = result.get('values', [])
    
    if not values:
        print("No prediction data found!")
        return
    
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
    
    # Game info
    games = [
        "MIA @ ATL", "CHI @ BAL", "BUF @ CAR", "NYJ @ CIN", "SF @ HOU",
        "CLE @ NE", "NYG @ PHI", "TB @ NO", "DAL @ DEN", "TEN @ IND",
        "GB @ PIT", "WAS @ KC"
    ]
    
    print("Predictions for 10/26/2025 games:")
    print("-" * 70)
    
    for i, row in enumerate(values):
        row_number = 111 + i
        game = games[i] if i < len(games) else f"Game {row_number}"
        
        predicted_winner = row[0] if len(row) > 0 else "N/A"  # AV column
        winner_confidence = row[2] if len(row) > 2 else "N/A"  # AX column
        
        print(f"Row {row_number}: {game}")
        print(f"  Predicted Winner: {predicted_winner}")
        print(f"  Winner Confidence: {winner_confidence}")
        
        # Check if predicted winner is a high performer
        if predicted_winner in high_performers:
            stats = high_performers[predicted_winner]
            print(f"  *** HIGH CONFIDENCE PICK ***")
            print(f"  {predicted_winner} Moneyline Accuracy: {stats['moneyline']}%")
            
            # Determine if it's home or away
            if " @ " in game:
                away_team, home_team = game.split(" @ ")
                if predicted_winner == home_team:
                    print(f"  {predicted_winner} Spread Home Accuracy: {stats['spread_home']}%")
                elif predicted_winner == away_team:
                    print(f"  {predicted_winner} Spread Away Accuracy: {stats['spread_away']}%")
        else:
            print(f"  {predicted_winner} not in high performers (70%+ threshold)")
        
        print()

if __name__ == "__main__":
    check_predictions_for_october_26()

