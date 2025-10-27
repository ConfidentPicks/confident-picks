#!/usr/bin/env python3

"""
Final Prediction Summary
=======================

This script shows you exactly where your predictions are located
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
    
    print("🏈 NFL PREDICTION SYSTEM - FINAL SUMMARY")
    print("=" * 60)
    
    # Check live_picks_sheets
    print("\n📊 LIVE PICKS SHEETS TAB:")
    print("-" * 30)
    
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="live_picks_sheets!A:ZZ"
    ).execute()
    
    values = result.get('values', [])
    
    if values and len(values) > 1:
        headers = values[0]
        data_rows = values[1:]
        
        print(f"✅ Found {len(data_rows)} games with predictions")
        print(f"📋 Headers: {len(headers)} columns")
        
        # Show prediction columns
        prediction_cols = []
        for i, header in enumerate(headers):
            if any(word in header.lower() for word in ['predicted', 'confidence', 'betting', 'probability']):
                prediction_cols.append(f"Column {chr(65+i)}: {header}")
        
        print(f"\n🎯 PREDICTION COLUMNS ({len(prediction_cols)}):")
        for col in prediction_cols:
            print(f"  • {col}")
        
        # Show sample predictions
        print(f"\n📈 SAMPLE PREDICTIONS (First 5 games):")
        for i, row in enumerate(data_rows[:5]):
            matchup = row[1] if len(row) > 1 else "Unknown"
            confidence = row[46] if len(row) > 46 else "N/A"
            recommendation = row[47] if len(row) > 47 else "N/A"
            print(f"  {i+1}. {matchup}: {confidence} confidence - {recommendation}")
    
    print("\n" + "=" * 60)
    print("✅ PREDICTIONS ARE NOW LIVE IN YOUR GOOGLE SHEET!")
    print("\n📋 WHERE TO FIND YOUR PREDICTIONS:")
    print("  1. Open your Google Sheet: My_NFL_Betting_Data1")
    print("  2. Click on the 'live_picks_sheets' tab")
    print("  3. Scroll to the right to see prediction columns")
    print("  4. Look for columns with:")
    print("     • predicted_winner")
    print("     • home_win_probability") 
    print("     • away_win_probability")
    print("     • confidence_score")
    print("     • betting_recommendation")
    print("     • betting_value")
    print("     • model_last_updated")
    
    print("\n🔄 TO UPDATE PREDICTIONS:")
    print("  Run: python add_predictions_to_live_picks.py")

if __name__ == "__main__":
    main()



