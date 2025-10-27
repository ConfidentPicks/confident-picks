#!/usr/bin/env python3
"""
Fetch Full 2025 NFL Season Data
"""

import sys
import json
from datetime import datetime

try:
    import nflreadpy as nfl
except ImportError:
    print(json.dumps({"error": "nflreadpy not installed. Run: pip install nflreadpy"}))
    sys.exit(1)

def fetch_full_season():
    """Fetch all games for 2025 NFL season with all columns"""
    try:
        # Fetch all 2025 season games
        games = nfl.load_schedules(seasons=2025)
        
        # Convert to list of dictionaries using Polars methods
        games_list = games.to_dicts()
        
        print(f"Fetched {len(games_list)} games for 2025 season", file=sys.stderr)
        
        return games_list
        
    except Exception as e:
        print(json.dumps({"error": f"Error fetching season data: {str(e)}"}))
        return []

if __name__ == "__main__":
    try:
        season_data = fetch_full_season()
        print(json.dumps(season_data))
    except Exception as e:
        print(json.dumps({"error": f"Script error: {str(e)}"}))



