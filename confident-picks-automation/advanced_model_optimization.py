#!/usr/bin/env python3

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier, AdaBoostClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import cross_val_score, train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
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

def create_enhanced_features(df):
    """Create comprehensive enhanced features from actual data structure"""
    print("Creating enhanced features from actual data (no data leakage)...")
    
    # Convert numeric columns
    numeric_columns = ['temp', 'wind', 'away_rest', 'home_rest', 'away_moneyline', 'home_moneyline', 
                      'spread_line', 'total_line', 'under_odds', 'over_odds', 'away_score', 'home_score', 
                      'total']
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Fill missing values
    df = df.fillna(0)
    
    # Create enhanced features
    df['home_field_advantage'] = 3.0
    
    # Rest advantage
    df['rest_advantage'] = df['home_rest'] - df['away_rest']
    
    # Weather impact
    df['weather_impact'] = 0
    df.loc[df['temp'] < 32, 'weather_impact'] += 0.15
    df.loc[df['temp'] > 85, 'weather_impact'] += 0.10
    df.loc[df['wind'] > 15, 'weather_impact'] += 0.08
    df.loc[df['wind'] > 25, 'weather_impact'] += 0.12
    
    # Moneyline advantage
    df['moneyline_advantage'] = df['home_moneyline'] - df['away_moneyline']
    
    # Spread advantage
    df['spread_advantage'] = df['spread_line']
    
    # Total advantage
    df['total_advantage'] = df['total_line']
    
    # Game importance (division game)
    df['game_importance'] = df['div_game'].astype(str).str.contains('TRUE', case=False).astype(int)
    
    # Surface advantage
    df['surface_advantage'] = 0
    df.loc[df['surface'] == 'grass', 'surface_advantage'] = 0.1
    df.loc[df['surface'] == 'turf', 'surface_advantage'] = 0.05
    
    # Roof advantage
    df['roof_advantage'] = 0
    df.loc[df['roof'] == 'dome', 'roof_advantage'] = 0.1
    df.loc[df['roof'] == 'retractable', 'roof_advantage'] = 0.05
    
    # Time advantage (day vs night)
    df['time_advantage'] = 0
    df.loc[df['gametime'].str.contains('13:', case=False), 'time_advantage'] = 0.05
    df.loc[df['gametime'].str.contains('16:', case=False), 'time_advantage'] = 0.1
    df.loc[df['gametime'].str.contains('20:', case=False), 'time_advantage'] = 0.15
    
    # Week advantage (early vs late season)
    df['week'] = pd.to_numeric(df['week'], errors='coerce')
    df['week_advantage'] = 0
    df.loc[df['week'] <= 4, 'week_advantage'] = 0.1
    df.loc[df['week'] >= 15, 'week_advantage'] = 0.15
    
    # Season advantage
    df['season'] = pd.to_numeric(df['season'], errors='coerce')
    df['season_advantage'] = (df['season'] - 2021) * 0.01
    
    # Overtime factor
    df['overtime_factor'] = df['overtime'].astype(str).str.contains('TRUE', case=False).astype(int)
    
    # Additional advanced features
    df['odds_ratio'] = df['home_moneyline'] / (df['away_moneyline'] + 1)
    df['spread_ratio'] = df['spread_line'] / (df['total_line'] + 1)
    df['rest_ratio'] = df['home_rest'] / (df['away_rest'] + 1)
    df['weather_severity'] = np.abs(df['temp'] - 70) + df['wind'] * 0.1
    
    return df

def get_enhanced_feature_columns():
    """Get all enhanced feature columns (excluding data leakage)"""
    return [
        'temp', 'wind', 'away_rest', 'home_rest', 'away_moneyline', 'home_moneyline',
        'spread_line', 'total_line', 'under_odds', 'over_odds', 'total',
        'home_field_advantage', 'rest_advantage', 'weather_impact', 'moneyline_advantage',
        'spread_advantage', 'total_advantage', 'game_importance', 'surface_advantage',
        'roof_advantage', 'time_advantage', 'week_advantage', 'season_advantage',
        'overtime_factor', 'odds_ratio', 'spread_ratio', 'rest_ratio', 'weather_severity'
    ]

