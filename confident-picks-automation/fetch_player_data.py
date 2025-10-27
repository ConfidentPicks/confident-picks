#!/usr/bin/env python3
"""
Fetch NFL Player Data using nflreadpy
"""

import sys
import json

try:
    import nflreadpy as nfl
except ImportError:
    print(json.dumps({"error": "nflreadpy not installed. Run: pip install nflreadpy"}))
    sys.exit(1)

def fetch_player_data():
    """Fetch all NFL player data"""
    try:
        # Fetch all player data
        players = nfl.load_players()
        
        # Convert to list of dictionaries using Polars methods
        players_list = players.to_dicts()
        
        print(f"Fetched {len(players_list)} players", file=sys.stderr)
        
        return players_list
        
    except Exception as e:
        print(json.dumps({"error": f"Error fetching player data: {str(e)}"}))
        return []

if __name__ == "__main__":
    try:
        player_data = fetch_player_data()
        print(json.dumps(player_data))
    except Exception as e:
        print(json.dumps({"error": f"Script error: {str(e)}"}))



