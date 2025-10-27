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

def debug_team_names():
    """Debug team names in the actual data"""
    print("=" * 80)
    print("DEBUGGING TEAM NAMES")
    print("=" * 80)
    
    service = get_sheets_service()
    
    # Get game data for rows 111-122
    range_name = "upcoming_games!I111:K122"  # Away, Home teams
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    games_data = result.get('values', [])
    
    # Get predictions
    range_name2 = "upcoming_games!AV111:AX122"  # Winner predictions and confidence
    result2 = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name2).execute()
    predictions_data = result2.get('values', [])
    
    # High-performing teams (60%+ threshold)
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
    
    print("Raw data from sheet:")
    print("-" * 80)
    
    for i, (game_row, pred_row) in enumerate(zip(games_data, predictions_data)):
        row_number = 111 + i
        game = games[i] if i < len(games) else f"Game {row_number}"
        
        print(f"\nRow {row_number}: {game}")
        print(f"  Raw game data: {game_row}")
        print(f"  Raw prediction data: {pred_row}")
        
        if len(game_row) >= 2 and len(pred_row) >= 3:
            away_team = game_row[0] if len(game_row) > 0 else ""
            home_team = game_row[1] if len(game_row) > 1 else ""
            predicted_winner = pred_row[0] if len(pred_row) > 0 else ""
            winner_confidence = pred_row[2] if len(pred_row) > 2 else ""
            
            print(f"  Parsed: Away={away_team}, Home={home_team}, Winner={predicted_winner}, Conf={winner_confidence}")
            
            # Check if teams are in high performers
            print(f"  High performers check:")
            print(f"    {away_team} in high_performers: {away_team in high_performers}")
            print(f"    {home_team} in high_performers: {home_team in high_performers}")
            print(f"    {predicted_winner} in high_performers: {predicted_winner in high_performers}")
            
            # Check spread opportunities
            for team in [away_team, home_team]:
                if team in high_performers and team != predicted_winner:
                    stats = high_performers[team]
                    if team == home_team:
                        spread_type = "home"
                        spread_accuracy = stats['spread_home']
                    else:
                        spread_type = "away"
                        spread_accuracy = stats['spread_away']
                    
                    print(f"    *** {team} spread {spread_type}: {spread_accuracy}% ***")
                else:
                    print(f"    {team}: Not a spread opportunity")

if __name__ == "__main__":
    debug_team_names()

