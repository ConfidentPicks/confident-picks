#!/usr/bin/env python3
"""
Fetch Live NFL Odds using nflreadpy
"""

import sys
import json
import pandas as pd
from datetime import datetime, timedelta

try:
    import nflreadpy as nfl
except ImportError:
    print(json.dumps({"error": "nflreadpy not installed. Run: pip install nflreadpy"}))
    sys.exit(1)

def fetch_live_odds():
    """Fetch live NFL odds using nflreadpy"""
    try:
        # Get current season
        current_year = datetime.now().year
        if datetime.now().month < 9:  # Before September, use previous year
            current_year -= 1
        
        # Fetch current week's games using the correct nflreadpy API
        games = nfl.load_schedules(seasons=current_year)
        
        # Convert to pandas DataFrame for easier handling
        # Use a more compatible method
        try:
            games_df = games.to_pandas()
        except:
            # Fallback: convert to dict then to pandas
            games_df = pd.DataFrame(games.to_dict())
        
        # Filter for current week
        current_week = games_df[games_df['week'] == games_df['week'].max()]
        
        # Get odds data
        odds_data = []
        
        for _, game in current_week.iterrows():
            # Extract odds information - use safe column access
            game_data = {
                'game_id': str(game.get('game_id', '')),
                'home_team': str(game.get('home_team', '')),
                'away_team': str(game.get('away_team', '')),
                'game_date': str(game.get('gameday', '')) if pd.notna(game.get('gameday')) else '',
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
        
        return odds_data
        
    except Exception as e:
        print(json.dumps({"error": f"Error fetching live odds: {str(e)}"}))
        return []

if __name__ == "__main__":
    try:
        odds = fetch_live_odds()
        print(json.dumps(odds))
    except Exception as e:
        print(json.dumps({"error": f"Script error: {str(e)}"}))
