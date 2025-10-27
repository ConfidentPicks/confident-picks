import pandas as pd
import numpy as np
import subprocess
import sys
import os

def fetch_historical_games():
    """Fetch 2021-2024 game data using nflreadpy"""
    print("📊 Fetching 2021-2024 game data using nflreadpy...")
    
    # Create a simple Python script without emojis
    python_script = '''
import nfl_data_py as nfl
import pandas as pd
import json

def fetch_historical_games():
    print("Fetching historical game data...")
    
    # Fetch games for 2021-2024
    all_games = []
    
    for year in [2021, 2022, 2023, 2024]:
        print(f"Fetching {year} games...")
        try:
            games = nfl.import_schedules([year])
            if not games.empty:
                games['season'] = year
                all_games.append(games)
                print(f"Found {len(games)} games for {year}")
            else:
                print(f"No games found for {year}")
        except Exception as e:
            print(f"Error fetching {year} games: {e}")
    
    if all_games:
        combined_games = pd.concat(all_games, ignore_index=True)
        print(f"Total games collected: {len(combined_games)}")
        
        # Save to JSON for processing
        games_json = combined_games.to_json(orient='records')
        with open('historical_games.json', 'w') as f:
            f.write(games_json)
        
        print("Historical games saved to historical_games.json")
        return len(combined_games)
    else:
        print("No games collected")
        return 0

if __name__ == "__main__":
    fetch_historical_games()
'''
    
    # Write Python script to file
    with open('temp_fetch_games.py', 'w', encoding='utf-8') as f:
        f.write(python_script)
    
    # Run the Python script
    try:
        result = subprocess.run([sys.executable, 'temp_fetch_games.py'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        # Check if historical_games.json was created
        if os.path.exists('historical_games.json'):
            print("✅ Historical games data fetched successfully!")
            return True
        else:
            print("❌ Failed to fetch historical games data")
            return False
            
    except Exception as e:
        print(f"❌ Error running fetch script: {e}")
        return False
    finally:
        # Clean up temp file
        if os.path.exists('temp_fetch_games.py'):
            os.remove('temp_fetch_games.py')

def load_historical_games():
    """Load the fetched historical games data"""
    print("📊 Loading historical games data...")
    
    try:
        with open('historical_games.json', 'r') as f:
            games_data = f.read()
        
        # Parse JSON and convert to DataFrame
        import json
        games_list = json.loads(games_data)
        df = pd.DataFrame(games_list)
        
        print(f"✅ Loaded {len(df)} historical games")
        return df
        
    except Exception as e:
        print(f"❌ Error loading historical games: {e}")
        return pd.DataFrame()

def main():
    print("🏈 FETCHING HISTORICAL GAME DATA (2021-2024)")
    print("=" * 60)
    print("🎯 Goal: Get enough historical data to build 60%+ accurate model")
    print("=" * 60)
    
    # Fetch historical games
    success = fetch_historical_games()
    
    if not success:
        print("❌ Failed to fetch historical games")
        return False
    
    # Load the data
    df = load_historical_games()
    
    if df.empty:
        print("❌ No historical games data loaded")
        return False
    
    # Show sample of data
    print(f"\n📊 Sample of historical games data:")
    print(f"   Columns: {list(df.columns)}")
    print(f"   Shape: {df.shape}")
    if 'season' in df.columns:
        print(f"   Years: {sorted(df['season'].unique())}")
    
    # Show first few rows
    print(f"\n📋 First 5 rows:")
    print(df.head())
    
    print("\n✅ HISTORICAL GAMES DATA SUCCESSFULLY FETCHED!")
    print("   Ready to build model with historical data")
    return True

if __name__ == "__main__":
    success = main()


