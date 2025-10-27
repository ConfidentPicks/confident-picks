"""
NBA Historical Data Fetcher
Fetches NBA game data from 2021-2024 seasons and current season
Writes to Google Sheets with progress tracking
"""

import requests
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os

# Configuration
SHEET_ID = '1Hel-NsCxmk07nM0AH4VkJFB9hSK23X7XOxtA4wyRNRo'
CREDS_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'
PROGRESS_FILE = 'nba_fetch_progress.json'
ODDS_API_KEY = 'b68d307ccf8519e69cbdea629b175b08'

# NBA team abbreviation mapping (ESPN to standard)
NBA_TEAMS = {
    'ATL': 'Atlanta Hawks', 'BOS': 'Boston Celtics', 'BKN': 'Brooklyn Nets',
    'CHA': 'Charlotte Hornets', 'CHI': 'Chicago Bulls', 'CLE': 'Cleveland Cavaliers',
    'DAL': 'Dallas Mavericks', 'DEN': 'Denver Nuggets', 'DET': 'Detroit Pistons',
    'GSW': 'Golden State Warriors', 'HOU': 'Houston Rockets', 'IND': 'Indiana Pacers',
    'LAC': 'LA Clippers', 'LAL': 'LA Lakers', 'MEM': 'Memphis Grizzlies',
    'MIA': 'Miami Heat', 'MIL': 'Milwaukee Bucks', 'MIN': 'Minnesota Timberwolves',
    'NOP': 'New Orleans Pelicans', 'NYK': 'New York Knicks', 'OKC': 'Oklahoma City Thunder',
    'ORL': 'Orlando Magic', 'PHI': 'Philadelphia 76ers', 'PHX': 'Phoenix Suns',
    'POR': 'Portland Trail Blazers', 'SAC': 'Sacramento Kings', 'SAS': 'San Antonio Spurs',
    'TOR': 'Toronto Raptors', 'UTA': 'Utah Jazz', 'WAS': 'Washington Wizards'
}

def update_progress(status, message, current_season=None, games_fetched=0, total_games=0):
    """Update progress JSON file for monitoring"""
    progress = {
        'status': status,
        'message': message,
        'current_season': current_season,
        'games_fetched': games_fetched,
        'total_games': total_games,
        'last_updated': datetime.now().isoformat(),
        'progress_percent': round((games_fetched / total_games * 100) if total_games > 0 else 0, 1)
    }
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)
    print(f"[{status.upper()}] {message}")

