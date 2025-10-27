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

def find_october_26_specific_rows():
    """Find games on 10/26/2025 in rows 111-122"""
    print("=" * 70)
    print("CHECKING ROWS 111-122 FOR 10/26/2025 GAMES")
    print("=" * 70)
    
    service = get_sheets_service()
    
    # Get specific rows 111-122
    range_name = "upcoming_games!A111:K122"  # Rows 111-122
    
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = result.get('values', [])
    
    if not values:
        print("No data found!")
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
    
    print("Checking rows 111-122:")
    print("-" * 70)
    
    october_26_games = []
    
    for i, row in enumerate(values):
        row_number = 111 + i  # Actual row number in sheet
        if len(row) >= 11:
            try:
                game_date = row[4] if len(row) > 4 else ""  # Column E
                home_team = row[9] if len(row) > 9 else ""  # Column J
                away_team = row[8] if len(row) > 8 else ""  # Column I
                
                print(f"Row {row_number}: Date={game_date}, Away={away_team}, Home={home_team}")
                
                # Check if this is 10/26/2025
                if "2025-10-26" in str(game_date) or "10/26/2025" in str(game_date) or "10-26-2025" in str(game_date):
                    home_performance = high_performers.get(home_team, {})
                    away_performance = high_performers.get(away_team, {})
                    
                    matchup_score = 0
                    if home_performance:
                        matchup_score += home_performance.get('moneyline', 0) + home_performance.get('spread_home', 0)
                    if away_performance:
                        matchup_score += away_performance.get('moneyline', 0) + away_performance.get('spread_away', 0)
                    
                    october_26_games.append({
                        'game': f"{away_team} @ {home_team}",
                        'date': game_date,
                        'home_team': home_team,
                        'away_team': away_team,
                        'home_stats': home_performance,
                        'away_stats': away_performance,
                        'score': matchup_score,
                        'row': row_number
                    })
                    
                    print(f"  *** FOUND 10/26 GAME: {away_team} @ {home_team} ***")
                    if home_performance:
                        print(f"  {home_team}: Moneyline {home_performance.get('moneyline', 0)}%, Spread Home {home_performance.get('spread_home', 0)}%")
                    if away_performance:
                        print(f"  {away_team}: Moneyline {away_performance.get('moneyline', 0)}%, Spread Away {away_performance.get('spread_away', 0)}%")
                    print()
                        
            except Exception as e:
                print(f"Row {row_number}: Error - {e}")
                continue
    
    if october_26_games:
        # Sort by matchup score
        october_26_games.sort(key=lambda x: x['score'], reverse=True)
        
        print("=" * 70)
        print("10/26/2025 GAMES RANKED BY PERFORMANCE")
        print("=" * 70)
        
        for i, matchup in enumerate(october_26_games):
            print(f"{i+1}. {matchup['game']} - Score: {matchup['score']}")
            print(f"   Row: {matchup['row']}, Date: {matchup['date']}")
            if matchup['home_stats']:
                print(f"   {matchup['home_team']}: Moneyline {matchup['home_stats'].get('moneyline', 0)}%, Spread Home {matchup['home_stats'].get('spread_home', 0)}%")
            if matchup['away_stats']:
                print(f"   {matchup['away_team']}: Moneyline {matchup['away_stats'].get('moneyline', 0)}%, Spread Away {matchup['away_stats'].get('spread_away', 0)}%")
            print()
    else:
        print("No 10/26/2025 games found in rows 111-122")

if __name__ == "__main__":
    find_october_26_specific_rows()

