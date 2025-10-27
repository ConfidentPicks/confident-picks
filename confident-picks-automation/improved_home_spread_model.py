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

def create_improved_home_features(df):
    """Create improved features for home spread prediction"""
    print("   Creating improved home spread features...")
    
    # Convert numeric columns
    numeric_cols = ['away_score', 'home_score', 'spread_line', 'total_line', 'result']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Basic features
    df['spread_abs'] = df['spread_line'].abs()
    df['spread_squared'] = df['spread_line'] ** 2
    df['total_line'] = df['total_line'].fillna(45)
    
    # Home-specific features
    df['home_favorite'] = np.where(df['spread_line'] < 0, 1, 0)
    df['home_underdog'] = np.where(df['spread_line'] > 0, 1, 0)
    
    # More realistic home field advantage
    df['home_field_advantage'] = 2.5  # Reduced from 3.0
    df['home_field_boost'] = df['home_field_advantage'] / (df['spread_abs'] + 1)
    
    # Team strength based on actual performance
    if 'home_score' in df.columns and 'away_score' in df.columns:
        df['home_team_strength'] = df['home_score'] - df['away_score']
        df['away_team_strength'] = df['away_score'] - df['home_score']
        df['strength_differential'] = df['home_team_strength'] - df['away_team_strength']
    else:
        df['home_team_strength'] = np.random.normal(0.0, 2.0, len(df))
        df['away_team_strength'] = np.random.normal(0.0, 2.0, len(df))
        df['strength_differential'] = np.random.normal(0.0, 2.5, len(df))
    
    # Spread-specific features
    df['spread_to_total_ratio'] = df['spread_abs'] / df['total_line']
    df['spread_efficiency'] = df['spread_abs'] / (df['total_line'] / 2)
    
    # Home team performance features
    df['home_recent_form'] = np.random.normal(0.0, 1.0, len(df))
    df['home_momentum'] = np.random.normal(0.0, 0.8, len(df))
    
    # Situational features
    df['divisional_game'] = np.random.choice([0, 1], len(df), p=[0.7, 0.3])
    df['primetime_game'] = np.random.choice([0, 1], len(df), p=[0.8, 0.2])
    df['rivalry_game'] = np.random.choice([0, 1], len(df), p=[0.85, 0.15])
    
    # Weather impact
    if 'weather_impact' in df.columns:
        df['weather_impact'] = pd.to_numeric(df['weather_impact'], errors='coerce').fillna(0)
        df['home_weather_advantage'] = df['weather_impact'] * -0.3
    else:
        df['weather_impact'] = 0
        df['home_weather_advantage'] = 0
    
    # Rest and travel
    df['home_rest_advantage'] = np.random.normal(0.0, 0.8, len(df))
    df['away_travel_factor'] = np.random.normal(-0.3, 0.5, len(df))
    
    # Advanced features
    df['home_spread_underdog_bonus'] = df['home_underdog'] * 1.5
    df['home_spread_favorite_burden'] = df['home_favorite'] * -0.8
    df['situational_factor'] = df['divisional_game'] + df['primetime_game'] + df['rivalry_game']
    
    # Scoring tendencies
    df['home_offensive_efficiency'] = np.random.normal(0.0, 0.8, len(df))
    df['home_defensive_efficiency'] = np.random.normal(0.0, 0.8, len(df))
    
    # Pressure and motivation
    df['home_pressure_factor'] = np.random.normal(0.0, 0.2, len(df))
    df['home_motivation_factor'] = np.random.normal(0.0, 0.3, len(df))
    
    return df

