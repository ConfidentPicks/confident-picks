#!/usr/bin/env python3
"""
Fetch Historical NFL Data using nflreadpy
"""

import sys
import json
import pandas as pd
from datetime import datetime

try:
    import nflreadpy as nfl
except ImportError:
    print("Error: nflreadpy not installed. Run: pip install nflreadpy")
    sys.exit(1)

def fetch_historical_data(years, data_type='games'):
    """Fetch historical NFL data using nflreadpy"""
    try:
        all_data = []
        
        for year in years:
            year = int(year)
            print(f"Fetching {data_type} data for {year}...")
            
            if data_type == 'games':
                # Fetch game data
                games = nfl.read_schedules(year=year)
                
                for _, game in games.iterrows():
                    game_data = {
                        'game_id': game.get('game_id', ''),
                        'season': game.get('season', ''),
                        'week': game.get('week', ''),
                        'game_date': game.get('gameday', '').strftime('%Y-%m-%d %H:%M:%S') if pd.notna(game.get('gameday')) else '',
                        'home_team': game.get('home_team', ''),
                        'away_team': game.get('away_team', ''),
                        'home_score': game.get('home_score', ''),
                        'away_score': game.get('away_score', ''),
                        'spread': game.get('spread_line', ''),
                        'total': game.get('total_line', ''),
                        'home_moneyline': game.get('home_moneyline', ''),
                        'away_moneyline': game.get('away_moneyline', ''),
                        'home_yards': game.get('home_yards', ''),
                        'away_yards': game.get('away_yards', ''),
                        'home_turnovers': game.get('home_turnovers', ''),
                        'away_turnovers': game.get('away_turnovers', '')
                    }
                    
                    all_data.append(game_data)
                    
            elif data_type == 'team_stats':
                # Fetch team stats
                team_stats = nfl.read_team_desc(year=year)
                
                for _, team in team_stats.iterrows():
                    team_data = {
                        'team': team.get('team', ''),
                        'season': team.get('season', ''),
                        'games': team.get('games', ''),
                        'wins': team.get('wins', ''),
                        'losses': team.get('losses', ''),
                        'ties': team.get('ties', ''),
                        'points_for': team.get('points_for', ''),
                        'points_against': team.get('points_against', ''),
                        'passing_yards': team.get('passing_yards', ''),
                        'rushing_yards': team.get('rushing_yards', ''),
                        'total_yards': team.get('total_yards', ''),
                        'passing_touchdowns': team.get('passing_touchdowns', ''),
                        'rushing_touchdowns': team.get('rushing_touchdowns', ''),
                        'total_touchdowns': team.get('total_touchdowns', ''),
                        'interceptions': team.get('interceptions', ''),
                        'fumbles': team.get('fumbles', ''),
                        'sacks': team.get('sacks', ''),
                        'turnovers': team.get('turnovers', '')
                    }
                    
                    all_data.append(team_data)
        
        return all_data
        
    except Exception as e:
        print(f"Error fetching historical data: {str(e)}")
        return []

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fetch_historical_data.py <year1> [year2] [year3] [year4] [data_type]")
        sys.exit(1)
    
    years = sys.argv[1:-1] if len(sys.argv) > 2 else [sys.argv[1]]
    data_type = sys.argv[-1] if sys.argv[-1] in ['games', 'team_stats'] else 'games'
    
    data = fetch_historical_data(years, data_type)
    print(json.dumps(data))



