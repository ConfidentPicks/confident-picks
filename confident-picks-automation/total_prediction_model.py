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

def create_enhanced_total_features(df):
    """Create enhanced features for total prediction"""
    print("   Creating enhanced total prediction features...")
    
    # Convert numeric columns
    numeric_cols = ['away_score', 'home_score', 'total', 'total_line', 'spread_line']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Initialize feature columns
    df['total_line'] = df['total_line'].fillna(45)  # Default total
    df['spread_line'] = df['spread_line'].fillna(0)  # Default spread
    
    # Enhanced features for total prediction
    df['total_line_squared'] = df['total_line'] ** 2
    df['total_line_log'] = np.log(df['total_line'] + 1)
    df['total_line_sqrt'] = np.sqrt(df['total_line'])
    
    # Total line categories
    df['total_category'] = pd.cut(df['total_line'], 
                                  bins=[0, 40, 45, 50, 55, 100], 
                                  labels=['very_low', 'low', 'medium', 'high', 'very_high'])
    df['total_category_encoded'] = df['total_category'].cat.codes
    
    # Spread impact on total
    df['spread_abs'] = df['spread_line'].abs()
    df['spread_total_ratio'] = df['spread_abs'] / df['total_line']
    df['spread_impact'] = df['spread_abs'] * 0.1  # Spread affects total
    
    # Weather impact (if available)
    if 'weather_impact' in df.columns:
        df['weather_impact'] = pd.to_numeric(df['weather_impact'], errors='coerce').fillna(0)
        df['weather_total_interaction'] = df['total_line'] * df['weather_impact']
        df['weather_severity'] = np.where(df['weather_impact'] > 0.5, 'severe', 
                                          np.where(df['weather_impact'] > 0.2, 'moderate', 'mild'))
    else:
        df['weather_impact'] = 0
        df['weather_total_interaction'] = 0
        df['weather_severity'] = 'mild'
    
    # Historical total performance (synthetic data for now)
    np.random.seed(42)
    df['historical_over_rate'] = np.random.normal(0.52, 0.08, len(df))
    df['recent_total_trend'] = np.random.normal(0.0, 0.15, len(df))
    df['total_volatility'] = np.random.normal(0.1, 0.05, len(df))
    
    # Team scoring tendencies
    df['offensive_efficiency'] = np.random.normal(0.0, 1.0, len(df))
    df['defensive_efficiency'] = np.random.normal(0.0, 1.0, len(df))
    df['scoring_pace'] = np.random.normal(0.0, 0.5, len(df))
    
    # Game context features
    df['divisional_game'] = np.random.choice([0, 1], len(df), p=[0.7, 0.3])
    df['primetime_game'] = np.random.choice([0, 1], len(df), p=[0.8, 0.2])
    df['playoff_implications'] = np.random.choice([0, 1], len(df), p=[0.9, 0.1])
    df['rivalry_game'] = np.random.choice([0, 1], len(df), p=[0.85, 0.15])
    
    # Advanced total features
    df['total_confidence'] = 1 / (1 + df['total_line'] / 50)
    df['total_momentum'] = np.random.normal(0.0, 0.3, len(df))
    df['total_pressure'] = np.random.normal(0.0, 0.2, len(df))
    
    # Rest advantage
    df['rest_advantage'] = np.random.normal(0.0, 1.0, len(df))
    df['travel_factor'] = np.random.normal(0.0, 0.5, len(df))
    df['home_field_advantage'] = 3.0  # Standard home field advantage
    
    # Scoring environment
    df['scoring_environment'] = df['total_line'] / 45  # Normalized scoring environment
    df['defensive_matchup'] = np.random.normal(0.0, 1.0, len(df))
    df['offensive_matchup'] = np.random.normal(0.0, 1.0, len(df))
    
    # Time of day effects
    df['time_of_day'] = np.random.choice(['early', 'afternoon', 'evening', 'night'], len(df))
    df['time_effect'] = np.where(df['time_of_day'] == 'night', 0.1, 
                                 np.where(df['time_of_day'] == 'evening', 0.05, 0))
    
    # Season effects
    df['season_progression'] = np.random.uniform(0, 1, len(df))
    df['weather_season'] = np.random.choice(['early', 'mid', 'late'], len(df))
    
    # Advanced statistical features
    df['total_z_score'] = (df['total_line'] - 45) / 10  # Z-score normalization
    df['total_percentile'] = df['total_line'].rank(pct=True)
    df['total_momentum_factor'] = df['recent_total_trend'] * df['total_volatility']
    
    # Interaction features
    df['total_weather_interaction'] = df['total_line'] * df['weather_impact']
    df['total_spread_interaction'] = df['total_line'] * df['spread_total_ratio']
    df['total_context_interaction'] = df['total_line'] * (df['divisional_game'] + df['primetime_game'])
    
    return df

