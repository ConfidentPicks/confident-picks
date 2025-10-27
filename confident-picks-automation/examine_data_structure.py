#!/usr/bin/env python3

import pandas as pd
import numpy as np
from google.oauth2 import service_account
from googleapiclient.discovery import build
import warnings
warnings.filterwarnings('ignore')

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'
SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU'

def get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

def load_sheet_data(spreadsheet_id, sheet_name, range_name=None):
    """Load data from Google Sheets"""
    service = get_sheets_service()
    
    if range_name is None:
        range_name = f"'{sheet_name}'!A:CZ"
    else:
        range_name = f"'{sheet_name}'!{range_name}"
    
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])

    if not values:
        return pd.DataFrame()

    headers = values[0]
    data = values[1:]

    max_cols = len(headers)
    for row in data:
        if len(row) > max_cols:
            max_cols = len(row)

    for i, row in enumerate(data):
        while len(row) < max_cols:
            row.append('')
        data[i] = row

    df = pd.DataFrame(data, columns=headers)
    return df

def examine_data_structure():
    """Examine the structure of the data"""
    print("EXAMINING DATA STRUCTURE")
    print("=" * 60)
    
    # Load historical data
    print("Loading historical data...")
    historical_df = load_sheet_data(SPREADSHEET_ID, 'historical_game_results_2021_2024')
    
    if historical_df.empty:
        print("Failed to load historical data!")
        return
    
    print(f"Loaded {len(historical_df)} historical games")
    print(f"Columns: {len(historical_df.columns)}")
    
    print("\nColumn names:")
    for i, col in enumerate(historical_df.columns):
        print(f"{i:2d}: {col}")
    
    print("\nFirst few rows:")
    print(historical_df.head())
    
    print("\nData types:")
    print(historical_df.dtypes)
    
    print("\nMissing values:")
    print(historical_df.isnull().sum())
    
    # Load upcoming games data
    print("\n" + "=" * 60)
    print("Loading upcoming games data...")
    upcoming_df = load_sheet_data(SPREADSHEET_ID, 'upcoming_games')
    
    if upcoming_df.empty:
        print("Failed to load upcoming games data!")
        return
    
    print(f"Loaded {len(upcoming_df)} upcoming games")
    print(f"Columns: {len(upcoming_df.columns)}")
    
    print("\nColumn names:")
    for i, col in enumerate(upcoming_df.columns):
        print(f"{i:2d}: {col}")
    
    print("\nFirst few rows:")
    print(upcoming_df.head())

def main():
    """Main function to examine data structure"""
    examine_data_structure()

if __name__ == "__main__":
    main()

