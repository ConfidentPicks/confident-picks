#!/usr/bin/env python3

"""
Clean Up Columns and Add Scoring Charts
======================================

This script removes the old prediction column and adds scoring charts
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

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
    
    print("🧹 CLEANING UP COLUMNS AND ADDING SCORING CHARTS")
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
    
    # Find column indices
    col_indices = {}
    for i, header in enumerate(headers):
        if 'predicted_winner' in header.lower():
            col_indices['predicted_winner'] = i
        elif 'confidence_score' in header.lower():
            col_indices['confidence_score'] = i
        elif 'home_team' in header.lower():
            col_indices['home_team'] = i
        elif 'away_team' in header.lower():
            col_indices['away_team'] = i
        elif 'home_score' in header.lower():
            col_indices['home_score'] = i
        elif 'away_score' in header.lower():
            col_indices['away_score'] = i
        elif 'prediction_outcome' in header.lower() or 'outcome' in header.lower():
            col_indices['outcome'] = i
        elif 'gameday' in header.lower():
            col_indices['gameday'] = i
        elif 'season' in header.lower():
            col_indices['season'] = i
    
    print(f"Found key columns: {col_indices}")
    
    # Step 1: Remove the old prediction column (AT) and shift everything left
    print("\n🧹 Removing old prediction column (AT)...")
    
    # Get current headers
    current_headers = headers.copy()
    
    # Find the old prediction column index
    old_prediction_index = None
    for i, header in enumerate(current_headers):
        if 'predicted_winner' in header.lower() and i == 45:  # Column AT (index 45)
            old_prediction_index = i
            break
    
    if old_prediction_index is not None:
        print(f"Found old prediction column at index {old_prediction_index} (Column {get_column_letter(old_prediction_index)})")
        
        # Remove the old column by shifting all columns to the left
        new_headers = []
        new_data = []
        
        # Process headers
        for i, header in enumerate(current_headers):
            if i != old_prediction_index:
                new_headers.append(header)
        
        # Process data rows
        for row in data_rows:
            new_row = []
            for i, value in enumerate(row):
                if i != old_prediction_index:
                    new_row.append(value)
            new_data.append(new_row)
        
        # Clear the sheet and write new data
        print("Clearing sheet and writing cleaned data...")
        service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range="upcoming_games!A:ZZ"
        ).execute()
        
        # Write new headers and data
        all_data = [new_headers] + new_data
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="upcoming_games!A1",
            valueInputOption='USER_ENTERED',
            body={'values': all_data}
        ).execute()
        
        print("✅ Old prediction column removed!")
        
        # Update column indices after removal
        col_indices = {}
        for i, header in enumerate(new_headers):
            if 'predicted_winner' in header.lower():
                col_indices['predicted_winner'] = i
            elif 'confidence_score' in header.lower():
                col_indices['confidence_score'] = i
            elif 'home_team' in header.lower():
                col_indices['home_team'] = i
            elif 'away_team' in header.lower():
                col_indices['away_team'] = i
            elif 'home_score' in header.lower():
                col_indices['home_score'] = i
            elif 'away_score' in header.lower():
                col_indices['away_score'] = i
            elif 'prediction_outcome' in header.lower() or 'outcome' in header.lower():
                col_indices['outcome'] = i
            elif 'gameday' in header.lower():
                col_indices['gameday'] = i
            elif 'season' in header.lower():
                col_indices['season'] = i
        
        print(f"Updated column indices: {col_indices}")
        
        # Update data_rows to use new data
        data_rows = new_data
    else:
        print("Old prediction column not found, proceeding with current data")
    
    # Step 2: Add scoring charts
    print("\n📊 Adding scoring charts...")
    
    # Get current data again after cleanup
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="upcoming_games!A:ZZ"
    ).execute()
    
    values = result.get('values', [])
    headers = values[0]
    data_rows = values[1:]
    
    # Calculate current date for date filtering
    current_date = datetime.now()
    seven_days_ago = current_date - timedelta(days=7)
    thirty_days_ago = current_date - timedelta(days=30)
    
    # Initialize counters
    season_2025_wins = 0
    season_2025_losses = 0
    past_7_days_wins = 0
    past_7_days_losses = 0
    past_30_days_wins = 0
    past_30_days_losses = 0
    
    # Count wins and losses
    for row in data_rows:
        # Get game data
        outcome = row[col_indices['outcome']] if len(row) > col_indices['outcome'] else ""
        gameday = row[col_indices['gameday']] if len(row) > col_indices['gameday'] else ""
        season = row[col_indices['season']] if len(row) > col_indices['season'] else ""
        
        if outcome == "WIN":
            season_2025_wins += 1
            # Check if within past 7 days
            try:
                if gameday:
                    game_date = datetime.strptime(gameday, '%Y-%m-%d')
                    if game_date >= seven_days_ago:
                        past_7_days_wins += 1
                    if game_date >= thirty_days_ago:
                        past_30_days_wins += 1
            except:
                pass
        elif outcome == "LOSS":
            season_2025_losses += 1
            # Check if within past 7 days
            try:
                if gameday:
                    game_date = datetime.strptime(gameday, '%Y-%m-%d')
                    if game_date >= seven_days_ago:
                        past_7_days_losses += 1
                    if game_date >= thirty_days_ago:
                        past_30_days_losses += 1
            except:
                pass
    
    # Calculate win rates
    season_2025_total = season_2025_wins + season_2025_losses
    season_2025_rate = (season_2025_wins / season_2025_total * 100) if season_2025_total > 0 else 0
    
    past_7_days_total = past_7_days_wins + past_7_days_losses
    past_7_days_rate = (past_7_days_wins / past_7_days_total * 100) if past_7_days_total > 0 else 0
    
    past_30_days_total = past_30_days_wins + past_30_days_losses
    past_30_days_rate = (past_30_days_wins / past_30_days_total * 100) if past_30_days_total > 0 else 0
    
    # Add scoring charts to the sheet
    print("Adding scoring charts to sheet...")
    
    # Find a good place to add the charts (after the last column)
    last_col_index = len(headers) - 1
    chart_start_col = last_col_index + 2  # Leave one column gap
    
    # Create scoring chart headers
    chart_headers = [
        "SCORING_CHARTS",
        "2025_SEASON",
        "Wins",
        "Losses", 
        "Win_Rate",
        "PAST_7_DAYS",
        "Wins",
        "Losses",
        "Win_Rate",
        "PAST_30_DAYS", 
        "Wins",
        "Losses",
        "Win_Rate"
    ]
    
    # Create scoring chart data
    chart_data = [
        chart_headers,
        ["", "", "", "", "", "", "", "", "", "", "", "", ""],
        ["", f"{season_2025_wins}", f"{season_2025_losses}", f"{season_2025_rate:.1f}%", "", f"{past_7_days_wins}", f"{past_7_days_losses}", f"{past_7_days_rate:.1f}%", "", f"{past_30_days_wins}", f"{past_30_days_losses}", f"{past_30_days_rate:.1f}%"]
    ]
    
    # Write scoring charts
    chart_start_col_letter = get_column_letter(chart_start_col)
    chart_range = f"upcoming_games!{chart_start_col_letter}1"
    
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=chart_range,
        valueInputOption='USER_ENTERED',
        body={'values': chart_data}
    ).execute()
    
    print("✅ Scoring charts added!")
    
    print("✅ ALL CLEANUP AND CHARTS COMPLETE!")
    print(f"\n📊 SCORING SUMMARY:")
    print(f"   2025 SEASON: {season_2025_wins} wins, {season_2025_losses} losses ({season_2025_rate:.1f}% win rate)")
    print(f"   PAST 7 DAYS: {past_7_days_wins} wins, {past_7_days_losses} losses ({past_7_days_rate:.1f}% win rate)")
    print(f"   PAST 30 DAYS: {past_30_days_wins} wins, {past_30_days_losses} losses ({past_30_days_rate:.1f}% win rate)")
    
    print(f"\n📋 CHANGES MADE:")
    print(f"   ✅ Removed old prediction column (AT)")
    print(f"   ✅ Added scoring charts for 2025 season, past 7 days, and past 30 days")
    print(f"   ✅ Charts show wins, losses, and win rates for each period")

if __name__ == "__main__":
    main()



