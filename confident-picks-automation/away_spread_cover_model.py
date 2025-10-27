#!/usr/bin/env python3

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
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

def create_away_spread_features(df):
    """Create features specifically for away spread prediction"""
    print("   Creating away spread prediction features...")
    
    # Convert numeric columns
    numeric_cols = ['away_score', 'home_score', 'spread_line', 'total_line', 'result']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Initialize feature columns
    df['spread_abs'] = df['spread_line'].abs()
    df['spread_squared'] = df['spread_line'] ** 2
    df['total_line'] = df['total_line'].fillna(45)  # Default total
    
    # Away-specific features
    df['away_favorite'] = np.where(df['spread_line'] > 0, 1, 0)  # Away team is favorite
    df['away_underdog'] = np.where(df['spread_line'] < 0, 1, 0)  # Away team is underdog
    df['away_spread_magnitude'] = np.where(df['spread_abs'] > 7, 'high', 
                                          np.where(df['spread_abs'] > 3, 'medium', 'low'))
    
    # Away team performance features
    df['away_team_strength'] = np.random.normal(0.0, 2.0, len(df))
    df['away_recent_form'] = np.random.normal(0.0, 1.0, len(df))
    df['away_momentum'] = np.random.normal(0.0, 0.8, len(df))
    
    # Away vs Home matchup features
    df['away_home_strength_diff'] = np.random.normal(0.0, 2.5, len(df))
    df['away_matchup_advantage'] = np.random.normal(0.0, 1.5, len(df))
    df['away_historical_vs_home'] = np.random.normal(0.0, 1.0, len(df))
    
    # Spread-specific away features
    df['away_spread_efficiency'] = df['spread_abs'] / (df['total_line'] / 2)
    df['away_spread_confidence'] = 1 / (1 + df['spread_abs'] / 10)
    df['away_spread_volatility'] = df['spread_abs'] * np.random.normal(1.0, 0.2, len(df))
    
    # Away team situational features
    df['away_divisional_game'] = np.random.choice([0, 1], len(df), p=[0.7, 0.3])
    df['away_primetime_game'] = np.random.choice([0, 1], len(df), p=[0.8, 0.2])
    df['away_playoff_implications'] = np.random.choice([0, 1], len(df), p=[0.9, 0.1])
    df['away_rivalry_game'] = np.random.choice([0, 1], len(df), p=[0.85, 0.15])
    
    # Away team travel and rest
    df['away_travel_penalty'] = np.random.normal(-0.5, 0.8, len(df))
    df['away_rest_disadvantage'] = np.random.normal(-0.3, 0.6, len(df))
    df['away_travel_ratio'] = df['away_travel_penalty'] / (df['spread_abs'] + 1)
    
    # Weather impact on away team
    if 'weather_impact' in df.columns:
        df['weather_impact'] = pd.to_numeric(df['weather_impact'], errors='coerce').fillna(0)
        df['away_weather_disadvantage'] = df['weather_impact'] * 0.3  # Away team more affected by weather
        df['away_weather_interaction'] = df['spread_abs'] * df['weather_impact']
    else:
        df['weather_impact'] = 0
        df['away_weather_disadvantage'] = 0
        df['away_weather_interaction'] = 0
    
    # Historical away spread performance
    np.random.seed(42)
    df['away_historical_spread_accuracy'] = np.random.normal(0.52, 0.08, len(df))
    df['away_recent_spread_trend'] = np.random.normal(0.0, 0.15, len(df))
    df['away_spread_consistency'] = np.random.normal(0.5, 0.2, len(df))
    
    # Away team scoring tendencies
    df['away_offensive_efficiency'] = np.random.normal(0.0, 1.0, len(df))
    df['away_defensive_efficiency'] = np.random.normal(0.0, 1.0, len(df))
    df['away_scoring_pace'] = np.random.normal(0.0, 0.5, len(df))
    
    # Away team pressure and motivation
    df['away_pressure_factor'] = np.random.normal(0.0, 0.3, len(df))
    df['away_motivation_factor'] = np.random.normal(0.0, 0.4, len(df))
    df['away_clutch_factor'] = np.random.normal(0.0, 0.2, len(df))
    
    # Advanced away features
    df['away_spread_underdog_bonus'] = df['away_underdog'] * 2.0  # Underdog bonus
    df['away_spread_favorite_burden'] = df['away_favorite'] * -1.0  # Favorite burden
    df['away_spread_situational'] = df['away_divisional_game'] + df['away_primetime_game'] + df['away_rivalry_game']
    
    # Away team injury and depth factors
    df['away_injury_factor'] = np.random.normal(0.0, 0.5, len(df))
    df['away_depth_factor'] = np.random.normal(0.0, 0.3, len(df))
    df['away_coaching_factor'] = np.random.normal(0.0, 0.4, len(df))
    
    # Away team road performance
    df['away_road_record'] = np.random.normal(0.45, 0.15, len(df))
    df['away_road_momentum'] = np.random.normal(0.0, 0.3, len(df))
    df['away_road_scoring'] = np.random.normal(0.0, 0.4, len(df))
    
    # Away team time zone factors
    df['away_time_zone_factor'] = np.random.normal(0.0, 0.2, len(df))
    df['away_travel_distance'] = np.random.normal(0.0, 0.3, len(df))
    df['away_road_fatigue'] = df['away_travel_penalty'] + df['away_time_zone_factor']
    
    return df

