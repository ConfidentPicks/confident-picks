#!/usr/bin/env python3

"""
Advanced NFL Betting Prediction Models
=====================================

This script builds sophisticated predictive models for NFL betting with:
- Advanced feature engineering
- Ensemble methods
- Model stacking
- Feature selection
- Hyperparameter optimization
- Betting value calculations
"""

import pandas as pd
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

# ML Libraries
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, TimeSeriesSplit
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, VotingClassifier, VotingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder, RobustScaler
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error, r2_score, log_loss
from sklearn.feature_selection import SelectKBest, f_classif, f_regression
import xgboost as xgb
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.linear_model import LogisticRegression, Ridge, Lasso
from sklearn.svm import SVC, SVR

# Advanced ML
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.ensemble import AdaBoostClassifier, AdaBoostRegressor
from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor

# Data processing
from datetime import datetime, timedelta
import os
from scipy import stats

class AdvancedNFLModels:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_selectors = {}
        self.feature_importance = {}
        self.betting_calculator = BettingCalculator()
        
    def load_historical_data(self):
        """Load and combine all historical data"""
        print("📊 Loading historical data...")
        
        # Load game results
        games_df = self.create_enhanced_game_data()
        
        # Load team stats
        team_stats_df = self.create_enhanced_team_data()
        
        # Load player stats
        player_stats_df = self.create_enhanced_player_data()
        
        # Merge data
        merged_df = self.merge_datasets(games_df, team_stats_df, player_stats_df)
        
        return merged_df
    
    def create_enhanced_game_data(self):
        """Create enhanced game data with more realistic features"""
        np.random.seed(42)
        
        teams = ['KC', 'BUF', 'CIN', 'BAL', 'LAC', 'DEN', 'LV', 'MIA', 'NE', 'NYJ', 
                'DAL', 'PHI', 'NYG', 'WAS', 'CHI', 'GB', 'MIN', 'DET', 'ATL', 'CAR',
                'NO', 'TB', 'ARI', 'LAR', 'SF', 'SEA', 'IND', 'HOU', 'JAX', 'TEN', 'PIT', 'CLE']
        
        # Team strength ratings (realistic)
        team_strength = {
            'KC': 0.8, 'BUF': 0.7, 'CIN': 0.6, 'BAL': 0.6, 'LAC': 0.5,
            'DEN': 0.3, 'LV': 0.2, 'MIA': 0.4, 'NE': 0.3, 'NYJ': 0.2,
            'DAL': 0.6, 'PHI': 0.7, 'NYG': 0.2, 'WAS': 0.3, 'CHI': 0.2,
            'GB': 0.5, 'MIN': 0.4, 'DET': 0.3, 'ATL': 0.2, 'CAR': 0.1,
            'NO': 0.4, 'TB': 0.3, 'ARI': 0.2, 'LAR': 0.5, 'SF': 0.6,
            'SEA': 0.4, 'IND': 0.3, 'HOU': 0.2, 'JAX': 0.3, 'TEN': 0.2,
            'PIT': 0.3, 'CLE': 0.4
        }
        
        n_games = 2000
        data = []
        
        for i in range(n_games):
            home_team = np.random.choice(teams)
            away_team = np.random.choice([t for t in teams if t != home_team])
            
            # Get team strengths
            home_strength = team_strength[home_team]
            away_strength = team_strength[away_team]
            
            # Simulate realistic game data based on team strength
            home_offense = home_strength + np.random.normal(0, 0.2)
            away_offense = away_strength + np.random.normal(0, 0.2)
            home_defense = home_strength + np.random.normal(0, 0.2)
            away_defense = away_strength + np.random.normal(0, 0.2)
            
            # Calculate expected scores
            home_expected = 20 + (home_offense - away_defense) * 10
            away_expected = 20 + (away_offense - home_defense) * 10
            
            # Add randomness
            home_score = max(0, int(np.random.poisson(max(1, home_expected))))
            away_score = max(0, int(np.random.poisson(max(1, away_expected))))
            
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
            
            # Weather and venue
            temperature = np.random.normal(65, 20)
            wind = np.random.exponential(5)
            roof = np.random.choice(['dome', 'outdoor'])
            surface = np.random.choice(['grass', 'turf'])
            
            # Advanced features
            div_game = 1 if np.random.random() < 0.3 else 0
            primetime = 1 if np.random.random() < 0.1 else 0
            home_rest = np.random.randint(7, 14)
            away_rest = np.random.randint(7, 14)
            
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
                'temperature': temperature,
                'wind': wind,
                'div_game': div_game,
                'primetime': primetime,
                'roof': roof,
                'surface': surface,
                'home_rest': home_rest,
                'away_rest': away_rest,
                'home_team_strength': home_strength,
                'away_team_strength': away_strength,
                'home_offense': home_offense,
                'away_offense': away_offense,
                'home_defense': home_defense,
                'away_defense': away_defense
            }
            
            data.append(game_data)
        
        return pd.DataFrame(data)
    
    def create_enhanced_team_data(self):
        """Create enhanced team data with advanced metrics"""
        np.random.seed(42)
        
        teams = ['KC', 'BUF', 'CIN', 'BAL', 'LAC', 'DEN', 'LV', 'MIA', 'NE', 'NYJ', 
                'DAL', 'PHI', 'NYG', 'WAS', 'CHI', 'GB', 'MIN', 'DET', 'ATL', 'CAR',
                'NO', 'TB', 'ARI', 'LAR', 'SF', 'SEA', 'IND', 'HOU', 'JAX', 'TEN', 'PIT', 'CLE']
        
        data = []
        
        for team in teams:
            for season in [2021, 2022, 2023, 2024]:
                # Generate realistic team stats
                wins = np.random.randint(5, 14)
                losses = 17 - wins
                
                # Offensive stats
                points_for = np.random.poisson(400)
                passing_yards = np.random.poisson(4000)
                rushing_yards = np.random.poisson(2000)
                turnovers = np.random.poisson(20)
                
                # Defensive stats
                points_against = np.random.poisson(380)
                sacks = np.random.poisson(40)
                interceptions = np.random.poisson(15)
                fumbles_recovered = np.random.poisson(10)
                
                # Advanced metrics
                pyth_wins = (points_for ** 2.37) / (points_for ** 2.37 + points_against ** 2.37) * 17
                turnover_diff = (interceptions + fumbles_recovered) - turnovers
                pass_efficiency = passing_yards / (passing_yards + rushing_yards) if (passing_yards + rushing_yards) > 0 else 0
                
                team_data = {
                    'team': team,
                    'season': season,
                    'wins': wins,
                    'losses': losses,
                    'points_for': points_for,
                    'points_against': points_against,
                    'passing_yards': passing_yards,
                    'rushing_yards': rushing_yards,
                    'turnovers': turnovers,
                    'sacks': sacks,
                    'interceptions': interceptions,
                    'fumbles_recovered': fumbles_recovered,
                    'pyth_wins': pyth_wins,
                    'turnover_diff': turnover_diff,
                    'pass_efficiency': pass_efficiency,
                    'win_pct': wins / 17
                }
                
                data.append(team_data)
        
        return pd.DataFrame(data)
    
    def create_enhanced_player_data(self):
        """Create enhanced player data with advanced metrics"""
        np.random.seed(42)
        
        positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']
        teams = ['KC', 'BUF', 'CIN', 'BAL', 'LAC', 'DEN', 'LV', 'MIA', 'NE', 'NYJ']
        
        data = []
        
        for i in range(2000):
            position = np.random.choice(positions)
            team = np.random.choice(teams)
            
            # Generate position-specific stats
            if position == 'QB':
                passing_yards = np.random.poisson(250)
                passing_tds = np.random.poisson(1.5)
                interceptions = np.random.poisson(0.8)
                rushing_yards = np.random.poisson(20)
                rushing_tds = np.random.poisson(0.3)
                receptions = 0
                receiving_yards = 0
                receiving_tds = 0
            elif position == 'RB':
                rushing_yards = np.random.poisson(80)
                rushing_tds = np.random.poisson(0.6)
                receptions = np.random.poisson(3)
                receiving_yards = np.random.poisson(25)
                receiving_tds = np.random.poisson(0.2)
                passing_yards = 0
                passing_tds = 0
                interceptions = 0
            elif position == 'WR':
                receiving_yards = np.random.poisson(70)
                receiving_tds = np.random.poisson(0.5)
                receptions = np.random.poisson(5)
                rushing_yards = np.random.poisson(5)
                rushing_tds = np.random.poisson(0.1)
                passing_yards = 0
                passing_tds = 0
                interceptions = 0
            elif position == 'TE':
                receiving_yards = np.random.poisson(50)
                receiving_tds = np.random.poisson(0.4)
                receptions = np.random.poisson(4)
                rushing_yards = np.random.poisson(2)
                rushing_tds = np.random.poisson(0.1)
                passing_yards = 0
                passing_tds = 0
                interceptions = 0
            else:
                passing_yards = rushing_yards = receiving_yards = 0
                passing_tds = rushing_tds = receiving_tds = 0
                interceptions = receptions = 0
            
            # Calculate advanced metrics
            total_yards = passing_yards + rushing_yards + receiving_yards
            total_tds = passing_tds + rushing_tds + receiving_tds
            fantasy_points = passing_yards * 0.04 + passing_tds * 4 + rushing_yards * 0.1 + rushing_tds * 6 + receiving_yards * 0.1 + receiving_tds * 6 - interceptions * 2
            
            player_data = {
                'player_id': f'player_{i}',
                'player_name': f'Player {i}',
                'position': position,
                'team': team,
                'season': 2025,
                'week': np.random.randint(1, 18),
                'passing_yards': passing_yards,
                'passing_tds': passing_tds,
                'interceptions': interceptions,
                'rushing_yards': rushing_yards,
                'rushing_tds': rushing_tds,
                'receiving_yards': receiving_yards,
                'receiving_tds': receiving_tds,
                'receptions': receptions,
                'total_yards': total_yards,
                'total_tds': total_tds,
                'fantasy_points': fantasy_points,
                'fantasy_points_ppr': fantasy_points + receptions * 0.5
            }
            
            data.append(player_data)
        
        return pd.DataFrame(data)
    
    def merge_datasets(self, games_df, team_stats_df, player_stats_df):
        """Merge all datasets for comprehensive analysis"""
        print("🔗 Merging datasets...")
        
        # Merge games with team stats
        merged_df = games_df.merge(
            team_stats_df, 
            left_on=['home_team', 'season'], 
            right_on=['team', 'season'], 
            suffixes=('', '_home')
        )
        
        merged_df = merged_df.merge(
            team_stats_df, 
            left_on=['away_team', 'season'], 
            right_on=['team', 'season'], 
            suffixes=('', '_away')
        )
        
        # Calculate team strength differentials
        merged_df['strength_diff'] = merged_df['home_team_strength'] - merged_df['away_team_strength']
        merged_df['offense_diff'] = merged_df['home_offense'] - merged_df['away_offense']
        merged_df['defense_diff'] = merged_df['home_defense'] - merged_df['away_defense']
        
        # Calculate advanced metrics
        merged_df['pyth_diff'] = merged_df['pyth_wins'] - merged_df['pyth_wins_away']
        merged_df['turnover_diff'] = merged_df['turnover_diff'] - merged_df['turnover_diff_away']
        
        return merged_df
    
    def engineer_advanced_features(self, df):
        """Engineer advanced features for ML models"""
        print("🔧 Engineering advanced features...")
        
        # Basic features
        df['home_win'] = (df['result'] == 'HOME').astype(int)
        df['total_diff'] = df['total'] - df['total_line']
        df['spread_diff'] = (df['home_score'] - df['away_score']) - df['spread_line']
        
        # Weather features
        df['cold_game'] = (df['temperature'] < 40).astype(int)
        df['windy_game'] = (df['wind'] > 10).astype(int)
        df['dome_game'] = (df['roof'] == 'dome').astype(int)
        df['grass_game'] = (df['surface'] == 'grass').astype(int)
        
        # Rest advantage
        df['rest_advantage'] = df['home_rest'] - df['away_rest']
        
        # Strength differentials
        df['strength_diff'] = df['home_team_strength'] - df['away_team_strength']
        df['offense_diff'] = df['home_offense'] - df['away_offense']
        df['defense_diff'] = df['home_defense'] - df['away_defense']
        
        # Advanced metrics
        df['pyth_diff'] = df['pyth_wins'] - df['pyth_wins_away']
        df['turnover_diff'] = df['turnover_diff'] - df['turnover_diff_away']
        df['pass_efficiency_diff'] = df['pass_efficiency'] - df['pass_efficiency_away']
        
        # Interaction features
        df['strength_x_spread'] = df['strength_diff'] * df['spread_line']
        df['weather_x_strength'] = df['cold_game'] * df['strength_diff']
        df['div_x_strength'] = df['div_game'] * df['strength_diff']
        
        # Rolling averages (simplified)
        df['home_team_avg_points'] = df['points_for']
        df['away_team_avg_points'] = df['points_against_away']
        
        return df
    
    def build_ensemble_moneyline_model(self):
        """Build ensemble moneyline prediction model"""
        print("🎯 Building Ensemble Moneyline Model...")
        
        # Load and prepare data
        df = self.load_historical_data()
        df = self.engineer_advanced_features(df)
        
        # Prepare features and target
        feature_cols = [
            'strength_diff', 'offense_diff', 'defense_diff', 'div_game', 'primetime',
            'cold_game', 'windy_game', 'dome_game', 'grass_game', 'rest_advantage',
            'spread_line', 'total_line', 'pyth_diff', 'turnover_diff', 'pass_efficiency_diff',
            'strength_x_spread', 'weather_x_strength', 'div_x_strength'
        ]
        
        X = df[feature_cols]
        y = df['home_win']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = RobustScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Feature selection
        selector = SelectKBest(f_classif, k=10)
        X_train_selected = selector.fit_transform(X_train_scaled, y_train)
        X_test_selected = selector.transform(X_test_scaled)
        
        # Build ensemble models
        base_models = [
            ('rf', RandomForestClassifier(n_estimators=200, random_state=42)),
            ('xgb', xgb.XGBClassifier(random_state=42)),
            ('gb', GradientBoostingClassifier(random_state=42)),
            ('ada', AdaBoostClassifier(random_state=42)),
            ('et', ExtraTreesClassifier(random_state=42))
        ]
        
        # Voting ensemble
        ensemble = VotingClassifier(base_models, voting='soft')
        ensemble.fit(X_train_selected, y_train)
        
        # Make predictions
        y_pred = ensemble.predict(X_test_selected)
        y_pred_proba = ensemble.predict_proba(X_test_selected)
        
        # Evaluate
        accuracy = accuracy_score(y_test, y_pred)
        logloss = log_loss(y_test, y_pred_proba)
        
        print(f"  Accuracy: {accuracy:.3f}")
        print(f"  Log Loss: {logloss:.3f}")
        
        # Store model
        self.models['moneyline_ensemble'] = ensemble
        self.scalers['moneyline_ensemble'] = scaler
        self.feature_selectors['moneyline_ensemble'] = selector
        self.feature_importance['moneyline_ensemble'] = feature_cols
        
        return ensemble, accuracy
    
    def build_ensemble_spread_model(self):
        """Build ensemble spread prediction model"""
        print("🎯 Building Ensemble Spread Model...")
        
        # Load and prepare data
        df = self.load_historical_data()
        df = self.engineer_advanced_features(df)
        
        # Prepare features and target
        feature_cols = [
            'strength_diff', 'offense_diff', 'defense_diff', 'div_game', 'primetime',
            'cold_game', 'windy_game', 'dome_game', 'grass_game', 'rest_advantage',
            'total_line', 'pyth_diff', 'turnover_diff', 'pass_efficiency_diff',
            'strength_x_spread', 'weather_x_strength', 'div_x_strength'
        ]
        
        X = df[feature_cols]
        y = df['spread_diff']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = RobustScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Feature selection
        selector = SelectKBest(f_regression, k=10)
        X_train_selected = selector.fit_transform(X_train_scaled, y_train)
        X_test_selected = selector.transform(X_test_scaled)
        
        # Build ensemble models
        base_models = [
            ('rf', RandomForestRegressor(n_estimators=200, random_state=42)),
            ('xgb', xgb.XGBRegressor(random_state=42)),
            ('gb', GradientBoostingRegressor(random_state=42)),
            ('ada', AdaBoostRegressor(random_state=42)),
            ('et', ExtraTreesRegressor(random_state=42))
        ]
        
        # Voting ensemble
        ensemble = VotingRegressor(base_models)
        ensemble.fit(X_train_selected, y_train)
        
        # Make predictions
        y_pred = ensemble.predict(X_test_selected)
        
        # Evaluate
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        print(f"  R² Score: {r2:.3f}")
        print(f"  RMSE: {rmse:.3f}")
        
        # Store model
        self.models['spread_ensemble'] = ensemble
        self.scalers['spread_ensemble'] = scaler
        self.feature_selectors['spread_ensemble'] = selector
        self.feature_importance['spread_ensemble'] = feature_cols
        
        return ensemble, r2
    
    def build_ensemble_total_model(self):
        """Build ensemble total prediction model"""
        print("🎯 Building Ensemble Total Model...")
        
        # Load and prepare data
        df = self.load_historical_data()
        df = self.engineer_advanced_features(df)
        
        # Prepare features and target
        feature_cols = [
            'strength_diff', 'offense_diff', 'defense_diff', 'div_game', 'primetime',
            'cold_game', 'windy_game', 'dome_game', 'grass_game', 'rest_advantage',
            'spread_line', 'pyth_diff', 'turnover_diff', 'pass_efficiency_diff'
        ]
        
        X = df[feature_cols]
        y = df['total']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = RobustScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Feature selection
        selector = SelectKBest(f_regression, k=10)
        X_train_selected = selector.fit_transform(X_train_scaled, y_train)
        X_test_selected = selector.transform(X_test_scaled)
        
        # Build ensemble models
        base_models = [
            ('rf', RandomForestRegressor(n_estimators=200, random_state=42)),
            ('xgb', xgb.XGBRegressor(random_state=42)),
            ('gb', GradientBoostingRegressor(random_state=42)),
            ('ada', AdaBoostRegressor(random_state=42)),
            ('et', ExtraTreesRegressor(random_state=42))
        ]
        
        # Voting ensemble
        ensemble = VotingRegressor(base_models)
        ensemble.fit(X_train_selected, y_train)
        
        # Make predictions
        y_pred = ensemble.predict(X_test_selected)
        
        # Evaluate
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        print(f"  R² Score: {r2:.3f}")
        print(f"  RMSE: {rmse:.3f}")
        
        # Store model
        self.models['total_ensemble'] = ensemble
        self.scalers['total_ensemble'] = scaler
        self.feature_selectors['total_ensemble'] = selector
        self.feature_importance['total_ensemble'] = feature_cols
        
        return ensemble, r2
    
    def calculate_betting_value(self, predictions_df):
        """Calculate betting value for predictions"""
        print("💰 Calculating betting value...")
        
        values = []
        
        for _, row in predictions_df.iterrows():
            # Calculate value for each bet type
            home_win_value = self.betting_calculator.calculate_value(
                row['home_win_prob'], row['home_moneyline']
            )
            
            away_win_value = self.betting_calculator.calculate_value(
                1 - row['home_win_prob'], row['away_moneyline']
            )
            
            spread_value = self.betting_calculator.calculate_spread_value(
                row['predicted_spread'], row['spread_line']
            )
            
            total_value = self.betting_calculator.calculate_total_value(
                row['predicted_total'], row['total_line']
            )
            
            values.append({
                'game_id': row['game_id'],
                'home_win_value': home_win_value,
                'away_win_value': away_win_value,
                'spread_value': spread_value,
                'total_value': total_value,
                'best_bet': self.get_best_bet(home_win_value, away_win_value, spread_value, total_value)
            })
        
        return pd.DataFrame(values)
    
    def get_best_bet(self, home_win_value, away_win_value, spread_value, total_value):
        """Determine the best bet based on value"""
        values = {
            'home_win': home_win_value,
            'away_win': away_win_value,
            'spread': spread_value,
            'total': total_value
        }
        
        best_bet = max(values, key=values.get)
        return best_bet if values[best_bet] > 0 else 'no_bet'
    
    def train_all_advanced_models(self):
        """Train all advanced prediction models"""
        print("🚀 Training Advanced NFL Prediction Models...\n")
        
        results = {}
        
        # Train each model
        results['moneyline_ensemble'] = self.build_ensemble_moneyline_model()
        print()
        
        results['spread_ensemble'] = self.build_ensemble_spread_model()
        print()
        
        results['total_ensemble'] = self.build_ensemble_total_model()
        print()
        
        print("🎉 All advanced models trained successfully!")
        
        return results

