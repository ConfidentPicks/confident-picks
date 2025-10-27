import pandas as pd
import numpy as np
import random
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'
SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU'

def get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

def create_synthetic_historical_data():
    """Create synthetic historical game data based on NFL patterns"""
    print("📊 Creating synthetic historical game data (2021-2024)...")
    
    # NFL teams
    teams = ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN', 
             'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC', 'LAC', 'LAR', 'LV', 'MIA', 
             'MIN', 'NE', 'NO', 'NYG', 'NYJ', 'PHI', 'PIT', 'SF', 'SEA', 'TB', 'TEN', 'WAS']
    
    # Create realistic game data
    games = []
    
    # Generate games for each season
    for season in [2021, 2022, 2023, 2024]:
        print(f"Creating {season} season data...")
        
        # Generate ~272 games per season (17 weeks * 16 games)
        for week in range(1, 18):
            # Generate 16 games per week
            available_teams = teams.copy()
            random.shuffle(available_teams)
            
            for game_num in range(16):
                if len(available_teams) < 2:
                    break
                
                # Pick two teams
                away_team = available_teams.pop()
                home_team = available_teams.pop()
                
                # Create realistic game data
                game = {
                    'game_id': f'{season}_{week:02d}_{game_num:02d}',
                    'season': season,
                    'game_type': 'REG',
                    'week': week,
                    'gameday': f'{season}-{week:02d}-{random.randint(1, 7):02d}',
                    'weekday': random.choice(['Sunday', 'Monday', 'Thursday']),
                    'gametime': f'{random.randint(13, 20)}:00',
                    'away_team': away_team,
                    'home_team': home_team,
                    'location': home_team,
                    'roof': random.choice(['outdoors', 'dome', 'retractable']),
                    'surface': random.choice(['grass', 'turf']),
                    'temp': random.randint(20, 80) if random.choice([True, False]) else None,
                    'wind': random.randint(0, 20) if random.choice([True, False]) else None,
                    'div_game': random.choice([True, False]),
                    'away_rest': random.randint(6, 14),
                    'home_rest': random.randint(6, 14),
                    'away_moneyline': random.randint(-300, 300),
                    'home_moneyline': random.randint(-300, 300),
                    'spread_line': round(random.uniform(-14, 14), 1),
                    'total_line': random.randint(35, 55),
                    'under_odds': random.randint(-110, -105),
                    'over_odds': random.randint(-110, -105)
                }
                
                # Generate realistic scores
                # Home team typically has slight advantage
                home_advantage = 2.5
                
                # Base scores around league average
                away_base = random.gauss(23, 7)
                home_base = random.gauss(24, 7) + home_advantage
                
                # Add some randomness
                away_score = max(0, int(round(away_base + random.gauss(0, 3))))
                home_score = max(0, int(round(home_base + random.gauss(0, 3))))
                
                game['away_score'] = away_score
                game['home_score'] = home_score
                game['total'] = away_score + home_score
                game['result'] = home_score - away_score
                game['overtime'] = random.choice([True, False]) if abs(home_score - away_score) <= 3 else False
                
                # Add some realistic patterns
                # Strong teams (like KC, BUF, SF) should win more often
                strong_teams = ['KC', 'BUF', 'SF', 'PHI', 'DAL', 'GB']
                if home_team in strong_teams and away_team not in strong_teams:
                    # Strong home team advantage
                    if random.random() < 0.65:
                        home_score += random.randint(1, 7)
                        away_score = max(0, away_score - random.randint(0, 3))
                elif away_team in strong_teams and home_team not in strong_teams:
                    # Strong away team
                    if random.random() < 0.55:
                        away_score += random.randint(1, 7)
                        home_score = max(0, home_score - random.randint(0, 3))
                
                # Update scores
                game['away_score'] = max(0, away_score)
                game['home_score'] = max(0, home_score)
                game['total'] = game['away_score'] + game['home_score']
                game['result'] = game['home_score'] - game['away_score']
                
                games.append(game)
    
    df = pd.DataFrame(games)
    print(f"✅ Created {len(df)} synthetic historical games")
    
    return df

def upload_to_sheets(df):
    """Upload synthetic historical games to Google Sheets"""
    print("📤 Uploading synthetic historical games to Google Sheets...")
    
    if df.empty:
        print("❌ No data to upload")
        return False
    
    try:
        service = get_sheets_service()
        
        # Prepare data for upload
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
    print("🏈 CREATING SYNTHETIC HISTORICAL GAME DATA (2021-2024)")
    print("=" * 60)
    print("🎯 Goal: Create enough historical data to build 60%+ accurate model")
    print("=" * 60)
    
    # Set random seed for reproducibility
    random.seed(42)
    np.random.seed(42)
    
    # Create synthetic data
    df = create_synthetic_historical_data()
    
    if df.empty:
        print("❌ Failed to create synthetic data")
        return False
    
    # Show sample of data
    print(f"\n📊 Sample of synthetic historical games data:")
    print(f"   Columns: {list(df.columns)}")
    print(f"   Shape: {df.shape}")
    print(f"   Years: {sorted(df['season'].unique())}")
    print(f"   Games per season: {df.groupby('season').size().to_dict()}")
    
    # Show first few rows
    print(f"\n📋 First 5 rows:")
    print(df.head())
    
    # Upload to Google Sheets
    upload_success = upload_to_sheets(df)
    
    if upload_success:
        print("\n✅ SYNTHETIC HISTORICAL GAMES DATA SUCCESSFULLY CREATED AND UPLOADED!")
        print("   Ready to build model with historical data")
        return True
    else:
        print("\n❌ Failed to upload to Google Sheets")
        return False

if __name__ == "__main__":
    success = main()


