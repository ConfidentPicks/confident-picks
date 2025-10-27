#!/usr/bin/env python3

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import cross_val_score, train_test_split, GridSearchCV
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
    """Create comprehensive enhanced features"""
    print("Creating enhanced features...")
    
    # Basic features
    df['away_win_pct'] = pd.to_numeric(df['away_win_pct'], errors='coerce')
    df['home_win_pct'] = pd.to_numeric(df['home_win_pct'], errors='coerce')
    df['away_avg_points_for'] = pd.to_numeric(df['away_avg_points_for'], errors='coerce')
    df['home_avg_points_for'] = pd.to_numeric(df['home_avg_points_for'], errors='coerce')
    df['away_avg_points_against'] = pd.to_numeric(df['away_avg_points_against'], errors='coerce')
    df['home_avg_points_against'] = pd.to_numeric(df['home_avg_points_against'], errors='coerce')
    
    # Enhanced features
    df['away_momentum'] = df['away_win_pct'] * 0.7 + (df['away_avg_points_for'] - df['away_avg_points_against']) * 0.3
    df['home_momentum'] = df['home_win_pct'] * 0.7 + (df['home_avg_points_for'] - df['home_avg_points_against']) * 0.3
    
    df['away_scoring_efficiency'] = df['away_avg_points_for'] / (df['away_avg_points_against'] + 1)
    df['home_scoring_efficiency'] = df['home_avg_points_for'] / (df['home_avg_points_against'] + 1)
    
    df['away_defensive_strength'] = 1 / (df['away_avg_points_against'] + 1)
    df['home_defensive_strength'] = 1 / (df['home_avg_points_against'] + 1)
    
    df['point_diff_advantage'] = (df['home_avg_points_for'] - df['home_avg_points_against']) - (df['away_avg_points_for'] - df['away_avg_points_against'])
    
    df['home_field_advantage'] = 3.0
    
    df['away_rest'] = pd.to_numeric(df['away_rest'], errors='coerce')
    df['home_rest'] = pd.to_numeric(df['home_rest'], errors='coerce')
    df['rest_advantage'] = df['home_rest'] - df['away_rest']
    
    # Weather impact (using existing data)
    df['temp'] = pd.to_numeric(df['temp'], errors='coerce')
    df['wind'] = pd.to_numeric(df['wind'], errors='coerce')
    
    df['weather_impact'] = 0
    df.loc[df['temp'] < 32, 'weather_impact'] += 0.15
    df.loc[df['temp'] > 85, 'weather_impact'] += 0.10
    df.loc[df['wind'] > 15, 'weather_impact'] += 0.08
    df.loc[df['wind'] > 25, 'weather_impact'] += 0.12
    
    df['away_recent_form'] = df['away_win_pct'] * 0.8 + np.random.normal(0, 0.1, len(df))
    df['home_recent_form'] = df['home_win_pct'] * 0.8 + np.random.normal(0, 0.1, len(df))
    
    df['away_offensive_efficiency'] = df['away_avg_points_for'] / 30
    df['home_offensive_efficiency'] = df['home_avg_points_for'] / 30
    df['away_defensive_efficiency'] = 1 - (df['away_avg_points_against'] / 30)
    df['home_defensive_efficiency'] = 1 - (df['home_avg_points_against'] / 30)
    
    df['game_importance'] = 1.0
    
    # Additional advanced features
    df['team_strength_differential'] = df['home_win_pct'] - df['away_win_pct']
    df['scoring_differential'] = (df['home_avg_points_for'] - df['away_avg_points_for']) - (df['home_avg_points_against'] - df['away_avg_points_against'])
    df['defensive_differential'] = df['home_defensive_strength'] - df['away_defensive_strength']
    df['offensive_differential'] = df['home_offensive_efficiency'] - df['away_offensive_efficiency']
    
    # Momentum features
    df['momentum_differential'] = df['home_momentum'] - df['away_momentum']
    df['scoring_efficiency_differential'] = df['home_scoring_efficiency'] - df['away_scoring_efficiency']
    
    # Rest advantage features
    df['rest_advantage_impact'] = df['rest_advantage'] * 0.5
    
    # Weather impact features
    df['weather_impact_home'] = df['weather_impact'] * 0.3
    df['weather_impact_away'] = df['weather_impact'] * 0.3
    
    return df

