#!/usr/bin/env python3
"""Fetch Game Results (completed games with outcomes)"""
import sys
import json

try:
    import nflreadpy as nfl
except ImportError:
    print(json.dumps({"error": "nflreadpy not installed"}))
    sys.exit(1)

def fetch_game_results(year):
    try:
        year = int(year)
        print(f"Fetching game results for {year}...", file=sys.stderr)
        
        # Load completed games
        games = nfl.load_schedules(seasons=year)
        completed = games.filter(games['home_score'].is_not_null())
        
        # Extract relevant columns for model building
        results = []
        for game in completed.to_dicts():
            results.append({
                'game_id': game.get('game_id', ''),
                'season': game.get('season', ''),
                'week': game.get('week', ''),
                'game_type': game.get('game_type', ''),
                'gameday': game.get('gameday', ''),
                'away_team': game.get('away_team', ''),
                'home_team': game.get('home_team', ''),
                'away_score': game.get('away_score', ''),
                'home_score': game.get('home_score', ''),
                'result': game.get('result', ''),
                'total': game.get('total', ''),
                'overtime': game.get('overtime', ''),
                'spread_line': game.get('spread_line', ''),
                'total_line': game.get('total_line', ''),
                'away_moneyline': game.get('away_moneyline', ''),
                'home_moneyline': game.get('home_moneyline', ''),
                'location': game.get('location', ''),
                'roof': game.get('roof', ''),
                'surface': game.get('surface', ''),
                'temp': game.get('temp', ''),
                'wind': game.get('wind', ''),
                'away_rest': game.get('away_rest', ''),
                'home_rest': game.get('home_rest', ''),
                'away_coach': game.get('away_coach', ''),
                'home_coach': game.get('home_coach', ''),
                'referee': game.get('referee', ''),
                'stadium': game.get('stadium', '')
            })
        
        print(f"Fetched {len(results)} game results", file=sys.stderr)
        return results
        
    except Exception as e:
        print(json.dumps({"error": f"Error: {str(e)}"}))
        return []

if __name__ == "__main__":
    year = sys.argv[1] if len(sys.argv) > 1 else "2025"
    data = fetch_game_results(year)
    print(json.dumps(data))



