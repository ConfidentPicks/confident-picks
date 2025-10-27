#!/usr/bin/env python3

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score
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

def create_clean_features(df):
    """Create clean features with NO data leakage - only use pre-game information"""
    print("   Creating clean features with NO data leakage...")
    
    # Convert numeric columns
    numeric_cols = ['away_score', 'home_score', 'spread_line', 'total_line']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # ONLY use features that would be available BEFORE the game
    # Basic spread information
    df['spread_abs'] = df['spread_line'].abs()
    df['spread_squared'] = df['spread_line'] ** 2
    df['total_line'] = df['total_line'].fillna(45)
    
    # Home team favorite/underdog status
    df['home_favorite'] = np.where(df['spread_line'] < 0, 1, 0)
    df['home_underdog'] = np.where(df['spread_line'] > 0, 1, 0)
    
    # Spread magnitude categories
    df['spread_small'] = np.where(df['spread_abs'] <= 3, 1, 0)
    df['spread_medium'] = np.where((df['spread_abs'] > 3) & (df['spread_abs'] <= 7), 1, 0)
    df['spread_large'] = np.where(df['spread_abs'] > 7, 1, 0)
    
    # Basic ratios
    df['spread_to_total_ratio'] = df['spread_abs'] / df['total_line']
    
    # Weather information (if available)
    if 'temp' in df.columns:
        df['temp'] = pd.to_numeric(df['temp'], errors='coerce').fillna(70)
        df['cold_weather'] = np.where(df['temp'] < 40, 1, 0)
        df['hot_weather'] = np.where(df['temp'] > 80, 1, 0)
    else:
        df['temp'] = 70
        df['cold_weather'] = 0
        df['hot_weather'] = 0
    
    # Wind information (if available)
    if 'wind' in df.columns:
        df['wind'] = pd.to_numeric(df['wind'], errors='coerce').fillna(0)
        df['high_wind'] = np.where(df['wind'] > 15, 1, 0)
    else:
        df['wind'] = 0
        df['high_wind'] = 0
    
    # Roof information (if available)
    if 'roof' in df.columns:
        df['dome_game'] = np.where(df['roof'] == 'dome', 1, 0)
    else:
        df['dome_game'] = 0
    
    # Divisional game (if available)
    if 'div_game' in df.columns:
        df['div_game'] = pd.to_numeric(df['div_game'], errors='coerce').fillna(0)
    else:
        df['div_game'] = 0
    
    # Rest days (if available)
    if 'home_rest' in df.columns:
        df['home_rest'] = pd.to_numeric(df['home_rest'], errors='coerce').fillna(7)
        df['away_rest'] = pd.to_numeric(df['away_rest'], errors='coerce').fillna(7)
        df['rest_advantage'] = df['home_rest'] - df['away_rest']
    else:
        df['home_rest'] = 7
        df['away_rest'] = 7
        df['rest_advantage'] = 0
    
    # Week information (if available)
    if 'week' in df.columns:
        df['week'] = pd.to_numeric(df['week'], errors='coerce').fillna(1)
        df['early_season'] = np.where(df['week'] <= 4, 1, 0)
        df['late_season'] = np.where(df['week'] >= 15, 1, 0)
    else:
        df['week'] = 1
        df['early_season'] = 0
        df['late_season'] = 0
    
    return df

def train_clean_home_spread_model(historical_df):
    """Train clean model with NO data leakage"""
    print("   Training clean home spread model with NO data leakage...")
    
    # Filter for completed games with spread lines
    completed = historical_df[
        (historical_df['away_score'].notna()) & (historical_df['home_score'].notna()) &
        (historical_df['away_score'] != '') & (historical_df['home_score'] != '') &
        (historical_df['spread_line'].notna()) & (historical_df['spread_line'] != '')
    ].copy()
    
    print(f"      Training on {len(completed)} games with spread data")
    
    df_with_features = create_clean_features(completed)
    
    # ONLY use features that would be available BEFORE the game
    feature_columns = [
        'spread_abs', 'spread_squared', 'home_favorite', 'home_underdog',
        'spread_small', 'spread_medium', 'spread_large', 'spread_to_total_ratio',
        'temp', 'cold_weather', 'hot_weather', 'wind', 'high_wind',
        'dome_game', 'div_game', 'rest_advantage', 'early_season', 'late_season'
    ]
    
    X = df_with_features[feature_columns].copy().fillna(0)
    
    # Create target: Home cover (1) or No cover (0)
    y_home_cover = []
    
    for idx, row in df_with_features.iterrows():
        try:
            away_score = float(row['away_score'])
            home_score = float(row['home_score'])
            spread_line = float(row['spread_line'])
            
            # Home cover: home team wins by more than the spread
            home_cover = 1 if (home_score - away_score) > spread_line else 0
            y_home_cover.append(home_cover)
            
        except (ValueError, TypeError):
            y_home_cover.append(0)
    
    print(f"      Home cover rate: {sum(y_home_cover)/len(y_home_cover):.3f}")
    
    # Split data for testing
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_home_cover, test_size=0.2, random_state=42, stratify=y_home_cover)
    
    # Use simple RandomForest with conservative parameters
    model = RandomForestClassifier(
        n_estimators=100, 
        max_depth=10, 
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42
    )
    
    # Cross-validation to check for overfitting
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
    mean_score = scores.mean()
    std_score = scores.std()
    
    print(f"      Cross-validation accuracy: {mean_score:.3f} (+/- {std_score:.3f})")
    
    # Train model on full dataset
    model.fit(X, y_home_cover)
    
    print(f"      Clean home spread model trained successfully!")
    
    return model, feature_columns

