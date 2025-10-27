#!/usr/bin/env python3

"""
Fix Column AU - Find Actual Scores and Winners
============================================

This script finds the actual score columns and uses them to determine winners
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
    
    print("🔍 FINDING ACTUAL SCORE COLUMNS AND FIXING AU")
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
    
    # Print all headers to find score columns
    print(f"\n📋 ALL COLUMN HEADERS:")
    for i, header in enumerate(headers):
        col_letter = get_column_letter(i)
        print(f"  {col_letter}: {header}")
    
    # Find home_team, away_team columns
    home_team_index = None
    away_team_index = None
    
    for i, header in enumerate(headers):
        if 'home_team' in header.lower():
            home_team_index = i
        elif 'away_team' in header.lower():
            away_team_index = i
    
    print(f"\n🔍 CHECKING SAMPLE DATA IN FIRST 10 ROWS:")
    for i in range(min(10, len(data_rows))):
        row = data_rows[i]
        row_num = i + 2
        
        home_team = row[home_team_index] if len(row) > home_team_index else ""
        away_team = row[away_team_index] if len(row) > away_team_index else ""
        
        print(f"  Row {row_num}: {away_team} @ {home_team}")
        
        # Check all columns for score-like data
        for j, value in enumerate(row):
            if value and str(value).strip() and str(value).replace('.', '').isdigit():
                col_letter = get_column_letter(j)
                header = headers[j] if j < len(headers) else "Unknown"
                print(f"    {col_letter} ({header}): '{value}'")
    
    # Look for columns with score data (I and K should be away_score and home_score)
    print(f"\n🔍 LOOKING FOR SCORE COLUMNS:")
    
    # Based on the original structure, I and K should be away_score and home_score
    away_score_index = 8  # Column I
    home_score_index = 10  # Column K
    
    print(f"Trying away_score at index {away_score_index} (Column {get_column_letter(away_score_index)})")
    print(f"Trying home_score at index {home_score_index} (Column {get_column_letter(home_score_index)})")
    
    # Check if these columns have score data
    print(f"\n📊 CHECKING SCORE DATA IN COLUMNS I AND K:")
    for i in range(min(10, len(data_rows))):
        row = data_rows[i]
        row_num = i + 2
        
        home_team = row[home_team_index] if len(row) > home_team_index else ""
        away_team = row[away_team_index] if len(row) > away_team_index else ""
        away_score = row[away_score_index] if len(row) > away_score_index else ""
        home_score = row[home_score_index] if len(row) > home_score_index else ""
        
        print(f"  Row {row_num}: {away_team} @ {home_team}")
        print(f"    Away Score (I): '{away_score}'")
        print(f"    Home Score (K): '{home_score}'")
    
    # Now fix column AU with actual winners using the correct score columns
    print(f"\n🔧 FIXING COLUMN AU WITH ACTUAL WINNERS...")
    
    au_index = 46  # Column AU
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

if __name__ == "__main__":
    main()