def get_enhanced_feature_columns():
    """Get all enhanced feature columns"""
    return [
        'away_win_pct', 'home_win_pct',
        'away_avg_points_for', 'home_avg_points_for',
        'away_avg_points_against', 'home_avg_points_against',
        'away_momentum', 'home_momentum',
        'away_scoring_efficiency', 'home_scoring_efficiency',
        'away_defensive_strength', 'home_defensive_strength',
        'point_diff_advantage',
        'home_field_advantage',
        'rest_advantage',
        'weather_impact',
        'away_recent_form', 'home_recent_form',
        'away_offensive_efficiency', 'home_offensive_efficiency',
        'away_defensive_efficiency', 'home_defensive_efficiency',
        'game_importance',
        'team_strength_differential',
        'scoring_differential',
        'defensive_differential',
        'offensive_differential',
        'momentum_differential',
        'scoring_efficiency_differential',
        'rest_advantage_impact',
        'weather_impact_home',
        'weather_impact_away'
    ]

def train_comprehensive_models(historical_df):
    """Train comprehensive models with real data"""
    print("Training comprehensive models with real data...")
    
    # Create features
    df_with_features = create_enhanced_features(historical_df)
    
    # Get feature columns
    feature_columns = get_enhanced_feature_columns()
    
    # Prepare data
    X = df_with_features[feature_columns].copy().fillna(0)
    
    # Create target variable (1 = home team wins, 0 = away team wins)
    completed_games = df_with_features.dropna(subset=['away_score', 'home_score'])
    completed_games = completed_games[
        (completed_games['away_score'] != '') & 
        (completed_games['home_score'] != '')
    ]
    
    if len(completed_games) == 0:
        print("No completed games found for training!")
        return None, None, None
    
    # Create target variable
    y = (completed_games['home_score'] > completed_games['away_score']).astype(int)
    X_train = X.loc[completed_games.index]
    
    print(f"Training data shape: {X_train.shape}")
    print(f"Target distribution: {y.value_counts()}")
    
    # Train multiple models
    models = {
        'RandomForest': RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        ),
        'GradientBoosting': GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        ),
        'LogisticRegression': LogisticRegression(
            random_state=42,
            max_iter=1000
        ),
        'ExtraTrees': ExtraTreesClassifier(
            n_estimators=200,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        ),
        'AdaBoost': AdaBoostClassifier(
            n_estimators=200,
            learning_rate=0.1,
            random_state=42
        ),
        'SVM': SVC(
            random_state=42,
            probability=True
        ),
        'KNN': KNeighborsClassifier(
            n_neighbors=5
        ),
        'DecisionTree': DecisionTreeClassifier(
            random_state=42
        ),
        'Ridge': RidgeClassifier(
            random_state=42
        ),
        'NaiveBayes': GaussianNB()
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
    """Main function to test comprehensive models with real data"""
    print("COMPREHENSIVE MODEL TESTING WITH REAL DATA")
    print("=" * 60)
    
    # Load real data
    print("Loading historical data...")
    historical_df = load_sheet_data(SPREADSHEET_ID, 'historical_game_results_2021_2024')
    
    if historical_df.empty:
        print("Failed to load historical data!")
        return False
    
    print(f"Loaded {len(historical_df)} historical games")
    
    # Train models
    model, features, score, results = train_comprehensive_models(historical_df)
    
    if model is not None:
        print(f"\nModel trained successfully!")
        print(f"Best accuracy: {score:.3f}")
        
        if score >= 0.60:
            print("SUCCESS! Model achieved 60%+ accuracy!")
        else:
            print("Model needs further optimization...")
            
            # Try hyperparameter tuning
            print("\nTrying hyperparameter tuning...")
            if hasattr(model, 'n_estimators'):
                param_grid = {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [10, 20, None],
                    'min_samples_split': [2, 5, 10]
                }
                
                grid_search = GridSearchCV(
                    model, param_grid, cv=5, scoring='accuracy', n_jobs=-1
                )
                grid_search.fit(historical_df[features], historical_df['target'])
                
                print(f"Tuned accuracy: {grid_search.best_score_:.3f}")
                print(f"Best parameters: {grid_search.best_params_}")
    
    return True

if __name__ == "__main__":
    success = main()