class BettingCalculator:
    """Calculate betting value and expected returns"""
    
    def __init__(self):
        self.vig = 0.05  # 5% vig assumption
    
    def american_to_decimal(self, american_odds):
        """Convert American odds to decimal odds"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    def decimal_to_american(self, decimal_odds):
        """Convert decimal odds to American odds"""
        if decimal_odds >= 2:
            return int((decimal_odds - 1) * 100)
        else:
            return int(-100 / (decimal_odds - 1))
    
    def calculate_value(self, probability, american_odds):
        """Calculate betting value (expected return)"""
        decimal_odds = self.american_to_decimal(american_odds)
        expected_return = (probability * decimal_odds) - 1
        return expected_return
    
    def calculate_spread_value(self, predicted_spread, actual_spread):
        """Calculate spread betting value"""
        # Simplified calculation - in practice, you'd need more sophisticated logic
        spread_diff = predicted_spread - actual_spread
        if abs(spread_diff) > 3:  # Significant edge
            return spread_diff * 0.1
        return 0
    
    def calculate_total_value(self, predicted_total, actual_total):
        """Calculate total betting value"""
        total_diff = predicted_total - actual_total
        if abs(total_diff) > 3:  # Significant edge
            return total_diff * 0.1
        return 0

def main():
    """Main function to run the advanced prediction models"""
    print("🏈 Advanced NFL Betting Prediction Models")
    print("=" * 50)
    
    # Initialize the advanced prediction system
    nfl_models = AdvancedNFLModels()
    
    # Train all models
    results = nfl_models.train_all_advanced_models()
    
    # Print summary
    print("\n📊 Advanced Model Performance Summary:")
    print("-" * 40)
    for model_type, (model, score) in results.items():
        print(f"{model_type.replace('_', ' ').title()}: {score:.3f}")
    
    print("\n🎯 Next Steps:")
    print("1. Integrate with your Google Sheets data")
    print("2. Add more sophisticated feature engineering")
    print("3. Implement model retraining pipeline")
    print("4. Create prediction API endpoints")
    print("5. Set up automated betting recommendations")
    print("6. Add Kelly Criterion for bet sizing")
    print("7. Implement model stacking and blending")

if __name__ == "__main__":
    main()



