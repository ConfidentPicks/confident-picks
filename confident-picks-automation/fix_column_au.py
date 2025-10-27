#!/usr/bin/env python3

"""
Fix Column AU - Actual Winner
============================

This script fixes column AU to show actual winner for completed games, blank for future games
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

def get_column_letter(col_index):
    """Convert column index to Google Sheets column letter (supports beyond Z)"""
    result = ""
    while col_index >= 0:
        result = chr(65 + (col_index % 26)) + result
        col_index = col_index // 26 - 1
    return result

def main():
    # Configuration
    credentials_path = "C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json"
    spreadsheet_id = "1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU"
    
    # Setup connection
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    
    service = build('sheets', 'v4', credentials=credentials)
    
    print("🔧 FIXING COLUMN AU - ACTUAL WINNER")
    print("=" * 60)
    
    # Get current data
    print("📊 Loading current sheet data...")
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="upcoming_games!A:ZZ"
    ).execute()
    
    values = result.get('values', [])
    if not values or len(values) < 2:
        print("❌ No data found")
        return
    
    headers = values[0]
    data_rows = values[1:]
    
    print(f"✅ Found {len(data_rows)} rows with {len(headers)} columns")
    
    # Find column AU (actual winner)
    au_index = None
    for i, header in enumerate(headers):
        if i == 46:  # Column AU (index 46)
            au_index = i
            break
    
    if au_index is None:
        print("❌ Column AU not found")
        return
    
    print(f"Found column AU at index {au_index}")
    
    # Find home_team, away_team, home_score, away_score columns
    home_team_index = None
    away_team_index = None
    home_score_index = None
    away_score_index = None
    
    for i, header in enumerate(headers):
        if 'home_team' in header.lower():
            home_team_index = i
        elif 'away_team' in header.lower():
            away_team_index = i
        elif 'home_score' in header.lower():
            home_score_index = i
        elif 'away_score' in header.lower():
            away_score_index = i
    
    if home_team_index is None or away_team_index is None or home_score_index is None or away_score_index is None:
        print("❌ Required columns not found")
        return
    
    print(f"Found columns: home_team={home_team_index}, away_team={away_team_index}, home_score={home_score_index}, away_score={away_score_index}")
    
    # Check current data in column AU
    print(f"\n🔍 CHECKING CURRENT DATA IN COLUMN AU:")
    for i in range(min(10, len(data_rows))):
        row = data_rows[i]
        row_num = i + 2
        
        home_team = row[home_team_index] if len(row) > home_team_index else ""
        away_team = row[away_team_index] if len(row) > away_team_index else ""
        home_score = row[home_score_index] if len(row) > home_score_index else ""
        away_score = row[away_score_index] if len(row) > away_score_index else ""
        current_au = row[au_index] if len(row) > au_index else ""
        
        print(f"  Row {row_num}: {away_team} @ {home_team}")
        print(f"    Scores: {away_score}-{home_score}")
        print(f"    Current AU value: '{current_au}'")
    
    # Fix column AU with actual winners
    print(f"\n🔧 FIXING COLUMN AU WITH ACTUAL WINNERS...")
    
    updates = []
    games_processed = 0
    completed_games = 0
    future_games = 0
    
    for idx, row in enumerate(data_rows):
        row_num = idx + 2  # +2 because row 1 is headers
        
        # Get game data
        home_team = row[home_team_index] if len(row) > home_team_index else ""
        away_team = row[away_team_index] if len(row) > away_team_index else ""
        home_score = row[home_score_index] if len(row) > home_score_index else ""
        away_score = row[away_score_index] if len(row) > away_score_index else ""
        
        # Check if game is completed (has scores)
        if home_score and away_score and home_score.strip() and away_score.strip():
            try:
                home_score_int = int(home_score)
                away_score_int = int(away_score)
                
                # Determine actual winner
                if home_score_int > away_score_int:
                    actual_winner = home_team
                elif away_score_int > home_score_int:
                    actual_winner = away_team
                else:
                    actual_winner = "TIE"
                
                # Update column AU with actual winner
                col_letter = get_column_letter(au_index)
                updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [[actual_winner]]})
                completed_games += 1
                
                if completed_games <= 15:  # Show first 15 completed games
                    print(f"  ✓ Row {row_num}: {away_team} @ {home_team} ({away_score_int}-{home_score_int}) → '{actual_winner}'")
                
            except ValueError:
                # Skip if scores aren't valid numbers
                continue
        else:
            # Game not completed yet - set to blank
            col_letter = get_column_letter(au_index)
            updates.append({'range': f"upcoming_games!{col_letter}{row_num}", 'values': [['']]})
            future_games += 1
        
        games_processed += 1
    
    # Execute updates
    if updates:
        print(f"\n📝 Updating {games_processed} games in column AU...")
        chunk_size = 100
        for i in range(0, len(updates), chunk_size):
            chunk = updates[i:i+chunk_size]
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'valueInputOption': 'USER_ENTERED', 'data': chunk}
            ).execute()
            print(f"  Updated chunk {i//chunk_size + 1}/{(len(updates)-1)//chunk_size + 1}")
    
    print("✅ COLUMN AU FIXED!")
    print(f"\n📊 SUMMARY:")
    print(f"   ✅ Processed {games_processed} games")
    print(f"   ✅ {completed_games} completed games show actual winners")
    print(f"   ✅ {future_games} future games are blank")
    print(f"   ✅ Column AU now shows actual winners for completed games")
    
    print(f"\n📋 NEXT STEPS:")
    print(f"   - Column AU now shows actual winners (PHI, KC, ATL, etc.) for completed games")
    print(f"   - Future games are blank until they're played")
    print(f"   - Ready for next column fix")

if __name__ == "__main__":
    main()


