#!/usr/bin/env python3
"""
Simple NFL Data Fetcher - No pyarrow required
"""

import sys
import json
from datetime import datetime

try:
    import nflreadpy as nfl
except ImportError:
    print(json.dumps({"error": "nflreadpy not installed. Run: pip install nflreadpy"}))
    sys.exit(1)

def fetch_live_odds():
    """Fetch live NFL odds using nflreadpy - simplified version"""
    try:
        # Get current season
        current_year = datetime.now().year
        if datetime.now().month < 9:  # Before September, use previous year
            current_year -= 1
        
        # Fetch current week's games using the correct nflreadpy API
        games = nfl.load_schedules(seasons=current_year)
        
        # Convert to list of dictionaries using Polars methods
        games_list = games.to_dicts()
        
        # Extract odds information for each game
        odds_data = []
        for game in games_list:
            game_data = {
                'game_id': str(game.get('game_id', '')),
                'home_team': str(game.get('home_team', '')),
                'away_team': str(game.get('away_team', '')),
                'game_date': str(game.get('gameday', '')),
                'home_score': str(game.get('home_score', '')),
                'away_score': str(game.get('away_score', '')),
                'spread': str(game.get('spread_line', '')),
                'spread_odds': str(game.get('spread_odds', '')),
                'total': str(game.get('total_line', '')),
                'total_odds': str(game.get('total_odds', '')),
                'home_moneyline': str(game.get('home_moneyline', '')),
                'away_moneyline': str(game.get('away_moneyline', ''))
            }
            
            odds_data.append(game_data)
        
        # Filter for current week (last few games)
        current_week_games = odds_data[-16:]  # Get last 16 games (roughly current week)
        
        return current_week_games
        
    except Exception as e:
        print(json.dumps({"error": f"Error fetching live odds: {str(e)}"}))
        return []

if __name__ == "__main__":
    try:
        odds = fetch_live_odds()
        print(json.dumps(odds))
    except Exception as e:
        print(json.dumps({"error": f"Script error: {str(e)}"}))