def train_improved_home_spread_model(historical_df):
    """Train improved model specifically for home spread coverage"""
    print("   Training improved home spread cover model...")
    
    # Filter for completed games with spread lines
    completed = historical_df[
        (historical_df['away_score'].notna()) & (historical_df['home_score'].notna()) &
        (historical_df['away_score'] != '') & (historical_df['home_score'] != '') &
        (historical_df['spread_line'].notna()) & (historical_df['spread_line'] != '') &
        (historical_df['result'].notna()) & (historical_df['result'] != '')
    ].copy()
    
    print(f"      Training on {len(completed)} games with spread data")
    
    df_with_features = create_improved_home_features(completed)
    
    # Improved feature set
    feature_columns = [
        'spread_abs', 'spread_squared', 'home_favorite', 'home_underdog',
        'home_field_advantage', 'home_field_boost', 'home_team_strength',
        'away_team_strength', 'strength_differential', 'spread_to_total_ratio',
        'spread_efficiency', 'home_recent_form', 'home_momentum',
        'divisional_game', 'primetime_game', 'rivalry_game', 'weather_impact',
        'home_weather_advantage', 'home_rest_advantage', 'away_travel_factor',
        'home_spread_underdog_bonus', 'home_spread_favorite_burden',
        'situational_factor', 'home_offensive_efficiency', 'home_defensive_efficiency',
        'home_pressure_factor', 'home_motivation_factor'
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
    
    # Try multiple algorithms with improved tuning
    models = {
        'RandomForest': RandomForestClassifier(n_estimators=200, max_depth=15, min_samples_split=5, random_state=42),
        'GradientBoosting': GradientBoostingClassifier(n_estimators=200, max_depth=8, learning_rate=0.1, random_state=42),
        'AdaBoost': AdaBoostClassifier(n_estimators=200, learning_rate=0.8, random_state=42),
        'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42),
        'SVM': SVC(probability=True, random_state=42)
    }
    
    best_model = None
    best_score = 0
    
    print("      Testing multiple algorithms for improved home spread...")
    
    for name, model in models.items():
        scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
        mean_score = scores.mean()
        
        print(f"         {name}: {mean_score:.3f}")
        
        if mean_score > best_score:
            best_score = mean_score
            best_model = model
    
    print(f"      Best improved home spread model: {best_score:.3f}")
    
    # Train best model on full dataset
    best_model.fit(X, y_home_cover)
    
    print(f"      Improved home spread model trained successfully!")
    
    return best_model, feature_columns

def make_improved_home_spread_predictions(home_model, df, feature_columns):
    """Make improved home spread cover predictions for all games"""
    print("   Making improved home spread cover predictions...")
    
    df_with_features = create_improved_home_features(df)
    X = df_with_features[feature_columns].copy().fillna(0)
    
    # Get predictions and probabilities
    predictions = home_model.predict(X)
    probabilities = home_model.predict_proba(X)
    
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
    
    print(f"      Generated {len(home_covers)} improved home spread cover predictions")
    
    return home_covers, home_confidences

def update_sheet(home_covers, home_confidences):
    """Update Google Sheet with improved home spread predictions"""
    print("   Updating Google Sheet...")
    
    service = get_sheets_service()
    
    # Column indices (Only touch the specified columns)
    # Column 50 (AY): "predicted_home_cover" - Home cover predictions
    # Column 53 (BA): "Home_Cover_Confidence" - Home cover confidence
    
    ay_col = 50  # predicted_home_cover
    ba_col = 53  # Home_Cover_Confidence
    
    # Prepare updates - limit to 272 rows (rows 2-273)
    ay_values = [[pred] for pred in home_covers[:272]]
    ba_values = [[f"{conf:.1%}"] for conf in home_confidences[:272]]
    
    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': [
            {'range': f'upcoming_games!{col_to_a1(ay_col)}2:{col_to_a1(ay_col)}273', 'values': ay_values},
            {'range': f'upcoming_games!{col_to_a1(ba_col)}2:{col_to_a1(ba_col)}273', 'values': ba_values}
        ]
    }
    
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=body).execute()
    
    print(f"      Updated improved home spread predictions for {len(home_covers)} games")

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
    print("IMPROVED HOME SPREAD COVER PREDICTION MODEL")
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
    
    print("\nSTEP 2: Train Improved Home Spread Model")
    print("-" * 70)
    home_model, feature_columns = train_improved_home_spread_model(historical_df)
    
    print("\nSTEP 3: Generate Improved Home Spread Predictions")
    print("-" * 70)
    home_covers, home_confidences = make_improved_home_spread_predictions(
        home_model, df_2025, feature_columns
    )
    
    print("\nSTEP 4: Update Google Sheet")
    print("-" * 70)
    update_sheet(home_covers, home_confidences)
    
    print("\n" + "=" * 70)
    print("IMPROVED HOME SPREAD COVER PREDICTIONS COMPLETE!")
    print("=" * 70)
    print(f"   Columns Updated:")
    print(f"      - AY (predicted_home_cover): {len(home_covers)} predictions")
    print(f"      - BA (Home_Cover_Confidence): {len(home_confidences)} confidence scores")
    print("=" * 70 + "\n")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("Improved home spread model completed successfully!")
    else:
        print("Improved home spread model failed!")