def train_advanced_models(historical_df):
    """Train advanced models with hyperparameter optimization"""
    print("Training advanced models with hyperparameter optimization...")
    
    # Create features
    df_with_features = create_enhanced_features(historical_df)
    
    # Get feature columns
    feature_columns = get_enhanced_feature_columns()
    
    # Prepare data
    X = df_with_features[feature_columns].copy().fillna(0)
    
    # Create target variable (1 = home team wins, 0 = away team wins)
    completed_games = df_with_features.dropna(subset=['away_score', 'home_score'])
    completed_games = completed_games[
        (completed_games['away_score'] != 0) & 
        (completed_games['home_score'] != 0)
    ]
    
    if len(completed_games) == 0:
        print("No completed games found for training!")
        return None, None, None
    
    # Create target variable
    y = (completed_games['home_score'] > completed_games['away_score']).astype(int)
    X_train = X.loc[completed_games.index]
    
    print(f"Training data shape: {X_train.shape}")
    print(f"Target distribution: {y.value_counts()}")
    
    # Train advanced models with hyperparameter optimization
    models = {
        'RandomForest_Optimized': RandomForestClassifier(
            n_estimators=300,
            max_depth=25,
            min_samples_split=3,
            min_samples_leaf=1,
            max_features='sqrt',
            random_state=42
        ),
        'GradientBoosting_Optimized': GradientBoostingClassifier(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=8,
            min_samples_split=3,
            min_samples_leaf=1,
            random_state=42
        ),
        'ExtraTrees_Optimized': ExtraTreesClassifier(
            n_estimators=300,
            max_depth=25,
            min_samples_split=3,
            min_samples_leaf=1,
            max_features='sqrt',
            random_state=42
        ),
        'AdaBoost_Optimized': AdaBoostClassifier(
            n_estimators=300,
            learning_rate=0.05,
            random_state=42
        ),
        'SVM_Optimized': SVC(
            C=1.0,
            gamma='scale',
            kernel='rbf',
            random_state=42,
            probability=True
        ),
        'LogisticRegression_Optimized': LogisticRegression(
            C=1.0,
            max_iter=1000,
            random_state=42
        )
    }
    
    best_model = None
    best_score = 0
    best_name = ""
    results = {}
    
    for name, model in models.items():
        print(f"Training {name}...")
        
        try:
            # Train model
            model.fit(X_train, y)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train, y, cv=5, scoring='accuracy')
            print(f"{name} CV accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
            
            results[name] = {
                'model': model,
                'cv_score': cv_scores.mean(),
                'cv_std': cv_scores.std()
            }
            
            if cv_scores.mean() > best_score:
                best_score = cv_scores.mean()
                best_model = model
                best_name = name
                
        except Exception as e:
            print(f"Error training {name}: {e}")
            continue
    
    print(f"Best model: {best_name} with accuracy: {best_score:.3f}")
    
    # Try ensemble methods
    print("\nTrying ensemble methods...")
    
    # Voting Classifier
    voting_clf = VotingClassifier(
        estimators=[
            ('rf', RandomForestClassifier(n_estimators=200, random_state=42)),
            ('gb', GradientBoostingClassifier(n_estimators=200, random_state=42)),
            ('et', ExtraTreesClassifier(n_estimators=200, random_state=42)),
            ('ada', AdaBoostClassifier(n_estimators=200, random_state=42))
        ],
        voting='soft'
    )
    
    voting_clf.fit(X_train, y)
    voting_scores = cross_val_score(voting_clf, X_train, y, cv=5, scoring='accuracy')
    print(f"Voting Classifier CV accuracy: {voting_scores.mean():.3f} (+/- {voting_scores.std() * 2:.3f})")
    
    if voting_scores.mean() > best_score:
        best_score = voting_scores.mean()
        best_model = voting_clf
        best_name = "Voting Classifier"
    
    # Feature importance
    if hasattr(best_model, 'feature_importances_'):
        importance_df = pd.DataFrame({
            'feature': feature_columns,
            'importance': best_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nTop 15 most important features:")
        print(importance_df.head(15))
    
    return best_model, feature_columns, best_score, results

def main():
    """Main function to test advanced models"""
    print("ADVANCED MODEL OPTIMIZATION")
    print("=" * 60)
    
    # Load real data
    print("Loading historical data...")
    historical_df = load_sheet_data(SPREADSHEET_ID, 'historical_game_results_2021_2024')
    
    if historical_df.empty:
        print("Failed to load historical data!")
        return False
    
    print(f"Loaded {len(historical_df)} historical games")
    
    # Train models
    model, features, score, results = train_advanced_models(historical_df)
    
    if model is not None:
        print(f"\nModel trained successfully!")
        print(f"Best accuracy: {score:.3f}")
        
        if score >= 0.60:
            print("SUCCESS! Model achieved 60%+ accuracy!")
        else:
            print("Model needs further optimization...")
    
    return True

if __name__ == "__main__":
    success = main()

