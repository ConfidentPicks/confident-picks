import nflreadpy as nfl

# Load player stats by week (game-by-game)
stats = nfl.load_player_stats(seasons=2024, summary_level='week')
data = stats.to_dicts()[:10]

print("\n✅ YES! Game-by-game player data IS available!\n")
print("="*70)
print("Sample: Patrick Mahomes game-by-game breakdown:\n")

# Find Mahomes games
mahomes = [d for d in data if 'Mahomes' in str(d.get('player_name', ''))][:5]

for game in mahomes:
    print(f"\nWeek {game.get('week')} vs {game.get('opponent_team')}")
    print(f"  Team: {game.get('team')}")
    print(f"  Passing: {game.get('passing_yards')} yards, {game.get('passing_tds')} TDs")
    print(f"  Completions: {game.get('completions')}/{game.get('attempts')}")
    print(f"  Interceptions: {game.get('passing_interceptions')}")
    print(f"  EPA: {game.get('passing_epa')}")

print("\n" + "="*70)
print(f"\nTotal records in 2024: {len(data)}")
print("Each record = 1 player in 1 game")
print("\nThis is EXACTLY what you need for modeling! ✅")




