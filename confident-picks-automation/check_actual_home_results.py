#!/usr/bin/env python3

import pandas as pd
import numpy as np
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import warnings
warnings.filterwarnings('ignore')

# Configuration
SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU'
SERVICE_ACCOUNT_FILE = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_sheets_service():
    """Get Google Sheets service"""
    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('sheets', 'v4', credentials=credentials)

def load_sheet_data(spreadsheet_id, sheet_name, range_name=None):
    """Load data from Google Sheets with improved error handling"""
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

    # Find the maximum number of columns across all rows
    max_cols = len(headers)
    for row in data:
        if len(row) > max_cols:
            max_cols = len(row)

    # Ensure all rows have the same number of columns
    for i, row in enumerate(data):
        while len(row) < max_cols:
            row.append('')
        data[i] = row

    # Create DataFrame with proper column handling
    df = pd.DataFrame(data)
    if len(headers) < max_cols:
        # Extend headers if needed
        extended_headers = headers + [f'col_{i}' for i in range(len(headers), max_cols)]
        df.columns = extended_headers
    else:
        df.columns = headers
    
    return df

def check_actual_home_spread_results():
    """Check the actual home spread results in the spreadsheet"""
    print("=" * 70)
    print("CHECKING ACTUAL HOME SPREAD RESULTS")
    print("=" * 70)
    
    # Load 2025 data
    df_2025 = load_sheet_data(SPREADSHEET_ID, 'upcoming_games')
    
    print(f"Loaded {len(df_2025)} 2025 games")
    print(f"Columns: {list(df_2025.columns)}")
    
    # Convert numeric columns
    numeric_cols = ['away_score', 'home_score', 'spread_line']
    for col in numeric_cols:
        if col in df_2025.columns:
            df_2025[col] = pd.to_numeric(df_2025[col], errors='coerce')
    
    # Filter completed games
    completed_2025 = df_2025[
        (df_2025['away_score'].notna()) & (df_2025['home_score'].notna()) &
        (df_2025['away_score'] != '') & (df_2025['home_score'] != '') &
        (df_2025['spread_line'].notna()) & (df_2025['spread_line'] != '')
    ].copy()
    
    print(f"Completed 2025 games: {len(completed_2025)}")
    
    if len(completed_2025) == 0:
        print("No completed 2025 games found!")
        return
    
    # Show first few completed games
    print("\nFirst 10 completed games:")
    print("-" * 50)
    for i, (idx, row) in enumerate(completed_2025.head(10).iterrows()):
        try:
            away_score = float(row['away_score'])
            home_score = float(row['home_score'])
            spread_line = float(row['spread_line'])
            
            # Calculate actual home cover
            home_cover_actual = "YES" if (home_score - away_score) > spread_line else "NO"
            
            # Get prediction if available
            home_cover_pred = row.get('predicted_home_cover', 'N/A')
            
            print(f"Game {i+1}: Home {home_score} vs Away {away_score}, Spread: {spread_line}")
            print(f"  Actual Home Cover: {home_cover_actual}")
            print(f"  Predicted Home Cover: {home_cover_pred}")
            print()
            
        except (ValueError, TypeError) as e:
            print(f"Game {i+1}: Error processing - {e}")
            print()
    
    # Calculate overall accuracy
    print("OVERALL ACCURACY CALCULATION:")
    print("-" * 50)
    
    correct = 0
    total = 0
    
    for idx, row in completed_2025.iterrows():
        try:
            away_score = float(row['away_score'])
            home_score = float(row['home_score'])
            spread_line = float(row['spread_line'])
            
            # Actual home cover
            home_cover_actual = 1 if (home_score - away_score) > spread_line else 0
            
            # Predicted home cover
            home_cover_pred = row.get('predicted_home_cover', '')
            home_cover_pred_val = 1 if home_cover_pred == "YES" else 0
            
            if home_cover_pred in ["YES", "NO"]:
                if home_cover_actual == home_cover_pred_val:
                    correct += 1
                total += 1
                
        except (ValueError, TypeError):
            continue
    
    if total > 0:
        accuracy = correct / total
        print(f"ACTUAL HOME SPREAD ACCURACY: {accuracy:.3f} ({correct}/{total})")
        
        if accuracy >= 0.60:
            print("SUCCESS: Home spread accuracy is 60%+ as required!")
        else:
            print("FAILURE: Home spread accuracy is below 60%")
    else:
        print("No valid predictions found!")

def check_recent_games():
    """Check the most recent games to see current performance"""
    print("\n" + "=" * 70)
    print("CHECKING RECENT GAMES")
    print("=" * 70)
    
    # Load 2025 data
    df_2025 = load_sheet_data(SPREADSHEET_ID, 'upcoming_games')
    
    # Convert numeric columns
    numeric_cols = ['away_score', 'home_score', 'spread_line']
    for col in numeric_cols:
        if col in df_2025.columns:
            df_2025[col] = pd.to_numeric(df_2025[col], errors='coerce')
    
    # Filter completed games
    completed_2025 = df_2025[
        (df_2025['away_score'].notna()) & (df_2025['home_score'].notna()) &
        (df_2025['away_score'] != '') & (df_2025['home_score'] != '') &
        (df_2025['spread_line'].notna()) & (df_2025['spread_line'] != '')
    ].copy()
    
    # Get last 20 games
    recent_games = completed_2025.tail(20)
    
    print(f"Last 20 completed games:")
    print("-" * 50)
    
    correct = 0
    total = 0
    
    for i, (idx, row) in enumerate(recent_games.iterrows()):
        try:
            away_score = float(row['away_score'])
            home_score = float(row['home_score'])
            spread_line = float(row['spread_line'])
            
            # Calculate actual home cover
            home_cover_actual = "YES" if (home_score - away_score) > spread_line else "NO"
            
            # Get prediction if available
            home_cover_pred = row.get('predicted_home_cover', 'N/A')
            
            # Check if prediction is correct
            is_correct = "CORRECT" if home_cover_pred == home_cover_actual else "WRONG"
            
            if home_cover_pred in ["YES", "NO"]:
                if home_cover_pred == home_cover_actual:
                    correct += 1
                total += 1
            
            print(f"Game {i+1}: Home {home_score} vs Away {away_score}, Spread: {spread_line}")
            print(f"  Actual: {home_cover_actual}, Predicted: {home_cover_pred} - {is_correct}")
            print()
            
        except (ValueError, TypeError) as e:
            print(f"Game {i+1}: Error processing - {e}")
            print()
    
    if total > 0:
        accuracy = correct / total
        print(f"RECENT 20 GAMES HOME SPREAD ACCURACY: {accuracy:.3f} ({correct}/{total})")

if __name__ == "__main__":
    check_actual_home_spread_results()
    check_recent_games()

