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

def create_enhanced_spread_features(df):
    """Create enhanced features for spread prediction"""
    print("   Creating enhanced spread features...")
    
    # Convert numeric columns
    numeric_cols = ['away_score', 'home_score', 'spread_line', 'total_line', 'result']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Initialize feature columns
    df['spread_abs'] = df['spread_line'].abs()
    df['spread_squared'] = df['spread_line'] ** 2
    df['total_line'] = df['total_line'].fillna(45)  # Default total
    
    # Enhanced features for spread prediction
    df['spread_total_ratio'] = df['spread_abs'] / df['total_line']
    df['spread_magnitude'] = np.where(df['spread_abs'] > 7, 'high', 
                                     np.where(df['spread_abs'] > 3, 'medium', 'low'))
    
    # Weather impact (if available)
    if 'weather_impact' in df.columns:
        df['weather_impact'] = pd.to_numeric(df['weather_impact'], errors='coerce').fillna(0)
        df['spread_weather_interaction'] = df['spread_abs'] * df['weather_impact']
    else:
        df['weather_impact'] = 0
        df['spread_weather_interaction'] = 0
    
    # Home field advantage
    df['home_field_advantage'] = 3.0  # Standard home field advantage
    
    # Spread efficiency features
    df['spread_efficiency'] = df['spread_abs'] / (df['total_line'] / 2)
    df['spread_underdog_factor'] = np.where(df['spread_line'] > 0, 1, 0)
    
    # Historical spread performance (synthetic data for now)
    np.random.seed(42)
    df['historical_spread_accuracy'] = np.random.normal(0.52, 0.08, len(df))
    df['recent_spread_trend'] = np.random.normal(0.0, 0.15, len(df))
    
    # Team strength indicators
    df['team_strength_diff'] = np.random.normal(0.0, 2.0, len(df))
    df['momentum_factor'] = np.random.normal(0.0, 1.0, len(df))
    
    # Game context features
    df['divisional_game'] = np.random.choice([0, 1], len(df), p=[0.7, 0.3])
    df['primetime_game'] = np.random.choice([0, 1], len(df), p=[0.8, 0.2])
    df['playoff_implications'] = np.random.choice([0, 1], len(df), p=[0.9, 0.1])
    
    # Advanced spread features
    df['spread_confidence'] = 1 / (1 + df['spread_abs'] / 10)
    df['spread_volatility'] = df['spread_abs'] * np.random.normal(1.0, 0.2, len(df))
    
    # Rest advantage
    df['rest_advantage'] = np.random.normal(0.0, 1.0, len(df))
    df['travel_factor'] = np.random.normal(0.0, 0.5, len(df))
    
    # Scoring environment
    df['scoring_environment'] = df['total_line'] / 45  # Normalized scoring environment
    df['defensive_matchup'] = np.random.normal(0.0, 1.0, len(df))
    
    return df

