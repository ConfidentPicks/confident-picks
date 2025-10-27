#!/usr/bin/env python3
"""
Fetch Active NFL Players Only
"""

import sys
import json

try:
    import nflreadpy as nfl
except ImportError:
    print(json.dumps({"error": "nflreadpy not installed. Run: pip install nflreadpy"}))
    sys.exit(1)

def fetch_active_players():
    """Fetch only active NFL players"""
    try:
        # Fetch all player data
        players = nfl.load_players()
        
        # Filter for active players only (status == 'ACT' or similar)
        # Also filter for players with a latest_team (currently on a roster)
        active_players = players.filter(
            (players['status'] == 'ACT') | 
            (players['ngs_status'] == 'Active')
        )
        
        # Further filter to only include players with a current team
        active_players = active_players.filter(
            players['latest_team'].is_not_null()
        )
        
        # Convert to list of dictionaries
        players_list = active_players.to_dicts()
        
        print(f"Fetched {len(players_list)} active players", file=sys.stderr)
        
        return players_list
        
    except Exception as e:
        # If filtering fails, just get all recent players
        try:
            print(f"Filter error, trying alternative method: {str(e)}", file=sys.stderr)
            players = nfl.load_players()
            
            # Get players from last season or current season
            recent_players = players.filter(
                (players['last_season'] >= 2024) & 
                (players['latest_team'].is_not_null())
            )
            
            players_list = recent_players.to_dicts()
            print(f"Fetched {len(players_list)} recent players", file=sys.stderr)
            return players_list
        except Exception as e2:
            print(json.dumps({"error": f"Error fetching active players: {str(e2)}"}))
            return []

if __name__ == "__main__":
    try:
        player_data = fetch_active_players()
        print(json.dumps(player_data))
    except Exception as e:
        print(json.dumps({"error": f"Script error: {str(e)}"}))



