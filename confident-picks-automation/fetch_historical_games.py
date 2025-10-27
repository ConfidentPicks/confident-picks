import pandas as pd
import numpy as np
from google.oauth2 import service_account
from googleapiclient.discovery import build
import subprocess
import sys
import os

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'
SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU'

def get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

def fetch_historical_games():
    """Fetch 2021-2024 game data using nflreadpy"""
    print("📊 Fetching 2021-2024 game data using nflreadpy...")
    
    # Create Python script to fetch historical games
    python_script = '''
import nfl_data_py as nfl
import pandas as pd
import json

def fetch_historical_games():
    print("🔍 Fetching historical game data...")
    
    # Fetch games for 2021-2024
    all_games = []
    
    for year in [2021, 2022, 2023, 2024]:
        print(f"📅 Fetching {year} games...")
        try:
            games = nfl.import_schedules([year])
            if not games.empty:
                games['season'] = year
                all_games.append(games)
                print(f"✅ Found {len(games)} games for {year}")
            else:
                print(f"❌ No games found for {year}")
        except Exception as e:
            print(f"❌ Error fetching {year} games: {e}")
    
    if all_games:
        combined_games = pd.concat(all_games, ignore_index=True)
        print(f"✅ Total games collected: {len(combined_games)}")
        
        # Save to JSON for processing
        games_json = combined_games.to_json(orient='records')
        with open('historical_games.json', 'w') as f:
            f.write(games_json)
        
        print("✅ Historical games saved to historical_games.json")
        return len(combined_games)
    else:
        print("❌ No games collected")
        return 0

if __name__ == "__main__":
    fetch_historical_games()
'''
    
    # Write Python script to file
    with open('temp_fetch_games.py', 'w') as f:
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

def upload_to_sheets(df):
    """Upload historical games to Google Sheets"""
    print("📤 Uploading historical games to Google Sheets...")
    
    if df.empty:
        print("❌ No data to upload")
        return False
    
    try:
        service = get_sheets_service()
        
        # Prepare data for upload
        # Convert DataFrame to list of lists
        headers = df.columns.tolist()
        values = [headers] + df.values.tolist()
        
        # Clear existing data and upload new data
        range_name = 'historical_game_results_2021_2024!A:ZZ'
        
        # Clear the sheet first
        service.spreadsheets().values().clear(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name
        ).execute()
        
        # Upload new data
        body = {
            'values': values
        }
        
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        print(f"✅ Uploaded {len(df)} games to historical_game_results_2021_2024 sheet")
        return True
        
    except Exception as e:
        print(f"❌ Error uploading to sheets: {e}")
        return False

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
    print(f"   Years: {sorted(df['season'].unique()) if 'season' in df.columns else 'Unknown'}")
    
    # Upload to Google Sheets
    upload_success = upload_to_sheets(df)
    
    if upload_success:
        print("\n✅ HISTORICAL GAMES DATA SUCCESSFULLY FETCHED AND UPLOADED!")
        print("   Ready to build model with historical data")
        return True
    else:
        print("\n❌ Failed to upload to Google Sheets")
        return False

if __name__ == "__main__":
    success = main()