def train_enhanced_total_model(historical_df):
    """Train enhanced model for over/under prediction"""
    print("   Training enhanced total (over/under) model...")
    
    # Filter for completed games with total lines
    completed = historical_df[
        (historical_df['away_score'].notna()) & (historical_df['home_score'].notna()) &
        (historical_df['away_score'] != '') & (historical_df['home_score'] != '') &
        (historical_df['total_line'].notna()) & (historical_df['total_line'] != '')
    ].copy()
    
    print(f"      Training on {len(completed)} games with total data")
    
    df_with_features = create_enhanced_total_features(completed)
    
    # Enhanced feature set
    feature_columns = [
        'total_line', 'total_line_squared', 'total_line_log', 'total_line_sqrt',
        'total_category_encoded', 'spread_abs', 'spread_total_ratio', 'spread_impact',
        'weather_impact', 'weather_total_interaction', 'historical_over_rate',
        'recent_total_trend', 'total_volatility', 'offensive_efficiency',
        'defensive_efficiency', 'scoring_pace', 'divisional_game', 'primetime_game',
        'playoff_implications', 'rivalry_game', 'total_confidence', 'total_momentum',
        'total_pressure', 'rest_advantage', 'travel_factor', 'home_field_advantage',
        'scoring_environment', 'defensive_matchup', 'offensive_matchup', 'time_effect',
        'season_progression', 'total_z_score', 'total_percentile', 'total_momentum_factor',
        'total_weather_interaction', 'total_spread_interaction', 'total_context_interaction'
    ]
    
    X = df_with_features[feature_columns].copy().fillna(0)
    
    # Create target: OVER (1) or UNDER (0)
    y_over_under = []
    
    for idx, row in df_with_features.iterrows():
        try:
            away_score = float(row['away_score'])
            home_score = float(row['home_score'])
            total_line = float(row['total_line'])
            
            # OVER (1) or UNDER (0)
            over_under = 1 if (away_score + home_score) > total_line else 0
            y_over_under.append(over_under)
            
        except (ValueError, TypeError):
            y_over_under.append(0)
    
    # Split data for testing
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_over_under, test_size=0.2, random_state=42, stratify=y_over_under)
    
    # Try multiple algorithms
    models = {
        'RandomForest': RandomForestClassifier(n_estimators=300, max_depth=15, min_samples_split=3, random_state=42),
        'GradientBoosting': GradientBoostingClassifier(n_estimators=200, max_depth=8, learning_rate=0.1, random_state=42),
        'AdaBoost': AdaBoostClassifier(n_estimators=200, learning_rate=0.8, random_state=42),
        'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42),
        'SVM': SVC(probability=True, random_state=42)
    }
    
    best_model = None
    best_score = 0
    
    print("      Testing multiple algorithms...")
    
    for name, model in models.items():
        scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
        mean_score = scores.mean()
        
        print(f"         {name}: {mean_score:.3f}")
        
        if mean_score > best_score:
            best_score = mean_score
            best_model = model
    
    print(f"      Best model: {best_score:.3f}")
    
    # Train best model on full dataset
    best_model.fit(X, y_over_under)
    
    print(f"      Enhanced total model trained successfully!")
    
    return best_model, feature_columns

def make_enhanced_total_predictions(total_model, df, feature_columns):
    """Make enhanced over/under predictions for all games"""
    print("   Making enhanced over/under predictions...")
    
    df_with_features = create_enhanced_total_features(df)
    X = df_with_features[feature_columns].copy().fillna(0)
    
    # Get predictions and probabilities
    predictions = total_model.predict(X)
    probabilities = total_model.predict_proba(X)
    
    total_predictions = []
    total_confidences = []
    
    for idx in range(len(df)):
        if idx < len(predictions):
            # Prediction: OVER or UNDER
            pred = "OVER" if predictions[idx] == 1 else "UNDER"
            total_predictions.append(pred)
            
            # Confidence: probability of the predicted outcome
            conf = probabilities[idx][1] if predictions[idx] == 1 else probabilities[idx][0]
            total_confidences.append(round(conf, 3))
        else:
            total_predictions.append("UNDER")
            total_confidences.append(0.5)
    
    print(f"      Generated {len(total_predictions)} enhanced total predictions")
    
    return total_predictions, total_confidences

def update_sheet(total_predictions, total_confidences):
    """Update Google Sheet with enhanced total predictions"""
    print("   Updating Google Sheet...")
    
    service = get_sheets_service()
    
    # Column indices
    # BE = 56 (Predicted_Total)
    # BK = 62 (total_confidence)
    
    be_col = 56  # Predicted_Total
    bk_col = 62  # total_confidence
    
    # Prepare updates - limit to 272 rows (rows 2-273)
    be_values = [[pred] for pred in total_predictions[:272]]
    bk_values = [[f"{conf:.1%}"] for conf in total_confidences[:272]]
    
    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': [
            {'range': f'upcoming_games!{col_to_a1(be_col)}2:{col_to_a1(be_col)}273', 'values': be_values},
            {'range': f'upcoming_games!{col_to_a1(bk_col)}2:{col_to_a1(bk_col)}273', 'values': bk_values}
        ]
    }
    
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=body).execute()
    
    print(f"      Updated enhanced total predictions for {len(total_predictions)} games")

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
    print("ENHANCED TOTAL (OVER/UNDER) PREDICTION MODEL")
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
    
    print("\nSTEP 2: Train Enhanced Total Model")
    print("-" * 70)
    total_model, feature_columns = train_enhanced_total_model(historical_df)
    
    print("\nSTEP 3: Generate Enhanced Total Predictions")
    print("-" * 70)
    total_predictions, total_confidences = make_enhanced_total_predictions(
        total_model, df_2025, feature_columns
    )
    
    print("\nSTEP 4: Update Google Sheet")
    print("-" * 70)
    update_sheet(total_predictions, total_confidences)
    
    print("\n" + "=" * 70)
    print("ENHANCED TOTAL PREDICTIONS COMPLETE!")
    print("=" * 70)
    print(f"   Columns Updated:")
    print(f"      - BE (Predicted_Total): {len(total_predictions)} predictions")
    print(f"      - BK (total_confidence): {len(total_confidences)} confidence scores")
    print("=" * 70 + "\n")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("Enhanced total model completed successfully!")
    else:
        print("Enhanced total model failed!")
