#!/usr/bin/env python3
"""
Fetch Historical Player Stats by Game (2021-Current)
"""

import sys
import json

try:
    import nflreadpy as nfl
except ImportError:
    print(json.dumps({"error": "nflreadpy not installed. Run: pip install nflreadpy"}))
    sys.exit(1)

def fetch_historical_stats(years):
    """Fetch player stats by game for multiple years"""
    try:
        # Convert years to integers
        years = [int(y) for y in years]
        
        print(f"Fetching player stats for years: {years}", file=sys.stderr)
        
        # Fetch weekly player stats for all years
        stats = nfl.load_player_stats(seasons=years, summary_level='week')
        
        # Convert to list of dictionaries
        stats_list = stats.to_dicts()
        
        print(f"Fetched {len(stats_list)} player game records", file=sys.stderr)
        
        return stats_list
        
    except Exception as e:
        print(json.dumps({"error": f"Error fetching stats: {str(e)}"}))
        return []

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fetch_historical_stats.py <year1> [year2] [year3] ...")
        sys.exit(1)
    
    years = sys.argv[1:]
    stats_data = fetch_historical_stats(years)
    print(json.dumps(stats_data))