def make_clean_home_spread_predictions(model, df, feature_columns):
    """Make clean home spread cover predictions"""
    print("   Making clean home spread cover predictions...")
    
    df_with_features = create_clean_features(df)
    X = df_with_features[feature_columns].copy().fillna(0)
    
    # Get predictions and probabilities
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)
    
    home_covers = []
    home_confidences = []
    
    for idx in range(len(df)):
        if idx < len(predictions):
            # Home cover prediction
            home_cover = "YES" if predictions[idx] == 1 else "NO"
            home_covers.append(home_cover)
            home_confidences.append(round(probabilities[idx][1] if predictions[idx] == 1 else probabilities[idx][0], 3))
        else:
            home_covers.append("NO")
            home_confidences.append(0.5)
    
    print(f"      Generated {len(home_covers)} clean home spread cover predictions")
    
    return home_covers, home_confidences

def update_sheet_ay_only(home_covers):
    """Update ONLY column AY (predicted_home_cover) - no other columns"""
    print("   Updating ONLY column AY (predicted_home_cover)...")
    
    service = get_sheets_service()
    
    # Column AY (50): "predicted_home_cover" - Home cover predictions ONLY
    ay_col = 50  # predicted_home_cover
    
    # Prepare updates - limit to 272 rows (rows 2-273)
    ay_values = [[pred] for pred in home_covers[:272]]
    
    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': [
            {'range': f'upcoming_games!{col_to_a1(ay_col)}2:{col_to_a1(ay_col)}273', 'values': ay_values}
        ]
    }
    
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=body).execute()
    
    print(f"      Updated ONLY column AY for {len(home_covers)} games")

def col_to_a1(col_num):
    """Convert column number to A1 notation"""
    result = ""
    while col_num > 0:
        col_num -= 1
        result = chr(col_num % 26 + ord('A')) + result
        col_num //= 26
    return result

def main():
    print("\n" + "=" * 70)
    print("CLEAN HOME SPREAD MODEL - NO DATA LEAKAGE")
    print("=" * 70)
    
    print("\nSTEP 1: Load Data")
    print("-" * 70)
    historical_df = load_sheet_data(SPREADSHEET_ID, 'historical_game_results_2021_2024')
    df_2025 = load_sheet_data(SPREADSHEET_ID, 'upcoming_games')
    
    if historical_df.empty or df_2025.empty:
        print("Failed to load data!")
        return False
    
    print(f"   Loaded {len(historical_df)} historical games")
    print(f"   Loaded {len(df_2025)} 2025 games")
    
    print("\nSTEP 2: Train Clean Home Spread Model")
    print("-" * 70)
    model, feature_columns = train_clean_home_spread_model(historical_df)
    
    print("\nSTEP 3: Generate Clean Home Spread Predictions")
    print("-" * 70)
    home_covers, home_confidences = make_clean_home_spread_predictions(
        model, df_2025, feature_columns
    )
    
    print("\nSTEP 4: Update ONLY Column AY")
    print("-" * 70)
    update_sheet_ay_only(home_covers)
    
    print("\n" + "=" * 70)
    print("CLEAN HOME SPREAD PREDICTIONS COMPLETE!")
    print("=" * 70)
    print(f"   Updated ONLY:")
    print(f"      - AY (predicted_home_cover): {len(home_covers)} predictions")
    print("   NO OTHER COLUMNS TOUCHED!")
    print("=" * 70 + "\n")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("Clean home spread model completed successfully!")
    else:
        print("Clean home spread model failed!")

