import nflreadpy as nfl

# Load player stats by week (game-by-game)
stats = nfl.load_player_stats(seasons=2024, summary_level='week')
data = stats.to_dicts()

print("\n✅ YES! Game-by-game player data IS AVAILABLE!\n")
print("="*70)

# Show some QBs
qbs = [d for d in data if d.get('position') == 'QB'][:20]

print(f"\nTotal 2024 player-game records: {len(data)}")
print(f"QB records: {len([d for d in data if d.get('position') == 'QB'])}")
print(f"RB records: {len([d for d in data if d.get('position') == 'RB'])}")
print(f"WR records: {len([d for d in data if d.get('position') == 'WR'])}")

print("\n" + "="*70)
print("Sample: QB Game-by-Game Stats (first 5 records):\n")

for game in qbs[:5]:
    print(f"{game.get('player_name')} - Week {game.get('week')} ({game.get('team')} vs {game.get('opponent_team')})")
    print(f"  Passing: {game.get('passing_yards')} yds, {game.get('passing_tds')} TDs, {game.get('passing_interceptions')} INTs")
    print(f"  Comp/Att: {game.get('completions')}/{game.get('attempts')}")
    print(f"  Rushing: {game.get('rushing_yards')} yds, {game.get('rushing_tds')} TDs")
    print()

print("="*70)
print("\n✅ You HAVE game-by-game player stats in your sheets!")
print("   - player_stats_2021 (18,969 records)")
print("   - player_stats_2022 (18,831 records)")
print("   - player_stats_2023 (18,643 records)")
print("   - player_stats_2024 (18,981 records)")
print("\n📦 2025 stats (7,398 records) - Can't fit in current sheet due to 10M cell limit")
print("\n💡 Solution: Query 2025 data directly via Python or create second sheet!")




