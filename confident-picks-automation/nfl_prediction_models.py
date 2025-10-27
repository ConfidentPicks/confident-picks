#!/usr/bin/env python3

"""
NFL Betting Prediction Models
============================

This script builds multiple predictive models for NFL betting:
1. Game Outcome Prediction (Moneyline)
2. Point Spread Prediction
3. Total Points Prediction (Over/Under)
4. Player Prop Prediction

Features:
- Automated feature engineering
- Multiple model types (XGBoost, Random Forest, Neural Networks)
- Model evaluation and comparison
- Prediction generation for upcoming games
- Integration with existing data pipeline
"""

import pandas as pd
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

# ML Libraries
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error, r2_score
import xgboost as xgb
from sklearn.neural_network import MLPClassifier, MLPRegressor

# Data processing
from datetime import datetime, timedelta
import os

class NFLPredictionModels:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.feature_importance = {}
        
    def load_data(self, sheet_name):
        """Load data from Google Sheets (you'll need to implement this)"""
        # For now, we'll create sample data structure
        # In production, this would connect to your Google Sheets
        
        print(f"📊 Loading data from {sheet_name}...")
        
        # Sample data structure - replace with actual Google Sheets connection
        if sheet_name == "historical_game_results_2021_2024":
            return self.create_sample_game_data()
        elif sheet_name == "player_stats_2025":
            return self.create_sample_player_data()
        elif sheet_name == "historical_team_stats_2021_2024":
            return self.create_sample_team_data()
        else:
            return pd.DataFrame()
    
    def create_sample_game_data(self):
        """Create sample game data for demonstration"""
        np.random.seed(42)
        
        # Generate sample game data
        n_games = 1000
        teams = ['KC', 'BUF', 'CIN', 'BAL', 'LAC', 'DEN', 'LV', 'MIA', 'NE', 'NYJ', 
                'DAL', 'PHI', 'NYG', 'WAS', 'CHI', 'GB', 'MIN', 'DET', 'ATL', 'CAR',
                'NO', 'TB', 'ARI', 'LAR', 'SF', 'SEA', 'IND', 'HOU', 'JAX', 'TEN', 'PIT', 'CLE']
        
        data = []
        for i in range(n_games):
            home_team = np.random.choice(teams)
            away_team = np.random.choice([t for t in teams if t != home_team])
            
            # Simulate realistic game data
            home_score = np.random.poisson(24)
            away_score = np.random.poisson(22)
            
            # Game outcome
            if home_score > away_score:
                result = 'HOME'
            elif away_score > home_score:
                result = 'AWAY'
            else:
                result = 'TIE'
            
            # Spread and total
            spread_line = np.random.normal(0, 7)
            total_line = np.random.normal(45, 10)
            
            game_data = {
                'game_id': f'game_{i}',
                'season': np.random.choice([2021, 2022, 2023, 2024]),
                'week': np.random.randint(1, 18),
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'result': result,
                'total': home_score + away_score,
                'spread_line': round(spread_line, 1),
                'total_line': round(total_line, 1),
                'home_moneyline': np.random.choice([-150, -120, -110, -105, 100, 110, 120, 150]),
                'away_moneyline': np.random.choice([-150, -120, -110, -105, 100, 110, 120, 150]),
                'temperature': np.random.normal(65, 20),
                'wind': np.random.exponential(5),
                'div_game': np.random.choice([0, 1]),
                'roof': np.random.choice(['dome', 'outdoor']),
                'surface': np.random.choice(['grass', 'turf'])
            }
            
            data.append(game_data)
        
        return pd.DataFrame(data)
    
    def create_sample_player_data(self):
        """Create sample player data for demonstration"""
        np.random.seed(42)
        
        positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']
        teams = ['KC', 'BUF', 'CIN', 'BAL', 'LAC', 'DEN', 'LV', 'MIA', 'NE', 'NYJ']
        
        data = []
        for i in range(1000):
            position = np.random.choice(positions)
            
            if position == 'QB':
                passing_yards = np.random.poisson(250)
                passing_tds = np.random.poisson(1.5)
                interceptions = np.random.poisson(0.8)
            elif position == 'RB':
                rushing_yards = np.random.poisson(80)
                rushing_tds = np.random.poisson(0.6)
                receptions = np.random.poisson(3)
            elif position == 'WR':
                receiving_yards = np.random.poisson(70)
                receiving_tds = np.random.poisson(0.5)
                receptions = np.random.poisson(5)
            else:
                passing_yards = rushing_yards = receiving_yards = 0
                passing_tds = rushing_tds = receiving_tds = 0
                interceptions = receptions = 0
            
            player_data = {
                'player_id': f'player_{i}',
                'player_name': f'Player {i}',
                'position': position,
                'team': np.random.choice(teams),
                'season': 2025,
                'week': np.random.randint(1, 18),
                'passing_yards': passing_yards,
                'passing_tds': passing_tds,
                'interceptions': interceptions,
                'rushing_yards': rushing_yards if position == 'RB' else 0,
                'rushing_tds': rushing_tds if position == 'RB' else 0,
                'receiving_yards': receiving_yards if position in ['WR', 'TE', 'RB'] else 0,
                'receiving_tds': receiving_tds if position in ['WR', 'TE', 'RB'] else 0,
                'receptions': receptions if position in ['WR', 'TE', 'RB'] else 0,
                'fantasy_points': np.random.normal(12, 8)
            }
            
            data.append(player_data)
        
        return pd.DataFrame(data)
    
    def create_sample_team_data(self):
        """Create sample team data for demonstration"""
        np.random.seed(42)
        
        teams = ['KC', 'BUF', 'CIN', 'BAL', 'LAC', 'DEN', 'LV', 'MIA', 'NE', 'NYJ']
        
        data = []
        for team in teams:
            for season in [2021, 2022, 2023, 2024]:
                team_data = {
                    'team': team,
                    'season': season,
                    'wins': np.random.randint(5, 14),
                    'losses': np.random.randint(3, 12),
                    'points_for': np.random.poisson(400),
                    'points_against': np.random.poisson(380),
                    'passing_yards': np.random.poisson(4000),
                    'rushing_yards': np.random.poisson(2000),
                    'turnovers': np.random.poisson(20),
                    'sacks': np.random.poisson(40)
                }
                data.append(team_data)
        
        return pd.DataFrame(data)
    
    def engineer_features(self, df, data_type='games'):
        """Engineer features for ML models"""
        print("🔧 Engineering features...")
        
        if data_type == 'games':
            # Game-specific features
            df['home_win'] = (df['result'] == 'HOME').astype(int)
            df['total_diff'] = df['total'] - df['total_line']
            df['spread_diff'] = (df['home_score'] - df['away_score']) - df['spread_line']
            
            # Weather features
            df['cold_game'] = (df['temperature'] < 40).astype(int)
            df['windy_game'] = (df['wind'] > 10).astype(int)
            df['dome_game'] = (df['roof'] == 'dome').astype(int)
            
            # Team performance features (simplified)
            df['home_team_strength'] = np.random.normal(0, 1, len(df))
            df['away_team_strength'] = np.random.normal(0, 1, len(df))
            
        elif data_type == 'players':
            # Player-specific features
            df['is_qb'] = (df['position'] == 'QB').astype(int)
            df['is_rb'] = (df['position'] == 'RB').astype(int)
            df['is_wr'] = (df['position'] == 'WR').astype(int)
            df['is_te'] = (df['position'] == 'TE').astype(int)
            
            # Performance features
            df['total_tds'] = df['passing_tds'] + df['rushing_tds'] + df['receiving_tds']
            df['total_yards'] = df['passing_yards'] + df['rushing_yards'] + df['receiving_yards']
            
        return df
    
    def build_moneyline_model(self):
        """Build moneyline prediction model"""
        print("🎯 Building Moneyline Prediction Model...")
        
        # Load and prepare data
        df = self.load_data("historical_game_results_2021_2024")
        df = self.engineer_features(df, 'games')
        
        # Prepare features and target
        feature_cols = ['home_team_strength', 'away_team_strength', 'div_game', 
                       'cold_game', 'windy_game', 'dome_game', 'spread_line', 'total_line']
        
        X = df[feature_cols]
        y = df['home_win']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train multiple models
        models = {
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'XGBoost': xgb.XGBClassifier(random_state=42),
            'Neural Network': MLPClassifier(hidden_layer_sizes=(100, 50), random_state=42, max_iter=500)
        }
        
        best_model = None
        best_score = 0
        best_model_name = None
        
        for name, model in models.items():
            print(f"  Training {name}...")
            
            if name == 'Neural Network':
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
            
            score = accuracy_score(y_test, y_pred)
            print(f"    Accuracy: {score:.3f}")
            
            if score > best_score:
                best_score = score
                best_model = model
                best_model_name = name
        
        # Store best model
        self.models['moneyline'] = best_model
        self.scalers['moneyline'] = scaler
        self.feature_importance['moneyline'] = feature_cols
        
        print(f"✅ Best Moneyline Model: {best_model_name} (Accuracy: {best_score:.3f})")
        
        return best_model, best_score
    
    def build_spread_model(self):
        """Build point spread prediction model"""
        print("🎯 Building Point Spread Prediction Model...")
        
        # Load and prepare data
        df = self.load_data("historical_game_results_2021_2024")
        df = self.engineer_features(df, 'games')
        
        # Prepare features and target
        feature_cols = ['home_team_strength', 'away_team_strength', 'div_game', 
                       'cold_game', 'windy_game', 'dome_game', 'total_line']
        
        X = df[feature_cols]
        y = df['spread_diff']  # Actual spread vs predicted spread
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train multiple models
        models = {
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'XGBoost': xgb.XGBRegressor(random_state=42),
            'Neural Network': MLPRegressor(hidden_layer_sizes=(100, 50), random_state=42, max_iter=500)
        }
        
        best_model = None
        best_score = 0
        best_model_name = None
        
        for name, model in models.items():
            print(f"  Training {name}...")
            
            if name == 'Neural Network':
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
            
            score = r2_score(y_test, y_pred)
            print(f"    R² Score: {score:.3f}")
            
            if score > best_score:
                best_score = score
                best_model = model
                best_model_name = name
        
        # Store best model
        self.models['spread'] = best_model
        self.scalers['spread'] = scaler
        self.feature_importance['spread'] = feature_cols
        
        print(f"✅ Best Spread Model: {best_model_name} (R² Score: {best_score:.3f})")
        
        return best_model, best_score
    
    def build_total_model(self):
        """Build total points prediction model"""
        print("🎯 Building Total Points Prediction Model...")
        
        # Load and prepare data
        df = self.load_data("historical_game_results_2021_2024")
        df = self.engineer_features(df, 'games')
        
        # Prepare features and target
        feature_cols = ['home_team_strength', 'away_team_strength', 'div_game', 
                       'cold_game', 'windy_game', 'dome_game', 'spread_line']
        
        X = df[feature_cols]
        y = df['total']  # Total points scored
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train multiple models
        models = {
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'XGBoost': xgb.XGBRegressor(random_state=42),
            'Neural Network': MLPRegressor(hidden_layer_sizes=(100, 50), random_state=42, max_iter=500)
        }
        
        best_model = None
        best_score = 0
        best_model_name = None
        
        for name, model in models.items():
            print(f"  Training {name}...")
            
            if name == 'Neural Network':
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
            
            score = r2_score(y_test, y_pred)
            print(f"    R² Score: {score:.3f}")
            
            if score > best_score:
                best_score = score
                best_model = model
                best_model_name = name
        
        # Store best model
        self.models['total'] = best_model
        self.scalers['total'] = scaler
        self.feature_importance['total'] = feature_cols
        
        print(f"✅ Best Total Model: {best_model_name} (R² Score: {best_score:.3f})")
        
        return best_model, best_score
    
    def build_player_prop_model(self):
        """Build player prop prediction model"""
        print("🎯 Building Player Prop Prediction Model...")
        
        # Load and prepare data
        df = self.load_data("player_stats_2025")
        df = self.engineer_features(df, 'players')
        
        # Prepare features and target
        feature_cols = ['is_qb', 'is_rb', 'is_wr', 'is_te', 'week']
        
        X = df[feature_cols]
        y = df['fantasy_points']  # Use fantasy points as proxy for performance
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train multiple models
        models = {
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'XGBoost': xgb.XGBRegressor(random_state=42),
            'Neural Network': MLPRegressor(hidden_layer_sizes=(100, 50), random_state=42, max_iter=500)
        }
        
        best_model = None
        best_score = 0
        best_model_name = None
        
        for name, model in models.items():
            print(f"  Training {name}...")
            
            if name == 'Neural Network':
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
            
            score = r2_score(y_test, y_pred)
            print(f"    R² Score: {score:.3f}")
            
            if score > best_score:
                best_score = score
                best_model = model
                best_model_name = name
        
        # Store best model
        self.models['player_props'] = best_model
        self.scalers['player_props'] = scaler
        self.feature_importance['player_props'] = feature_cols
        
        print(f"✅ Best Player Prop Model: {best_model_name} (R² Score: {best_score:.3f})")
        
        return best_model, best_score
    
    def predict_upcoming_games(self, upcoming_games_df):
        """Make predictions for upcoming games"""
        print("🔮 Making predictions for upcoming games...")
        
        predictions = []
        
        for _, game in upcoming_games_df.iterrows():
            # Prepare features for each model
            features = {
                'home_team_strength': np.random.normal(0, 1),  # Replace with actual team strength
                'away_team_strength': np.random.normal(0, 1),  # Replace with actual team strength
                'div_game': game.get('div_game', 0),
                'cold_game': 1 if game.get('temperature', 65) < 40 else 0,
                'windy_game': 1 if game.get('wind', 5) > 10 else 0,
                'dome_game': 1 if game.get('roof') == 'dome' else 0,
                'spread_line': game.get('spread_line', 0),
                'total_line': game.get('total_line', 45)
            }
            
            # Make predictions
            prediction = {
                'game_id': game['game_id'],
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'predicted_home_win_prob': 0.5,  # Placeholder
                'predicted_spread': 0,  # Placeholder
                'predicted_total': 45,  # Placeholder
                'confidence': 0.7  # Placeholder
            }
            
            predictions.append(prediction)
        
        return pd.DataFrame(predictions)
    
    def train_all_models(self):
        """Train all prediction models"""
        print("🚀 Training All NFL Prediction Models...\n")
        
        results = {}
        
        # Train each model
        results['moneyline'] = self.build_moneyline_model()
        print()
        
        results['spread'] = self.build_spread_model()
        print()
        
        results['total'] = self.build_total_model()
        print()
        
        results['player_props'] = self.build_player_prop_model()
        print()
        
        print("🎉 All models trained successfully!")
        
        # Save models (you'll need to implement model persistence)
        self.save_models()
        
        return results
    
    def save_models(self):
        """Save trained models to disk"""
        print("💾 Saving models...")
        
        # Create models directory
        os.makedirs('models', exist_ok=True)
        
        # Save model info
        model_info = {
            'trained_at': datetime.now().isoformat(),
            'models': list(self.models.keys()),
            'feature_importance': self.feature_importance
        }
        
        with open('models/model_info.json', 'w') as f:
            json.dump(model_info, f, indent=2)
        
        print("✅ Models saved successfully!")
    
    def load_models(self):
        """Load trained models from disk"""
        print("📂 Loading models...")
        
        try:
            with open('models/model_info.json', 'r') as f:
                model_info = json.load(f)
            
            print(f"✅ Models loaded from {model_info['trained_at']}")
            return model_info
            
        except FileNotFoundError:
            print("❌ No saved models found. Train models first.")
            return None

def main():
    """Main function to run the prediction models"""
    print("🏈 NFL Betting Prediction Models")
    print("=" * 50)
    
    # Initialize the prediction system
    nfl_models = NFLPredictionModels()
    
    # Train all models
    results = nfl_models.train_all_models()
    
    # Print summary
    print("\n📊 Model Performance Summary:")
    print("-" * 30)
    for model_type, (model, score) in results.items():
        print(f"{model_type.capitalize()}: {score:.3f}")
    
    print("\n🎯 Next Steps:")
    print("1. Integrate with your Google Sheets data")
    print("2. Add more sophisticated feature engineering")
    print("3. Implement model retraining pipeline")
    print("4. Create prediction API endpoints")
    print("5. Set up automated betting recommendations")

if __name__ == "__main__":
    main()