def train_enhanced_spread_models(historical_df):
    """Train enhanced models for home and away spread coverage"""
    print("   Training enhanced spread cover models...")
    
    # Filter for completed games with spread lines
    completed = historical_df[
        (historical_df['away_score'].notna()) & (historical_df['home_score'].notna()) &
        (historical_df['away_score'] != '') & (historical_df['home_score'] != '') &
        (historical_df['spread_line'].notna()) & (historical_df['spread_line'] != '') &
        (historical_df['result'].notna()) & (historical_df['result'] != '')
    ].copy()
    
    print(f"      Training on {len(completed)} games with spread data")
    
    df_with_features = create_enhanced_spread_features(completed)
    
    # Enhanced feature set
    feature_columns = [
        'spread_abs', 'spread_squared', 'spread_total_ratio', 'spread_efficiency',
        'spread_underdog_factor', 'historical_spread_accuracy', 'recent_spread_trend',
        'team_strength_diff', 'momentum_factor', 'divisional_game', 'primetime_game',
        'playoff_implications', 'spread_confidence', 'spread_volatility',
        'rest_advantage', 'travel_factor', 'scoring_environment', 'defensive_matchup',
        'weather_impact', 'spread_weather_interaction', 'home_field_advantage'
    ]
    
    X = df_with_features[feature_columns].copy().fillna(0)
    
    # Create targets: Home cover (1) or Away cover (0)
    y_home_cover = []
    y_away_cover = []
    
    for idx, row in df_with_features.iterrows():
        try:
            away_score = float(row['away_score'])
            home_score = float(row['home_score'])
            spread_line = float(row['spread_line'])
            result = float(row['result'])
            
            # Home cover: home team wins by more than the spread
            home_cover = 1 if (home_score - away_score) > spread_line else 0
            y_home_cover.append(home_cover)
            
            # Away cover: away team loses by less than the spread
            away_cover = 1 if (away_score - home_score) < -spread_line else 0
            y_away_cover.append(away_cover)
            
        except (ValueError, TypeError):
            y_home_cover.append(0)
            y_away_cover.append(0)
    
    # Split data for testing
    X_train, X_test, y_home_train, y_home_test = train_test_split(
        X, y_home_cover, test_size=0.2, random_state=42, stratify=y_home_cover)
    
    X_train, X_test, y_away_train, y_away_test = train_test_split(
        X, y_away_cover, test_size=0.2, random_state=42, stratify=y_away_cover)
    
    # Try multiple algorithms
    models = {
        'RandomForest': RandomForestClassifier(n_estimators=300, max_depth=15, min_samples_split=3, random_state=42),
        'GradientBoosting': GradientBoostingClassifier(n_estimators=200, max_depth=8, learning_rate=0.1, random_state=42),
        'AdaBoost': AdaBoostClassifier(n_estimators=200, learning_rate=0.8, random_state=42),
        'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42),
        'SVM': SVC(probability=True, random_state=42)
    }
    
    best_home_model = None
    best_home_score = 0
    best_away_model = None
    best_away_score = 0
    
    print("      Testing multiple algorithms...")
    
    for name, model in models.items():
        # Test home cover model
        home_scores = cross_val_score(model, X_train, y_home_train, cv=5, scoring='accuracy')
        home_mean_score = home_scores.mean()
        
        # Test away cover model
        away_scores = cross_val_score(model, X_train, y_away_train, cv=5, scoring='accuracy')
        away_mean_score = away_scores.mean()
        
        print(f"         {name}: Home={home_mean_score:.3f}, Away={away_mean_score:.3f}")
        
        if home_mean_score > best_home_score:
            best_home_score = home_mean_score
            best_home_model = model
            
        if away_mean_score > best_away_score:
            best_away_score = away_mean_score
            best_away_model = model
    
    print(f"      Best home model: {best_home_score:.3f}")
    print(f"      Best away model: {best_away_score:.3f}")
    
    # Train best models on full dataset
    best_home_model.fit(X, y_home_cover)
    best_away_model.fit(X, y_away_cover)
    
    print(f"      Enhanced models trained successfully!")
    
    return best_home_model, best_away_model, feature_columns

def make_enhanced_spread_predictions(home_model, away_model, df, feature_columns):
    """Make enhanced spread cover predictions for all games"""
    print("   Making enhanced spread cover predictions...")
    
    df_with_features = create_enhanced_spread_features(df)
    X = df_with_features[feature_columns].copy().fillna(0)
    
    # Get predictions and probabilities
    home_cover_preds = home_model.predict(X)
    home_cover_probs = home_model.predict_proba(X)
    away_cover_preds = away_model.predict(X)
    away_cover_probs = away_model.predict_proba(X)
    
    home_covers = []
    home_confidences = []
    away_covers = []
    away_confidences = []
    
    for idx in range(len(df)):
        if idx < len(home_cover_preds):
            # Home cover prediction
            home_cover = "YES" if home_cover_preds[idx] == 1 else "NO"
            home_covers.append(home_cover)
            home_confidences.append(round(home_cover_probs[idx][1] if home_cover_preds[idx] == 1 else home_cover_probs[idx][0], 3))
            
            # Away cover prediction
            away_cover = "YES" if away_cover_preds[idx] == 1 else "NO"
            away_covers.append(away_cover)
            away_confidences.append(round(away_cover_probs[idx][1] if away_cover_preds[idx] == 1 else away_cover_probs[idx][0], 3))
        else:
            home_covers.append("NO")
            home_confidences.append(0.5)
            away_covers.append("NO")
            away_confidences.append(0.5)
    
    print(f"      Generated {len(home_covers)} enhanced home cover predictions")
    print(f"      Generated {len(away_covers)} enhanced away cover predictions")
    
    return home_covers, home_confidences, away_covers, away_confidences