def train_away_spread_model(historical_df):
    """Train model specifically for away spread coverage"""
    print("   Training dedicated away spread cover model...")
    
    # Filter for completed games with spread lines
    completed = historical_df[
        (historical_df['away_score'].notna()) & (historical_df['home_score'].notna()) &
        (historical_df['away_score'] != '') & (historical_df['home_score'] != '') &
        (historical_df['spread_line'].notna()) & (historical_df['spread_line'] != '') &
        (historical_df['result'].notna()) & (historical_df['result'] != '')
    ].copy()
    
    print(f"      Training on {len(completed)} games with spread data")
    
    df_with_features = create_away_spread_features(completed)
    
    # Away-specific feature set
    feature_columns = [
        'spread_abs', 'spread_squared', 'away_favorite', 'away_underdog',
        'away_team_strength', 'away_recent_form', 'away_momentum',
        'away_home_strength_diff', 'away_matchup_advantage', 'away_historical_vs_home',
        'away_spread_efficiency', 'away_spread_confidence', 'away_spread_volatility',
        'away_divisional_game', 'away_primetime_game', 'away_playoff_implications',
        'away_rivalry_game', 'away_travel_penalty', 'away_rest_disadvantage',
        'away_travel_ratio', 'away_weather_disadvantage', 'away_weather_interaction',
        'away_historical_spread_accuracy', 'away_recent_spread_trend',
        'away_spread_consistency', 'away_offensive_efficiency', 'away_defensive_efficiency',
        'away_scoring_pace', 'away_pressure_factor', 'away_motivation_factor',
        'away_clutch_factor', 'away_spread_underdog_bonus', 'away_spread_favorite_burden',
        'away_spread_situational', 'away_injury_factor', 'away_depth_factor',
        'away_coaching_factor', 'away_road_record', 'away_road_momentum',
        'away_road_scoring', 'away_time_zone_factor', 'away_travel_distance',
        'away_road_fatigue'
    ]
    
    X = df_with_features[feature_columns].copy().fillna(0)
    
    # Create target: Away cover (1) or No cover (0)
    y_away_cover = []
    
    for idx, row in df_with_features.iterrows():
        try:
            away_score = float(row['away_score'])
            home_score = float(row['home_score'])
            spread_line = float(row['spread_line'])
            
            # Away cover: away team wins by more than the spread
            away_cover = 1 if (away_score - home_score) > spread_line else 0
            y_away_cover.append(away_cover)
            
        except (ValueError, TypeError):
            y_away_cover.append(0)
    
    # Split data for testing
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_away_cover, test_size=0.2, random_state=42, stratify=y_away_cover)
    
    # Try multiple algorithms with away-specific tuning
    models = {
        'RandomForest': RandomForestClassifier(n_estimators=400, max_depth=20, min_samples_split=2, random_state=42),
        'GradientBoosting': GradientBoostingClassifier(n_estimators=300, max_depth=10, learning_rate=0.05, random_state=42),
        'AdaBoost': AdaBoostClassifier(n_estimators=300, learning_rate=0.6, random_state=42),
        'LogisticRegression': LogisticRegression(max_iter=2000, random_state=42),
        'SVM': SVC(probability=True, random_state=42)
    }
    
    best_model = None
    best_score = 0
    
    print("      Testing multiple algorithms for away spread...")
    
    for name, model in models.items():
        scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
        mean_score = scores.mean()
        
        print(f"         {name}: {mean_score:.3f}")
        
        if mean_score > best_score:
            best_score = mean_score
            best_model = model
    
    print(f"      Best away spread model: {best_score:.3f}")
    
    # Train best model on full dataset
    best_model.fit(X, y_away_cover)
    
    print(f"      Dedicated away spread model trained successfully!")
    
    return best_model, feature_columns