def get_sheets_service():
    """Initialize Google Sheets API service"""
    creds = Credentials.from_service_account_file(
        CREDS_FILE,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    return build('sheets', 'v4', credentials=creds)

def create_sheet_structure(service):
    """Create tabs for historical data, current season, and upcoming games"""
    update_progress('initializing', 'Creating sheet structure...')
    
    try:
        # Get existing sheets
        sheet_metadata = service.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
        existing_sheets = [s['properties']['title'] for s in sheet_metadata.get('sheets', [])]
        
        # Define required sheets
        required_sheets = ['Historical_Games', 'Current_Season', 'Upcoming_Games']
        
        requests = []
        for sheet_name in required_sheets:
            if sheet_name not in existing_sheets:
                requests.append({
                    'addSheet': {
                        'properties': {
                            'title': sheet_name,
                            'gridProperties': {
                                'rowCount': 10000,
                                'columnCount': 50
                            }
                        }
                    }
                })
        
        if requests:
            service.spreadsheets().batchUpdate(
                spreadsheetId=SHEET_ID,
                body={'requests': requests}
            ).execute()
            print(f"Created {len(requests)} new sheets")
        else:
            print("All required sheets already exist")
            
    except Exception as e:
        print(f"Error creating sheet structure: {e}")
        raise

def fetch_nba_season_games(season_year):
    """
    Fetch NBA games for a specific season using ESPN API
    season_year: e.g., 2021 for 2021-22 season
    """
    games = []
    
    # NBA season runs from October to June (next year)
    # Regular season is ~1,230 games (82 games × 30 teams / 2)
    
    try:
        # ESPN NBA scoreboard API
        # Format: YYYYMMDD
        start_date = datetime(season_year, 10, 1)
        end_date = datetime(season_year + 1, 6, 30)
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y%m%d')
            url = f'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={date_str}'
            
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'events' in data:
                        for event in data['events']:
                            game_data = parse_nba_game(event, season_year)
                            if game_data:
                                games.append(game_data)
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error fetching date {date_str}: {e}")
            
            current_date += timedelta(days=1)
            
            # Update progress every 30 days
            if (current_date - start_date).days % 30 == 0:
                update_progress(
                    'fetching',
                    f'Fetching {season_year}-{season_year+1} season: {current_date.strftime("%Y-%m-%d")}',
                    f'{season_year}-{season_year+1}',
                    len(games),
                    1230
                )
    
    except Exception as e:
        print(f"Error fetching season {season_year}: {e}")
    
    return games

def parse_nba_game(event, season_year):
    """Parse ESPN NBA game event into structured data"""
    try:
        game_id = event.get('id')
        game_date = event.get('date')
        status = event.get('status', {}).get('type', {}).get('completed', False)
        
        competitions = event.get('competitions', [])
        if not competitions:
            return None
        
        competition = competitions[0]
        competitors = competition.get('competitors', [])
        
        if len(competitors) != 2:
            return None
        
        # Identify home and away teams
        home_team = next((c for c in competitors if c.get('homeAway') == 'home'), None)
        away_team = next((c for c in competitors if c.get('homeAway') == 'away'), None)
        
        if not home_team or not away_team:
            return None
        
        # Extract team data
        home_abbr = home_team.get('team', {}).get('abbreviation', '')
        away_abbr = away_team.get('team', {}).get('abbreviation', '')
        
        home_score = int(home_team.get('score', 0)) if status else None
        away_score = int(away_team.get('score', 0)) if status else None
        
        # Extract detailed stats if available
        home_stats = home_team.get('statistics', [])
        away_stats = away_team.get('statistics', [])
        
        def get_stat(stats_list, name):
            """Extract specific stat from statistics list"""
            for stat in stats_list:
                if stat.get('name') == name:
                    return stat.get('displayValue', 0)
            return 0
        
        game_data = {
            'game_id': game_id,
            'date': game_date,
            'season': f'{season_year}-{season_year+1}',
            'home_team': home_abbr,
            'away_team': away_abbr,
            'home_score': home_score,
            'away_score': away_score,
            'completed': status,
            
            # Team stats (if available)
            'home_fg_pct': get_stat(home_stats, 'fieldGoalPct'),
            'away_fg_pct': get_stat(away_stats, 'fieldGoalPct'),
            'home_3pt_pct': get_stat(home_stats, 'threePointPct'),
            'away_3pt_pct': get_stat(away_stats, 'threePointPct'),
            'home_ft_pct': get_stat(home_stats, 'freeThrowPct'),
            'away_ft_pct': get_stat(away_stats, 'freeThrowPct'),
            'home_rebounds': get_stat(home_stats, 'rebounds'),
            'away_rebounds': get_stat(away_stats, 'rebounds'),
            'home_assists': get_stat(home_stats, 'assists'),
            'away_assists': get_stat(away_stats, 'assists'),
            'home_turnovers': get_stat(home_stats, 'turnovers'),
            'away_turnovers': get_stat(away_stats, 'turnovers'),
            'home_steals': get_stat(home_stats, 'steals'),
            'away_steals': get_stat(away_stats, 'steals'),
            'home_blocks': get_stat(home_stats, 'blocks'),
            'away_blocks': get_stat(away_stats, 'blocks'),
        }
        
        return game_data
        
    except Exception as e:
        print(f"Error parsing game: {e}")
        return None

def write_to_sheet(service, sheet_name, data):
    """Write data to specified sheet"""
    if not data:
        print(f"No data to write to {sheet_name}")
        return
    
    df = pd.DataFrame(data)
    
    # Prepare data for Sheets API
    values = [df.columns.tolist()] + df.values.tolist()
    
    body = {
        'values': values
    }
    
    try:
        # Clear existing data
        service.spreadsheets().values().clear(
            spreadsheetId=SHEET_ID,
            range=f'{sheet_name}!A:Z'
        ).execute()
        
        # Write new data
        service.spreadsheets().values().update(
            spreadsheetId=SHEET_ID,
            range=f'{sheet_name}!A1',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"Wrote {len(data)} rows to {sheet_name}")
        
    except Exception as e:
        print(f"Error writing to sheet {sheet_name}: {e}")
        raise

def fetch_current_season_games():
    """Fetch current 2024-25 season games"""
    update_progress('fetching', 'Fetching current 2024-25 season games...', '2024-25', 0, 1230)
    
    # Current season started October 2024
    return fetch_nba_season_games(2024)

def main():
    """Main execution function"""
    print("=" * 60)
    print("NBA DATA FETCHER - Starting")
    print("=" * 60)
    
    update_progress('starting', 'Initializing NBA data collection...')
    
    try:
        # Initialize Google Sheets
        service = get_sheets_service()
        create_sheet_structure(service)
        
        # Fetch historical data (2021-2024)
        all_historical_games = []
        seasons = [2021, 2022, 2023]  # 2021-22, 2022-23, 2023-24
        
        total_seasons = len(seasons) + 1  # +1 for current season
        
        for idx, season_year in enumerate(seasons, 1):
            update_progress(
                'fetching',
                f'Fetching season {season_year}-{season_year+1} ({idx}/{total_seasons})...',
                f'{season_year}-{season_year+1}',
                len(all_historical_games),
                1230 * total_seasons
            )
            
            season_games = fetch_nba_season_games(season_year)
            all_historical_games.extend(season_games)
            
            print(f"Fetched {len(season_games)} games for {season_year}-{season_year+1} season")
        
        # Write historical data
        update_progress('writing', 'Writing historical data to sheet...', 'Historical', len(all_historical_games), len(all_historical_games))
        write_to_sheet(service, 'Historical_Games', all_historical_games)
        
        # Fetch current season
        current_season_games = fetch_current_season_games()
        update_progress('writing', 'Writing current season data to sheet...', '2024-25', len(current_season_games), len(current_season_games))
        write_to_sheet(service, 'Current_Season', current_season_games)
        
        # Success
        total_games = len(all_historical_games) + len(current_season_games)
        update_progress(
            'completed',
            f'Successfully fetched {total_games} total games!',
            'All',
            total_games,
            total_games
        )
        
        print("=" * 60)
        print(f"COMPLETED: {len(all_historical_games)} historical + {len(current_season_games)} current season games")
        print("=" * 60)
        
    except Exception as e:
        update_progress('error', f'Error: {str(e)}')
        print(f"FATAL ERROR: {e}")
        raise

if __name__ == '__main__':
    main()
