#!/usr/bin/env python3

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
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

def verify_2025_home_spread_accuracy():
    """Verify the 2025 home spread accuracy is actually high"""
    print("=" * 70)
    print("VERIFYING 2025 HOME SPREAD ACCURACY")
    print("=" * 70)
    
    # Load 2025 data
    df_2025 = load_sheet_data(SPREADSHEET_ID, 'upcoming_games')
    
    print(f"Loaded {len(df_2025)} 2025 games")
    
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
        return False
    
    # Calculate actual home covers
    actual_home_covers = []
    for idx, row in completed_2025.iterrows():
        try:
            away_score = float(row['away_score'])
            home_score = float(row['home_score'])
            spread_line = float(row['spread_line'])
            
            # Home cover: home team wins by more than the spread
            home_cover = 1 if (home_score - away_score) > spread_line else 0
            actual_home_covers.append(home_cover)
        except (ValueError, TypeError):
            actual_home_covers.append(0)
    
    actual_home_cover_rate = sum(actual_home_covers) / len(actual_home_covers)
    print(f"Actual 2025 home cover rate: {actual_home_cover_rate:.3f} ({sum(actual_home_covers)}/{len(actual_home_covers)})")
    
    # Get predictions
    if 'predicted_home_cover' in df_2025.columns:
        predictions = df_2025['predicted_home_cover'].iloc[:len(completed_2025)]
        print(f"Predictions: {predictions.value_counts().to_dict()}")
        
        # Calculate accuracy
        correct = 0
        total = 0
        for i, (pred, actual) in enumerate(zip(predictions, actual_home_covers)):
            if i < len(actual_home_covers):
                pred_val = 1 if pred == "YES" else 0
                if pred_val == actual:
                    correct += 1
                total += 1
        
        if total > 0:
            accuracy = correct / total
            print(f"\n2025 HOME SPREAD ACCURACY: {accuracy:.3f} ({correct}/{total})")
            
            if accuracy >= 0.60:
                print("SUCCESS: Home spread accuracy is 60%+ as required!")
                return True
            else:
                print("FAILURE: Home spread accuracy is below 60%")
                return False
    else:
        print("No predictions found in the data!")
        return False

def test_all_models_2025_accuracy():
    """Test all models on 2025 data"""
    print("\n" + "=" * 70)
    print("TESTING ALL MODELS ON 2025 DATA")
    print("=" * 70)
    
    # Load 2025 data
    df_2025 = load_sheet_data(SPREADSHEET_ID, 'upcoming_games')
    
    # Convert numeric columns
    numeric_cols = ['away_score', 'home_score', 'spread_line', 'total_line']
    for col in numeric_cols:
        if col in df_2025.columns:
            df_2025[col] = pd.to_numeric(df_2025[col], errors='coerce')
    
    # Filter completed games
    completed_2025 = df_2025[
        (df_2025['away_score'].notna()) & (df_2025['home_score'].notna()) &
        (df_2025['away_score'] != '') & (df_2025['home_score'] != '') &
        (df_2025['spread_line'].notna()) & (df_2025['spread_line'] != '')
    ].copy()
    
    print(f"Testing on {len(completed_2025)} completed 2025 games")
    
    if len(completed_2025) == 0:
        print("No completed 2025 games found!")
        return False
    
    # Test Winner Predictions
    if 'predicted_winner' in df_2025.columns:
        winner_predictions = df_2025['predicted_winner'].iloc[:len(completed_2025)]
        winner_actuals = []
        
        for idx, row in completed_2025.iterrows():
            try:
                away_score = float(row['away_score'])
                home_score = float(row['home_score'])
                winner = 'home' if home_score > away_score else 'away'
                winner_actuals.append(winner)
            except (ValueError, TypeError):
                winner_actuals.append('away')
        
        winner_correct = sum(1 for pred, actual in zip(winner_predictions, winner_actuals) if pred == actual)
        winner_accuracy = winner_correct / len(winner_actuals)
        print(f"Winner Accuracy: {winner_accuracy:.3f} ({winner_correct}/{len(winner_actuals)})")
    
    # Test Home Spread Predictions
    if 'predicted_home_cover' in df_2025.columns:
        home_predictions = df_2025['predicted_home_cover'].iloc[:len(completed_2025)]
        home_actuals = []
        
        for idx, row in completed_2025.iterrows():
            try:
                away_score = float(row['away_score'])
                home_score = float(row['home_score'])
                spread_line = float(row['spread_line'])
                home_cover = 1 if (home_score - away_score) > spread_line else 0
                home_actuals.append(home_cover)
            except (ValueError, TypeError):
                home_actuals.append(0)
        
        home_correct = sum(1 for pred, actual in zip(home_predictions, home_actuals) 
                          if (1 if pred == "YES" else 0) == actual)
        home_accuracy = home_correct / len(home_actuals)
        print(f"Home Spread Accuracy: {home_accuracy:.3f} ({home_correct}/{len(home_actuals)})")
    
    # Test Away Spread Predictions
    if 'predicted_away_cover' in df_2025.columns:
        away_predictions = df_2025['predicted_away_cover'].iloc[:len(completed_2025)]
        away_actuals = []
        
        for idx, row in completed_2025.iterrows():
            try:
                away_score = float(row['away_score'])
                home_score = float(row['home_score'])
                spread_line = float(row['spread_line'])
                away_cover = 1 if (away_score - home_score) > spread_line else 0
                away_actuals.append(away_cover)
            except (ValueError, TypeError):
                away_actuals.append(0)
        
        away_correct = sum(1 for pred, actual in zip(away_predictions, away_actuals) 
                          if (1 if pred == "YES" else 0) == actual)
        away_accuracy = away_correct / len(away_actuals)
        print(f"Away Spread Accuracy: {away_accuracy:.3f} ({away_correct}/{len(away_actuals)})")
    
    # Test Total Predictions
    if 'predicted_total' in df_2025.columns:
        total_predictions = df_2025['predicted_total'].iloc[:len(completed_2025)]
        total_actuals = []
        
        for idx, row in completed_2025.iterrows():
            try:
                away_score = float(row['away_score'])
                home_score = float(row['home_score'])
                total_line = float(row['total_line'])
                total_over = 1 if (away_score + home_score) > total_line else 0
                total_actuals.append(total_over)
            except (ValueError, TypeError):
                total_actuals.append(0)
        
        total_correct = sum(1 for pred, actual in zip(total_predictions, total_actuals) 
                           if (1 if pred == "OVER" else 0) == actual)
        total_accuracy = total_correct / len(total_actuals)
        print(f"Total Accuracy: {total_accuracy:.3f} ({total_correct}/{len(total_actuals)})")
    
    return True

if __name__ == "__main__":
    print("Testing 2025 accuracy for all models...")
    
    # Test home spread accuracy specifically
    home_success = verify_2025_home_spread_accuracy()
    
    # Test all models
    all_success = test_all_models_2025_accuracy()
    
    if home_success:
        print("\nHOME SPREAD MODEL VERIFICATION PASSED!")
        print("The improved home spread model is performing at 60%+ accuracy on 2025 data.")
    else:
        print("\nHOME SPREAD MODEL VERIFICATION FAILED!")
        print("The home spread model needs further improvement.")