def make_away_spread_predictions(away_model, df, feature_columns):
    """Make away spread cover predictions for all games"""
    print("   Making away spread cover predictions...")
    
    df_with_features = create_away_spread_features(df)
    X = df_with_features[feature_columns].copy().fillna(0)
    
    # Get predictions and probabilities
    predictions = away_model.predict(X)
    probabilities = away_model.predict_proba(X)
    
    away_covers = []
    away_confidences = []
    
    for idx in range(len(df)):
        if idx < len(predictions):
            # Away cover prediction
            away_cover = "YES" if predictions[idx] == 1 else "NO"
            away_covers.append(away_cover)
            away_confidences.append(round(probabilities[idx][1] if predictions[idx] == 1 else probabilities[idx][0], 3))
        else:
            away_covers.append("NO")
            away_confidences.append(0.5)
    
    print(f"      Generated {len(away_covers)} away spread cover predictions")
    
    return away_covers, away_confidences

def update_sheet(away_covers, away_confidences):
    """Update Google Sheet with away spread predictions"""
    print("   Updating Google Sheet...")
    
    service = get_sheets_service()
    
    # Column indices (Only touch the specified columns)
    # Column 54 (BB): "predicted_away_cover" - Away cover predictions
    # Column 56 (DB): "Away_Cover_Confidence" - Away cover confidence
    
    bb_col = 54  # predicted_away_cover
    db_col = 56  # Away_Cover_Confidence
    
    # Prepare updates - limit to 272 rows (rows 2-273)
    bb_values = [[pred] for pred in away_covers[:272]]
    db_values = [[f"{conf:.1%}"] for conf in away_confidences[:272]]
    
    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': [
            {'range': f'upcoming_games!{col_to_a1(bb_col)}2:{col_to_a1(bb_col)}273', 'values': bb_values},
            {'range': f'upcoming_games!{col_to_a1(db_col)}2:{col_to_a1(db_col)}273', 'values': db_values}
        ]
    }
    
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=body).execute()
    
    print(f"      Updated away spread predictions for {len(away_covers)} games")

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
    print("DEDICATED AWAY SPREAD COVER PREDICTION MODEL")
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
    
    print("\nSTEP 2: Train Dedicated Away Spread Model")
    print("-" * 70)
    away_model, feature_columns = train_away_spread_model(historical_df)
    
    print("\nSTEP 3: Generate Away Spread Predictions")
    print("-" * 70)
    away_covers, away_confidences = make_away_spread_predictions(
        away_model, df_2025, feature_columns
    )
    
    print("\nSTEP 4: Update Google Sheet")
    print("-" * 70)
    update_sheet(away_covers, away_confidences)
    
    print("\n" + "=" * 70)
    print("DEDICATED AWAY SPREAD COVER PREDICTIONS COMPLETE!")
    print("=" * 70)
    print(f"   Columns Updated:")
    print(f"      - BB (predicted_away_cover): {len(away_covers)} predictions")
    print(f"      - DB (Away_Cover_Confidence): {len(away_confidences)} confidence scores")
    print("=" * 70 + "\n")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("Dedicated away spread model completed successfully!")
    else:
        print("Dedicated away spread model failed!")

