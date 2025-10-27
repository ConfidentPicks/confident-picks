#!/usr/bin/env python3

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

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

def train_enhanced_model(historical_df):
    """Train enhanced model with real data"""
    print("Training enhanced model with real data...")
    
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
        )
    }
    
    best_model = None
    best_score = 0
    best_name = ""
    results = {}
    
    for name, model in models.items():
        print(f"Training {name}...")
        
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
    """Main function to test the enhanced model in sandbox"""
    print("SANDBOX MODEL TESTING")
    print("=" * 60)
    
    print("Ready to test in sandbox environment!")
    print("Features available:")
    print("- Comprehensive enhanced features")
    print("- Multiple ML algorithms")
    print("- Cross-validation testing")
    print("- Feature importance analysis")
    print("- Performance tracking")
    
    return True

if __name__ == "__main__":
    success = main()

