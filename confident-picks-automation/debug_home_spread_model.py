#!/usr/bin/env python3

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
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

def analyze_home_spread_data():
    """Analyze the home spread data to understand the issue"""
    print("=" * 70)
    print("ANALYZING HOME SPREAD DATA")
    print("=" * 70)
    
    # Load historical data
    historical_df = load_sheet_data(SPREADSHEET_ID, 'historical_game_results_2021_2024')
    df_2025 = load_sheet_data(SPREADSHEET_ID, 'upcoming_games')
    
    print(f"Historical games: {len(historical_df)}")
    print(f"2025 games: {len(df_2025)}")
    
    # Check historical data
    print("\nHISTORICAL DATA ANALYSIS:")
    print("-" * 50)
    
    # Convert numeric columns
    numeric_cols = ['away_score', 'home_score', 'spread_line', 'total_line', 'result']
    for col in numeric_cols:
        if col in historical_df.columns:
            historical_df[col] = pd.to_numeric(historical_df[col], errors='coerce')
    
    # Filter completed games
    completed = historical_df[
        (historical_df['away_score'].notna()) & (historical_df['home_score'].notna()) &
        (historical_df['away_score'] != '') & (historical_df['home_score'] != '') &
        (historical_df['spread_line'].notna()) & (historical_df['spread_line'] != '') &
        (historical_df['result'].notna()) & (historical_df['result'] != '')
    ].copy()
    
    print(f"Completed games with spread data: {len(completed)}")
    
    # Analyze home cover rates
    home_covers = []
    for idx, row in completed.iterrows():
        try:
            away_score = float(row['away_score'])
            home_score = float(row['home_score'])
            spread_line = float(row['spread_line'])
            
            # Home cover: home team wins by more than the spread
            home_cover = 1 if (home_score - away_score) > spread_line else 0
            home_covers.append(home_cover)
        except (ValueError, TypeError):
            home_covers.append(0)
    
    home_cover_rate = sum(home_covers) / len(home_covers)
    print(f"Historical home cover rate: {home_cover_rate:.3f} ({sum(home_covers)}/{len(home_covers)})")
    
    # Check 2025 data
    print("\n2025 DATA ANALYSIS:")
    print("-" * 50)
    
    # Convert numeric columns for 2025
    for col in numeric_cols:
        if col in df_2025.columns:
            df_2025[col] = pd.to_numeric(df_2025[col], errors='coerce')
    
    # Check completed 2025 games
    completed_2025 = df_2025[
        (df_2025['away_score'].notna()) & (df_2025['home_score'].notna()) &
        (df_2025['away_score'] != '') & (df_2025['home_score'] != '') &
        (df_2025['spread_line'].notna()) & (df_2025['spread_line'] != '')
    ].copy()
    
    print(f"Completed 2025 games: {len(completed_2025)}")
    
    if len(completed_2025) > 0:
        # Analyze 2025 home cover rates
        home_covers_2025 = []
        for idx, row in completed_2025.iterrows():
            try:
                away_score = float(row['away_score'])
                home_score = float(row['home_score'])
                spread_line = float(row['spread_line'])
                
                home_cover = 1 if (home_score - away_score) > spread_line else 0
                home_covers_2025.append(home_cover)
            except (ValueError, TypeError):
                home_covers_2025.append(0)
        
        home_cover_rate_2025 = sum(home_covers_2025) / len(home_covers_2025)
        print(f"2025 home cover rate: {home_cover_rate_2025:.3f} ({sum(home_covers_2025)}/{len(home_covers_2025)})")
        
        # Check predictions vs actual
        if 'predicted_home_cover' in df_2025.columns:
            predictions = df_2025['predicted_home_cover'].iloc[:len(completed_2025)]
            print(f"\nPREDICTION ANALYSIS:")
            print(f"Predictions: {predictions.value_counts().to_dict()}")
            
            # Calculate accuracy
            correct = 0
            total = 0
            for i, (pred, actual) in enumerate(zip(predictions, home_covers_2025)):
                if i < len(home_covers_2025):
                    pred_val = 1 if pred == "YES" else 0
                    if pred_val == actual:
                        correct += 1
                    total += 1
            
            if total > 0:
                accuracy = correct / total
                print(f"Home spread accuracy: {accuracy:.3f} ({correct}/{total})")
    
    return completed, completed_2025

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

