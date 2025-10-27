#!/usr/bin/env python3

"""
Clean and Reorganize Sheet
=========================

This script cleans up the upcoming_games sheet and reorganizes columns properly
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

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
    
    print("🧹 Cleaning and Reorganizing upcoming_games Sheet")
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
    
    # Define the clean, organized structure
    print("🔧 Defining clean column structure...")
    
    # Original columns (first 45 columns should be the core game data)
    clean_headers = headers[:45]  # Keep original game data columns
    
    # Add clean prediction columns
    prediction_headers = [
        'predicted_winner',
        'confidence_score', 
        'predicted_spread',
        'predicted_total',
        'edge_vs_line',
        'line_movement',
        'sharp_money',
        'public_percentage',
        'value_rating',
        'home_win_probability',
        'away_win_probability',
        'betting_recommendation',
        'betting_value',
        'model_last_updated'
    ]
    
    # Add status columns
    status_headers = [
        'Last_Updated',
        'Auto_Update_Status'
    ]
    
    # Combine all headers
    final_headers = clean_headers + prediction_headers + status_headers
    
    print(f"✅ Clean structure: {len(final_headers)} columns")
    print(f"   - Original game data: {len(clean_headers)} columns")
    print(f"   - Prediction data: {len(prediction_headers)} columns")
    print(f"   - Status data: {len(status_headers)} columns")
    
    # Clear the entire sheet
    print("🧹 Clearing entire sheet...")
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range="upcoming_games!A:ZZ"
    ).execute()
    
    # Prepare clean data
    print("📝 Preparing clean data...")
    clean_data = []
    
    # Add headers
    clean_data.append(final_headers)
    
    # Process each data row
    for row in data_rows:
        # Take only the original game data columns
        clean_row = row[:45] if len(row) > 45 else row
        
        # Pad with empty strings for prediction columns
        while len(clean_row) < len(final_headers):
            clean_row.append('')
        
        clean_data.append(clean_row)
    
    # Write clean data back to sheet
    print("💾 Writing clean data to sheet...")
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="upcoming_games!A1",
        valueInputOption='USER_ENTERED',
        body={'values': clean_data}
    ).execute()
    
    print("✅ Sheet cleaned and reorganized!")
    print(f"✅ Restored {len(data_rows)} rows with clean structure")
    
    print("\n📋 CLEAN SHEET STRUCTURE:")
    print("   Columns 1-45: Original game data")
    print("   Columns 46-59: Prediction data (empty, ready for predictions)")
    print("   Columns 60-61: Status columns")
    
    print("\n🎯 Next step: Run predictions to populate the clean columns")

if __name__ == "__main__":
    main()



