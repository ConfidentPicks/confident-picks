#!/usr/bin/env python3
"""
NBA Current Season Team Stats - Daily Update
Updates the current season (2025-26) with latest games
"""

import sys
import os
import time
from datetime import datetime, timedelta
import json
import math

from nba_api.stats.endpoints import scoreboardv2, boxscoretraditionalv2
import pandas as pd

# Google Sheets setup
from google.oauth2.service_account import Credentials
import gspread

# Configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'
NBA_SHEET_ID = '1Hel-NsCxmk07nM0AH4VkJFB9hSK23X7XOxtA4wyRNRo'

CURRENT_SEASON_START = '2025-10-21'  # Start of current season (2025-26)
CURRENT_SEASON_NAME = '2025-26'

def initialize_sheets():
    """Initialize Google Sheets client"""
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

def fetch_games_for_date(date_str, max_retries=3):
    """Fetch team stats for a specific date"""
    for attempt in range(max_retries):
        try:
            print(f"  Fetching {date_str}... (attempt {attempt + 1}/{max_retries})")
            
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            
            scoreboard_data = scoreboardv2.ScoreboardV2(
                game_date=date_obj.strftime('%m/%d/%Y'),
                league_id='00',
                day_offset='0'
            )
            
            games = scoreboard_data.line_score.get_data_frame()
            
            if games.empty:
                print(f"    No games found for {date_str}")
                return []
            
            game_list = []
            game_ids = games['GAME_ID'].unique()
            
            for game_id in game_ids:
                try:
                    box_score = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id, timeout=10)
                    all_dfs = box_score.get_data_frames()
                    
                    if len(all_dfs) < 2:
                        continue
                    
                    team_stats_df = all_dfs[1]
                    game_data = games[games['GAME_ID'] == game_id]
                    
                    if len(game_data) < 2:
                        continue
                    
                    away_team_row = game_data.iloc[0]
                    home_team_row = game_data.iloc[1]
                    
                    for idx, team_row in team_stats_df.iterrows():
                        team_abbr = team_row['TEAM_ABBREVIATION']
                        
                        is_home = team_abbr == home_team_row['TEAM_ABBREVIATION']
                        opponent = home_team_row['TEAM_ABBREVIATION'] if not is_home else away_team_row['TEAM_ABBREVIATION']
                        
                        team_score = int(home_team_row['PTS']) if is_home else int(away_team_row['PTS'])
                        opp_score = int(away_team_row['PTS']) if is_home else int(home_team_row['PTS'])
                        win = 1 if team_score > opp_score else 0
                        
                        game_info = {
                            'game_id': game_id,
                            'date': date_str,
                            'team': team_abbr,
                            'opponent': opponent,
                            'home_away': 'Home' if is_home else 'Away',
                            'team_score': team_score,
                            'opp_score': opp_score,
                            'win': win,
                            'min': team_row.get('MIN', ''),
                            'fgm': team_row.get('FGM', ''),
                            'fga': team_row.get('FGA', ''),
                            'fg_pct': team_row.get('FG_PCT', ''),
                            'fg3m': team_row.get('FG3M', ''),
                            'fg3a': team_row.get('FG3A', ''),
                            'fg3_pct': team_row.get('FG3_PCT', ''),
                            'ftm': team_row.get('FTM', ''),
                            'fta': team_row.get('FTA', ''),
                            'ft_pct': team_row.get('FT_PCT', ''),
                            'oreb': team_row.get('OREB', ''),
                            'dreb': team_row.get('DREB', ''),
                            'reb': team_row.get('REB', ''),
                            'ast': team_row.get('AST', ''),
                            'stl': team_row.get('STL', ''),
                            'blk': team_row.get('BLK', ''),
                            'tov': team_row.get('TO', ''),
                            'pf': team_row.get('PF', ''),
                            'pts': team_row.get('PTS', ''),
                            'plus_minus': team_row.get('PLUS_MINUS', ''),
                        }
                        
                        game_list.append(game_info)
                    
                    time.sleep(1.5)
                    
                except Exception as e:
                    print(f"    Warning: Could not get stats for game {game_id}: {e}")
                    continue
            
            return game_list
                
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                print(f"  Error fetching {date_str} (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"  Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"  Error fetching {date_str} after {max_retries} attempts: {e}")
                return []
    
    return []

def append_to_sheet(new_games, season_name):
    """Append new games to current season sheet"""
    try:
        print(f"\nUpdating {season_name} sheet...")
        
        client = initialize_sheets()
        sheet = client.open_by_key(NBA_SHEET_ID)
        
        worksheet_name = f'Team_Stats_{season_name}'
        try:
            worksheet = sheet.worksheet(worksheet_name)
            # Append to existing sheet
        except:
            # Create new sheet with headers
            worksheet = sheet.add_worksheet(title=worksheet_name, rows=5000, cols=30)
            headers = [
                'Game ID', 'Date', 'Team', 'Opponent', 'Home/Away', 'Team Score', 'Opponent Score', 'Win',
                'Min', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%',
                'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'Plus/Minus'
            ]
            worksheet.append_row(headers)
            print(f"  Created new {worksheet_name} sheet")
        
        if new_games:
            headers = [
                'Game ID', 'Date', 'Team', 'Opponent', 'Home/Away', 'Team Score', 'Opponent Score', 'Win',
                'Min', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%',
                'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'Plus/Minus'
            ]
            
            all_rows = []
            for game in new_games:
                row = [game.get(col.lower().replace('/', '').replace(' ', '_'), '') for col in headers]
                all_rows.append(row)
            
            worksheet.append_rows(all_rows)
            print(f"  [OK] Added {len(new_games)} new team records to {worksheet_name}")
        else:
            print(f"  No new games to add")
        
    except Exception as e:
        print(f"  Error updating sheet: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function - daily update"""
    print("=" * 60)
    print("NBA CURRENT SEASON TEAM UPDATE")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get today's date
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    # Check last 7 days for completed games (wider range to catch data)
    dates_to_check = [
        yesterday.strftime('%Y-%m-%d'),
        (yesterday - timedelta(days=1)).strftime('%Y-%m-%d'),
        (yesterday - timedelta(days=2)).strftime('%Y-%m-%d'),
        (yesterday - timedelta(days=3)).strftime('%Y-%m-%d'),
        (yesterday - timedelta(days=4)).strftime('%Y-%m-%d'),
        (yesterday - timedelta(days=5)).strftime('%Y-%m-%d'),
        (yesterday - timedelta(days=6)).strftime('%Y-%m-%d')
    ]
    
    print(f"Checking dates: {', '.join(dates_to_check)}")
    print()
    
    all_new_games = []
    
    for date_str in dates_to_check:
        games = fetch_games_for_date(date_str)
        all_new_games.extend(games)
        if games:
            print(f"  Found {len(games)} team records for {date_str}")
    
    if all_new_games:
        append_to_sheet(all_new_games, CURRENT_SEASON_NAME)
    else:
        print("\nNo new games found")
    
    print()
    print("=" * 60)
    print(f"UPDATE COMPLETE: {len(all_new_games)} team records added")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == '__main__':
    main() 