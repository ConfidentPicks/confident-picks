#!/usr/bin/env python3

"""
Verify Predictions in Upcoming Games
==================================

This script verifies that predictions are now in the upcoming_games tab
"""

import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

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
    
    print("🔍 VERIFYING PREDICTIONS IN UPCOMING_GAMES TAB")
    print("=" * 60)
    
    # Check upcoming_games
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="upcoming_games!A:ZZ"
    ).execute()
    
    values = result.get('values', [])
    
    if values and len(values) > 1:
        headers = values[0]
        data_rows = values[1:]
        
        print(f"✅ Found {len(data_rows)} rows in upcoming_games")
        
        # Find prediction columns
        prediction_cols = []
        for i, header in enumerate(headers):
            if any(word in header.lower() for word in ['predicted', 'confidence', 'betting', 'probability']):
                prediction_cols.append((i, header))
        
        print(f"\n🎯 PREDICTION COLUMNS FOUND:")
        for col_idx, header in prediction_cols:
            print(f"  Column {chr(65+col_idx)}: {header}")
        
        # Check if predictions are populated
        print(f"\n📊 CHECKING PREDICTION DATA...")
        
        games_with_predictions = 0
        for i, row in enumerate(data_rows[:10]):  # Check first 10 rows
            if len(row) > 46 and row[46]:  # Check predicted_winner column
                games_with_predictions += 1
                matchup = f"{row[7]} @ {row[10]}" if len(row) > 10 else "Unknown"
                predicted_winner = row[46] if len(row) > 46 else "N/A"
                confidence = row[47] if len(row) > 47 else "N/A"
                print(f"  {i+1}. {matchup}: {predicted_winner} ({confidence} confidence)")
        
        if games_with_predictions > 0:
            print(f"\n✅ SUCCESS! Found {games_with_predictions} games with predictions!")
            print(f"📋 Your predictions are now in the upcoming_games tab")
            print(f"🎯 Look for columns: predicted_winner, confidence_score, etc.")
        else:
            print(f"\n⚠️ No predictions found in the first 10 rows")
    
    print("\n" + "=" * 60)
    print("🔍 VERIFICATION COMPLETE")

if __name__ == "__main__":
    main()