def test_improved_home_model():
    """Test improved home spread model"""
    print("\n" + "=" * 70)
    print("TESTING IMPROVED HOME SPREAD MODEL")
    print("=" * 70)
    
    # Load data
    historical_df = load_sheet_data(SPREADSHEET_ID, 'historical_game_results_2021_2024')
    df_2025 = load_sheet_data(SPREADSHEET_ID, 'upcoming_games')
    
    # Analyze data first
    completed, completed_2025 = analyze_home_spread_data()
    
    if len(completed) == 0:
        print("No historical data available!")
        return False
    
    # Create features
    df_with_features = create_improved_home_features(completed)
    
    # Feature columns
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
    
    # Create target
    y_home_cover = []
    for idx, row in df_with_features.iterrows():
        try:
            away_score = float(row['away_score'])
            home_score = float(row['home_score'])
            spread_line = float(row['spread_line'])
            
            home_cover = 1 if (home_score - away_score) > spread_line else 0
            y_home_cover.append(home_cover)
        except (ValueError, TypeError):
            y_home_cover.append(0)
    
    print(f"Training on {len(X)} games")
    print(f"Home cover rate: {sum(y_home_cover)/len(y_home_cover):.3f}")
    
    # Test multiple algorithms
    models = {
        'RandomForest': RandomForestClassifier(n_estimators=200, max_depth=15, min_samples_split=5, random_state=42),
        'GradientBoosting': GradientBoostingClassifier(n_estimators=200, max_depth=8, learning_rate=0.1, random_state=42),
        'AdaBoost': AdaBoostClassifier(n_estimators=200, learning_rate=0.8, random_state=42),
        'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42),
        'SVM': SVC(probability=True, random_state=42)
    }
    
    best_model = None
    best_score = 0
    
    print("\nTesting algorithms:")
    for name, model in models.items():
        scores = cross_val_score(model, X, y_home_cover, cv=5, scoring='accuracy')
        mean_score = scores.mean()
        std_score = scores.std()
        
        print(f"   {name}: {mean_score:.3f} (+/- {std_score:.3f})")
        
        if mean_score > best_score:
            best_score = mean_score
            best_model = model
    
    print(f"\nBest model: {best_score:.3f}")
    
    # Train best model
    best_model.fit(X, y_home_cover)
    
    # Test on 2025 data if available
    if len(completed_2025) > 0:
        print(f"\nTesting on {len(completed_2025)} 2025 games...")
        
        df_2025_features = create_improved_home_features(completed_2025)
        X_2025 = df_2025_features[feature_columns].copy().fillna(0)
        
        predictions = best_model.predict(X_2025)
        probabilities = best_model.predict_proba(X_2025)
        
        # Calculate actual home covers for 2025
        y_2025_actual = []
        for idx, row in completed_2025.iterrows():
            try:
                away_score = float(row['away_score'])
                home_score = float(row['home_score'])
                spread_line = float(row['spread_line'])
                
                home_cover = 1 if (home_score - away_score) > spread_line else 0
                y_2025_actual.append(home_cover)
            except (ValueError, TypeError):
                y_2025_actual.append(0)
        
        # Calculate accuracy
        correct = sum(1 for pred, actual in zip(predictions, y_2025_actual) if pred == actual)
        accuracy = correct / len(y_2025_actual)
        
        print(f"2025 Home Spread Accuracy: {accuracy:.3f} ({correct}/{len(y_2025_actual)})")
        
        # Show prediction distribution
        pred_counts = pd.Series(predictions).value_counts()
        actual_counts = pd.Series(y_2025_actual).value_counts()
        
        print(f"Predictions: {pred_counts.to_dict()}")
        print(f"Actual: {actual_counts.to_dict()}")
        
        return accuracy > 0.55  # Target accuracy
    
    return True

if __name__ == "__main__":
    success = test_improved_home_model()
    if success:
        print("\nImproved home spread model test completed!")
    else:
        print("\nHome spread model needs more work!")

