#!/usr/bin/env python3
"""Populate NHL upcoming_games tab with today's games"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests
from datetime import datetime, timedelta
import pytz

SERVICE_ACCOUNT_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
NHL_SHEET_ID = '1Hel-NsCxmk07nM0AH4VkJFB9hSK23X7XOxtA4wyRNRo'
ODDS_API_KEY = 'b68d307ccf8519e69cbdea629b175b08'

# NHL team name to abbreviation mapping
NHL_TEAM_MAP = {
    'Anaheim Ducks': 'ANA',
    'Arizona Coyotes': 'ARI',
    'Boston Bruins': 'BOS',
    'Buffalo Sabres': 'BUF',
    'Calgary Flames': 'CGY',
    'Carolina Hurricanes': 'CAR',
    'Chicago Blackhawks': 'CHI',
    'Colorado Avalanche': 'COL',
    'Columbus Blue Jackets': 'CBJ',
    'Dallas Stars': 'DAL',
    'Detroit Red Wings': 'DET',
    'Edmonton Oilers': 'EDM',
    'Florida Panthers': 'FLA',
    'Los Angeles Kings': 'LAK',
    'Minnesota Wild': 'MIN',
    'Montréal Canadiens': 'MTL',
    'Montreal Canadiens': 'MTL',
    'Nashville Predators': 'NSH',
    'New Jersey Devils': 'NJD',
    'New York Islanders': 'NYI',
    'New York Rangers': 'NYR',
    'Ottawa Senators': 'OTT',
    'Philadelphia Flyers': 'PHI',
    'Pittsburgh Penguins': 'PIT',
    'San Jose Sharks': 'SJS',
    'Seattle Kraken': 'SEA',
    'St. Louis Blues': 'STL',
    'St Louis Blues': 'STL',
    'Tampa Bay Lightning': 'TBL',
    'Toronto Maple Leafs': 'TOR',
    'Utah Hockey Club': 'UTA',
    'Utah Mammoth': 'UTA',
    'Vancouver Canucks': 'VAN',
    'Vegas Golden Knights': 'VGK',
    'Washington Capitals': 'WSH',
    'Winnipeg Jets': 'WPG'
}

def get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build('sheets', 'v4', credentials=creds)

def get_nhl_games_with_odds():
    """Fetch upcoming NHL games with odds from Odds API"""
    print("Fetching NHL games from Odds API...")
    
    url = 'https://api.the-odds-api.com/v4/sports/icehockey_nhl/odds/'
    params = {
        'apiKey': ODDS_API_KEY,
        'regions': 'us',
        'markets': 'h2h,spreads,totals',
        'oddsFormat': 'american'
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print(f"Error fetching odds: {response.status_code}")
        return []
    
    games = response.json()
    print(f"Found {len(games)} upcoming NHL games")
    
    return games

def format_game_data(games):
    """Format games for Google Sheets"""
    rows = []
    
    for game in games:
        away_team_full = game['away_team']
        home_team_full = game['home_team']
        
        # Convert to abbreviations
        away_team = NHL_TEAM_MAP.get(away_team_full, away_team_full)
        home_team = NHL_TEAM_MAP.get(home_team_full, home_team_full)
        
        commence_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
        
        # Convert to EST
        est = pytz.timezone('US/Eastern')
        commence_time_est = commence_time.astimezone(est)
        
        game_date = commence_time_est.strftime('%Y-%m-%d')
        game_time = commence_time_est.strftime('%H:%M')
        game_id = f"{game_date}_{away_team}_{home_team}"
        
        # Extract odds
        away_ml = None
        home_ml = None
        puck_line = None
        total_line = None
        
        if game.get('bookmakers'):
            bookmaker = game['bookmakers'][0]  # Use first bookmaker
            
            for market in bookmaker.get('markets', []):
                if market['key'] == 'h2h':
                    for outcome in market['outcomes']:
                        if outcome['name'] == away_team_full:
                            away_ml = outcome['price']
                        elif outcome['name'] == home_team_full:
                            home_ml = outcome['price']
                
                elif market['key'] == 'spreads':
                    for outcome in market['outcomes']:
                        if outcome['name'] == home_team_full:
                            puck_line = outcome['point']
                
                elif market['key'] == 'totals':
                    if market['outcomes']:
                        total_line = market['outcomes'][0]['point']
        
        row = [
            game_id,
            game_date,
            game_time,
            away_team,
            home_team,
            away_ml or '',
            home_ml or '',
            puck_line or '',
            total_line or ''
        ]
        
        rows.append(row)
    
    return rows

def write_to_sheet(service, rows):
    """Write games to Upcoming_Games tab"""
    print(f"\nWriting {len(rows)} games to sheet...")
    
    # Clear existing data (except headers)
    service.spreadsheets().values().clear(
        spreadsheetId=NHL_SHEET_ID,
        range='Upcoming_Games!A2:I1000'
    ).execute()
    
    # Write new data
    if rows:
        body = {'values': rows}
        service.spreadsheets().values().update(
            spreadsheetId=NHL_SHEET_ID,
            range='Upcoming_Games!A2',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"Successfully wrote {len(rows)} games to Upcoming_Games tab")
        
        # Print sample
        print("\nSample games:")
        for row in rows[:3]:
            print(f"  {row[3]} @ {row[4]} - {row[1]} {row[2]}")
    else:
        print("No games to write")

def main():
    print("="*60)
    print("POPULATING NHL UPCOMING GAMES")
    print("="*60)
    
    # Get games with odds
    games = get_nhl_games_with_odds()
    
    if not games:
        print("\nNo upcoming NHL games found")
        return
    
    # Format for sheets
    rows = format_game_data(games)
    
    # Write to sheet
    service = get_sheets_service()
    write_to_sheet(service, rows)
    
    print("\n" + "="*60)
    print("DONE!")
    print("="*60)
    print(f"\nPopulated {len(rows)} NHL games in Upcoming_Games tab")
    print("Ready to generate picks!")

if __name__ == '__main__':
    main()

