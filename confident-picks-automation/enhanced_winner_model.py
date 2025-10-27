#!/usr/bin/env python3

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score, GridSearchCV, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

def create_enhanced_features(df):
    """Create enhanced features for the model"""
    print("🔧 Creating enhanced features...")
    
    # Basic features
    df['away_win_pct'] = pd.to_numeric(df['away_win_pct'], errors='coerce')
    df['home_win_pct'] = pd.to_numeric(df['home_win_pct'], errors='coerce')
    df['away_avg_points_for'] = pd.to_numeric(df['away_avg_points_for'], errors='coerce')
    df['home_avg_points_for'] = pd.to_numeric(df['home_avg_points_for'], errors='coerce')
    df['away_avg_points_against'] = pd.to_numeric(df['away_avg_points_against'], errors='coerce')
    df['home_avg_points_against'] = pd.to_numeric(df['home_avg_points_against'], errors='coerce')
    
    # NEW FEATURES
    # 1. Team momentum (win/loss streaks)
    df['away_momentum'] = df['away_win_pct'] * 0.7 + (df['away_avg_points_for'] - df['away_avg_points_against']) * 0.3
    df['home_momentum'] = df['home_win_pct'] * 0.7 + (df['home_avg_points_for'] - df['home_avg_points_against']) * 0.3
    
    # 2. Scoring efficiency
    df['away_scoring_efficiency'] = df['away_avg_points_for'] / (df['away_avg_points_against'] + 1)
    df['home_scoring_efficiency'] = df['home_avg_points_for'] / (df['home_avg_points_against'] + 1)
    
    # 3. Defensive strength
    df['away_defensive_strength'] = 1 / (df['away_avg_points_against'] + 1)
    df['home_defensive_strength'] = 1 / (df['home_avg_points_against'] + 1)
    
    # 4. Point differential advantage
    df['point_diff_advantage'] = (df['home_avg_points_for'] - df['home_avg_points_against']) - (df['away_avg_points_for'] - df['away_avg_points_against'])
    
    # 5. Home field advantage (enhanced)
    df['home_field_advantage'] = 3.0  # Base home field advantage
    
    # 6. Rest advantage
    df['away_rest'] = pd.to_numeric(df['away_rest'], errors='coerce')
    df['home_rest'] = pd.to_numeric(df['home_rest'], errors='coerce')
    df['rest_advantage'] = df['home_rest'] - df['away_rest']
    
    # 7. Weather impact (enhanced)
    df['temp'] = pd.to_numeric(df['temp'], errors='coerce')
    df['wind'] = pd.to_numeric(df['wind'], errors='coerce')
    
    # Rodriguez's Weather Impact Formula
    df['weather_impact'] = 0
    df.loc[df['temp'] < 32, 'weather_impact'] += 0.15
    df.loc[df['temp'] > 85, 'weather_impact'] += 0.10
    df.loc[df['wind'] > 15, 'weather_impact'] += 0.08
    df.loc[df['wind'] > 25, 'weather_impact'] += 0.12
    
    # 8. Recent form (last 5 games)
    df['away_recent_form'] = df['away_win_pct'] * 0.8 + np.random.normal(0, 0.1, len(df))  # Simulated
    df['home_recent_form'] = df['home_win_pct'] * 0.8 + np.random.normal(0, 0.1, len(df))  # Simulated
    
    # 9. Offensive/Defensive efficiency
    df['away_offensive_efficiency'] = df['away_avg_points_for'] / 30  # Normalized
    df['home_offensive_efficiency'] = df['home_avg_points_for'] / 30  # Normalized
    df['away_defensive_efficiency'] = 1 - (df['away_avg_points_against'] / 30)  # Normalized
    df['home_defensive_efficiency'] = 1 - (df['home_avg_points_against'] / 30)  # Normalized
    
    # 10. Game importance factor
    df['game_importance'] = 1.0  # Base importance
    
    return df

def get_enhanced_feature_columns():
    """Get the enhanced feature columns for the model"""
    return [
        # Basic features
        'away_win_pct', 'home_win_pct',
        'away_avg_points_for', 'home_avg_points_for',
        'away_avg_points_against', 'home_avg_points_against',
        
        # Enhanced features
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
        'game_importance'
    ]

def train_enhanced_model(X, y):
    """Train multiple models and select the best one"""
    print("🤖 Training enhanced models...")
    
    # Split data for validation
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    
    models = {
        'RandomForest': RandomForestClassifier(random_state=42),
        'GradientBoosting': GradientBoostingClassifier(random_state=42),
        'LogisticRegression': LogisticRegression(random_state=42, max_iter=1000),
        'SVM': SVC(random_state=42, probability=True)
    }
    
    best_model = None
    best_score = 0
    best_name = ""
    
    for name, model in models.items():
        print(f"Training {name}...")
        
        # Train model
        model.fit(X_train, y_train)
        
        # Validate
        val_score = model.score(X_val, y_val)
        print(f"{name} validation accuracy: {val_score:.3f}")
        
        if val_score > best_score:
            best_score = val_score
            best_model = model
            best_name = name
    
    print(f"Best model: {best_name} with accuracy: {best_score:.3f}")
    
    # Hyperparameter tuning for best model
    if best_name == 'RandomForest':
        param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [10, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        grid_search = GridSearchCV(
            RandomForestClassifier(random_state=42),
            param_grid,
            cv=5,
            scoring='accuracy',
            n_jobs=-1
        )
        
        grid_search.fit(X_train, y_train)
        best_model = grid_search.best_estimator_
        print(f"Tuned RandomForest accuracy: {grid_search.best_score_:.3f}")
        print(f"Best parameters: {grid_search.best_params_}")
    
    return best_model, best_score

def evaluate_enhanced_model(model, X, y):
    """Evaluate the enhanced model"""
    print("📊 Evaluating enhanced model...")
    
    # Cross-validation
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
    print(f"Cross-validation scores: {cv_scores}")
    print(f"Mean CV accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
    
    # Feature importance (if available)
    if hasattr(model, 'feature_importances_'):
        feature_columns = get_enhanced_feature_columns()
        importance_df = pd.DataFrame({
            'feature': feature_columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nTop 10 most important features:")
        print(importance_df.head(10))
    
    return cv_scores.mean()

def main():
    """Main function to train and evaluate enhanced model"""
    print("🚀 ENHANCED WINNER PREDICTION MODEL")
    print("=" * 60)
    
    # Load data (you'll need to integrate this with your existing data loading)
    # For now, this is the framework
    
    print("Target: 60%+ accuracy on winner predictions")
    print("Features: Enhanced with momentum, efficiency, weather, and more")
    print("Models: RandomForest, GradientBoosting, LogisticRegression, SVM")
    print("Optimization: Hyperparameter tuning and cross-validation")
    
    return True

if __name__ == "__main__":
    success = main()
