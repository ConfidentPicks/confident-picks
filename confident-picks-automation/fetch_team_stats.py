#!/usr/bin/env python3
"""Fetch Team Stats by Game"""
import sys
import json

try:
    import nflreadpy as nfl
except ImportError:
    print(json.dumps({"error": "nflreadpy not installed"}))
    sys.exit(1)

def fetch_team_stats(year):
    try:
        year = int(year)
        print(f"Fetching team stats for {year}...", file=sys.stderr)
        
        # Load schedules with team stats
        games = nfl.load_schedules(seasons=year)
        
        # Filter completed games only
        completed = games.filter(games['home_score'].is_not_null())
        
        stats_list = completed.to_dicts()
        print(f"Fetched {len(stats_list)} completed games", file=sys.stderr)
        return stats_list
        
    except Exception as e:
        print(json.dumps({"error": f"Error: {str(e)}"}))
        return []

if __name__ == "__main__":
    year = sys.argv[1] if len(sys.argv) > 1 else "2025"
    data = fetch_team_stats(year)
    print(json.dumps(data))



