#!/usr/bin/env python3

"""
Revert and Cleanup Live Picks Sheet
==================================

This script reverts the live_picks_sheets to its original state
and removes the prediction columns I added
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
    
    print("🔧 Reverting live_picks_sheets to original state...")
    
    # Get current data
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="live_picks_sheets!A:ZZ"
    ).execute()
    
    values = result.get('values', [])
    
    if not values or len(values) < 2:
        print("❌ No data found")
        return
    
    headers = values[0]
    data_rows = values[1:]
    
    print(f"Found {len(data_rows)} data rows")
    print(f"Original headers: {headers[:35]}")  # Show first 35 columns
    
    # Find the original end of headers (before my additions)
    original_end = 35  # Based on what we saw earlier
    
    # Restore original headers and data
    original_headers = headers[:original_end]
    
    # Clear the entire sheet first
    print("Clearing entire sheet...")
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range="live_picks_sheets!A:ZZ"
    ).execute()
    
    # Write back only the original data
    print("Restoring original data...")
    all_rows = [original_headers]
    
    for row in data_rows:
        # Only keep the original columns
        original_row = row[:original_end] if len(row) > original_end else row
        all_rows.append(original_row)
    
    # Write back the original data
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="live_picks_sheets!A1",
        valueInputOption='USER_ENTERED',
        body={'values': all_rows}
    ).execute()
    
    print("✅ Successfully reverted live_picks_sheets to original state!")
    print(f"✅ Restored {len(original_headers)} original columns")
    print(f"✅ Restored {len(data_rows)} data rows")
    
    print("\n📋 Your live_picks_sheets tab is now back to its original state")
    print("   All the prediction columns I added have been removed")

if __name__ == "__main__":
    main()