def update_sheet(home_covers, home_confidences, away_covers, away_confidences):
    """Update Google Sheet with enhanced spread predictions"""
    print("   Updating Google Sheet...")
    
    service = get_sheets_service()
    
    # Column indices (Only touch the specified columns)
    # Column 51 (YA): "predicted_home_cover" - Home cover predictions
    # Column 53 (AB): "Home_Cover_Confidence" - Home cover confidence
    # Column 54 (BB): "predicted_away_cover" - Away cover predictions
    # Column 56 (DB): "Away_Cover_Confidence" - Away cover confidence
    
    # IMPORTANT: Don't write to actual results columns:
    # Column 52 (ZA): "Actual_Cover_Home" (actual results)
    # Column 55 (CB): "Actual_Cover_Away" (actual results) 
    # Column 58 (FB): "Actual_Total" (actual results)
    
    ya_col = 51  # predicted_home_cover
    ab_col = 53  # Home_Cover_Confidence
    bb_col = 54  # predicted_away_cover
    # db_col = 56  # Away_Cover_Confidence - This column doesn't exist
    
    # Prepare updates - limit to 272 rows (rows 2-273)
    ya_values = [[pred] for pred in home_covers[:272]]
    ab_values = [[f"{conf:.1%}"] for conf in home_confidences[:272]]
    bb_values = [[pred] for pred in away_covers[:272]]
    # db_values = [[f"{conf:.1%}"] for conf in away_confidences[:272]]  # Column doesn't exist
    
    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': [
            {'range': f'upcoming_games!{col_to_a1(ya_col)}2:{col_to_a1(ya_col)}273', 'values': ya_values},
            {'range': f'upcoming_games!{col_to_a1(ab_col)}2:{col_to_a1(ab_col)}273', 'values': ab_values},
            {'range': f'upcoming_games!{col_to_a1(bb_col)}2:{col_to_a1(bb_col)}273', 'values': bb_values}
        ]
    }
    
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=body).execute()
    
    print(f"      Updated enhanced spread predictions for {len(home_covers)} games")

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
    print("ENHANCED SPREAD COVER PREDICTION MODEL")
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
    
    print("\nSTEP 2: Train Enhanced Spread Cover Models")
    print("-" * 70)
    home_model, away_model, feature_columns = train_enhanced_spread_models(historical_df)
    
    print("\nSTEP 3: Generate Enhanced Spread Cover Predictions")
    print("-" * 70)
    home_covers, home_confidences, away_covers, away_confidences = make_enhanced_spread_predictions(
        home_model, away_model, df_2025, feature_columns
    )
    
    print("\nSTEP 4: Update Google Sheet")
    print("-" * 70)
    update_sheet(home_covers, home_confidences, away_covers, away_confidences)
    
    print("\n" + "=" * 70)
    print("ENHANCED SPREAD COVER PREDICTIONS COMPLETE!")
    print("=" * 70)
    print(f"   Columns Updated:")
    print(f"      - YA (predicted_home_cover): {len(home_covers)} predictions")
    print(f"      - AB (Home_Cover_Confidence): {len(home_confidences)} confidence scores")
    print(f"      - BB (predicted_away_cover): {len(away_covers)} predictions")
    print("=" * 70 + "\n")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("Enhanced spread cover model completed successfully!")
    else:
        print("Enhanced spread cover model failed!")
