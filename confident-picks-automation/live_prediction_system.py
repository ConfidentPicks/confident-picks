#!/usr/bin/env python3

"""
Live NFL Prediction System with Google Sheets Integration
=======================================================

This script integrates with your Google Sheets data to:
1. Load real historical data
2. Train models with actual stats
3. Make predictions for upcoming games
4. Auto-update predictions with new data
"""

import pandas as pd
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

# Google Sheets integration
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ML Libraries
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, r2_score
import xgboost as xgb

# Data processing
from datetime import datetime, timedelta
import os

class LiveNFLPredictionSystem:
    def __init__(self, credentials_path, spreadsheet_id):
        """Initialize with Google Sheets credentials"""
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        self.service = None
        self.models = {}
        self.scalers = {}
        self.team_strengths = {}
        
        # Initialize Google Sheets connection
        self.setup_sheets_connection()
    
    def setup_sheets_connection(self):
        """Setup Google Sheets connection"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            self.service = build('sheets', 'v4', credentials=credentials)
            print("✅ Google Sheets connection established")
            
        except Exception as e:
            print(f"❌ Error connecting to Google Sheets: {e}")
    
    def load_sheet_data(self, sheet_name, range_name=None):
        """Load data from Google Sheets"""
        try:
            if range_name is None:
                range_name = f"{sheet_name}!A1:ZZ10000"
            
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                print(f"⚠️ No data found in {sheet_name}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(values[1:], columns=values[0])
            
            # Convert numeric columns
            numeric_columns = ['season', 'week', 'home_score', 'away_score', 'total', 
                             'spread_line', 'total_line', 'home_moneyline', 'away_moneyline',
                             'temperature', 'wind', 'home_rest', 'away_rest', 'wins', 'losses',
                             'points_for', 'points_against', 'passing_yards', 'rushing_yards',
                             'turnovers', 'sacks', 'interceptions', 'fumbles_recovered']
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            print(f"✅ Loaded {len(df)} rows from {sheet_name}")
            return df
            
        except Exception as e:
            print(f"❌ Error loading data from {sheet_name}: {e}")
            return pd.DataFrame()
    
    def save_predictions_to_sheet(self, predictions_df, sheet_name):
        """Save predictions to Google Sheets"""
        try:
            # Prepare data for Google Sheets
            values = [predictions_df.columns.tolist()]
            values.extend(predictions_df.values.tolist())
            
            # Clear existing data
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!A1:ZZ10000"
            ).execute()
            
            # Update with new data
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!A1",
                valueInputOption='USER_ENTERED',
                body={'values': values}
            ).execute()
            
            print(f"✅ Predictions saved to {sheet_name}")
            
        except Exception as e:
            print(f"❌ Error saving predictions to {sheet_name}: {e}")
    
    def calculate_team_strengths(self, games_df):
        """Calculate team strength ratings from actual game data"""
        print("📊 Calculating team strength ratings from game data...")
        
        team_strengths = {}
        
        # Get unique teams from both home and away teams
        all_teams = set(games_df['home_team'].unique()) | set(games_df['away_team'].unique())
        
        for team in all_teams:
            # Get all games where this team played
            team_games = games_df[(games_df['home_team'] == team) | (games_df['away_team'] == team)]
            
            if len(team_games) > 0:
                # Calculate team performance metrics
                wins = 0
                total_games = len(team_games)
                total_points_for = 0
                total_points_against = 0
                
                for _, game in team_games.iterrows():
                    if game['home_team'] == team:
                        # Team was home
                        team_score = game['home_score']
                        opponent_score = game['away_score']
                        if game['result'] == 'HOME':
                            wins += 1
                    else:
                        # Team was away
                        team_score = game['away_score']
                        opponent_score = game['home_score']
                        if game['result'] == 'AWAY':
                            wins += 1
                    
                    total_points_for += team_score
                    total_points_against += opponent_score
                
                # Calculate metrics
                win_pct = wins / total_games if total_games > 0 else 0.5
                points_diff = total_points_for - total_points_against
                
                # Normalize strength (0 to 1 scale)
                strength = (win_pct * 0.6 + (points_diff / (total_games * 10)) * 0.4)
                
                # Ensure strength is between 0 and 1
                strength = max(0.1, min(0.9, strength))
                team_strengths[team] = strength
            else:
                team_strengths[team] = 0.5
        
        self.team_strengths = team_strengths
        print(f"✅ Calculated strength ratings for {len(team_strengths)} teams")
        
        return team_strengths
    
    def engineer_features(self, df):
        """Engineer features for ML models using real data"""
        print("🔧 Engineering features from real data...")
        
        # Basic features - check what result values mean
        print(f"  Result values: {df['result'].value_counts().to_dict()}")
        
        # Based on the data, result=4 seems to mean HOME win, let's check
        # Let's create a more robust home_win calculation
        df['home_win'] = ((df['home_score'] > df['away_score'])).astype(int)
        df['total_diff'] = df['total'] - df['total_line']
        df['spread_diff'] = (df['home_score'] - df['away_score']) - df['spread_line']
        
        # Ensure numeric columns are properly formatted
        numeric_cols = ['total', 'total_line', 'spread_line', 'home_score', 'away_score', 'home_rest', 'away_rest']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Weather features (using actual column names)
        if 'temp' in df.columns:
            df['temp'] = pd.to_numeric(df['temp'], errors='coerce').fillna(65)
            df['cold_game'] = (df['temp'] < 40).astype(int)
        else:
            df['cold_game'] = 0
            
        if 'wind' in df.columns:
            df['wind'] = pd.to_numeric(df['wind'], errors='coerce').fillna(5)
            df['windy_game'] = (df['wind'] > 10).astype(int)
        else:
            df['windy_game'] = 0
            
        df['dome_game'] = (df['roof'] == 'dome').astype(int) if 'roof' in df.columns else 0
        
        # Rest advantage
        df['rest_advantage'] = df['home_rest'] - df['away_rest']
        
        # Team strength features
        df['home_team_strength'] = df['home_team'].map(self.team_strengths).fillna(0.5)
        df['away_team_strength'] = df['away_team'].map(self.team_strengths).fillna(0.5)
        df['strength_diff'] = df['home_team_strength'] - df['away_team_strength']
        
        # Advanced features
        df['div_game'] = 0  # We don't have division info in current data
        df['primetime'] = 0  # We don't have primetime info in current data
        
        return df
    
    def build_moneyline_model(self, df):
        """Build moneyline prediction model with real data"""
        print("🎯 Building Moneyline Model with real data...")
        
        # Prepare features and target
        feature_cols = ['strength_diff', 'div_game', 'cold_game', 'windy_game', 
                       'dome_game', 'rest_advantage', 'spread_line', 'total_line']
        
        # Filter out rows with missing data
        df_clean = df.dropna(subset=feature_cols + ['home_win'])
        
        print(f"  Original data: {len(df)} rows")
        print(f"  Clean data: {len(df_clean)} rows")
        print(f"  Target distribution: {df_clean['home_win'].value_counts().to_dict()}")
        
        if len(df_clean) < 10:
            print("⚠️ Not enough clean data for training")
            return None, 0
        
        X = df_clean[feature_cols]
        y = df_clean['home_win']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = xgb.XGBClassifier(random_state=42, n_estimators=100, eval_metric='logloss')
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"  Accuracy: {accuracy:.3f}")
        print(f"  Training samples: {len(X_train)}")
        print(f"  Test samples: {len(X_test)}")
        
        # Store model
        self.models['moneyline'] = model
        self.scalers['moneyline'] = scaler
        
        return model, accuracy
    
    def build_spread_model(self, df):
        """Build spread prediction model with real data"""
        print("🎯 Building Spread Model with real data...")
        
        # Prepare features and target
        feature_cols = ['strength_diff', 'div_game', 'cold_game', 'windy_game', 
                       'dome_game', 'rest_advantage', 'total_line']
        
        # Filter out rows with missing data
        df_clean = df.dropna(subset=feature_cols + ['spread_diff'])
        
        if len(df_clean) < 100:
            print("⚠️ Not enough clean data for training")
            return None, 0
        
        X = df_clean[feature_cols]
        y = df_clean['spread_diff']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = xgb.XGBRegressor(random_state=42, n_estimators=100)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        
        print(f"  R² Score: {r2:.3f}")
        print(f"  Training samples: {len(X_train)}")
        print(f"  Test samples: {len(X_test)}")
        
        # Store model
        self.models['spread'] = model
        self.scalers['spread'] = scaler
        
        return model, r2
    
    def build_total_model(self, df):
        """Build total prediction model with real data"""
        print("🎯 Building Total Model with real data...")
        
        # Prepare features and target
        feature_cols = ['strength_diff', 'div_game', 'cold_game', 'windy_game', 
                       'dome_game', 'rest_advantage', 'spread_line']
        
        # Filter out rows with missing data
        df_clean = df.dropna(subset=feature_cols + ['total'])
        
        if len(df_clean) < 100:
            print("⚠️ Not enough clean data for training")
            return None, 0
        
        X = df_clean[feature_cols]
        y = df_clean['total']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = xgb.XGBRegressor(random_state=42, n_estimators=100)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        
        print(f"  R² Score: {r2:.3f}")
        print(f"  Training samples: {len(X_train)}")
        print(f"  Test samples: {len(X_test)}")
        
        # Store model
        self.models['total'] = model
        self.scalers['total'] = scaler
        
        return model, r2
    
    def predict_upcoming_games(self):
        """Make predictions for upcoming games using real data"""
        print("🔮 Making predictions for upcoming games...")
        
        # Load upcoming games
        upcoming_df = self.load_sheet_data("upcoming_games")
        
        if upcoming_df.empty:
            print("⚠️ No upcoming games found")
            return pd.DataFrame()
        
        predictions = []
        
        for _, game in upcoming_df.iterrows():
            try:
                # Get team strengths
                home_strength = self.team_strengths.get(game['home_team'], 0.5)
                away_strength = self.team_strengths.get(game['away_team'], 0.5)
                strength_diff = home_strength - away_strength
                
                # Prepare features (using actual column names)
                temp = pd.to_numeric(game.get('temp', 65), errors='coerce')
                wind = pd.to_numeric(game.get('wind', 5), errors='coerce')
                
                features = {
                    'strength_diff': strength_diff,
                    'div_game': 0,  # We don't have division info
                    'cold_game': 1 if temp < 40 else 0,
                    'windy_game': 1 if wind > 10 else 0,
                    'dome_game': 1 if game.get('roof') == 'dome' else 0,
                    'rest_advantage': game.get('home_rest', 7) - game.get('away_rest', 7),
                    'spread_line': game.get('spread_line', 0),
                    'total_line': game.get('total_line', 45)
                }
                
                # Make predictions
                feature_vector = np.array([features[col] for col in [
                    'strength_diff', 'div_game', 'cold_game', 'windy_game', 
                    'dome_game', 'rest_advantage', 'spread_line', 'total_line'
                ]]).reshape(1, -1)
                
                # Moneyline prediction
                moneyline_features = feature_vector[:, :-1]  # Exclude total_line
                moneyline_scaled = self.scalers['moneyline'].transform(moneyline_features)
                home_win_prob = self.models['moneyline'].predict_proba(moneyline_scaled)[0][1]
                
                # Spread prediction
                spread_features = feature_vector[:, :-1]  # Exclude total_line
                spread_scaled = self.scalers['spread'].transform(spread_features)
                predicted_spread = self.models['spread'].predict(spread_scaled)[0]
                
                # Total prediction
                total_features = feature_vector[:, :-1]  # Exclude total_line
                total_scaled = self.scalers['total'].transform(total_features)
                predicted_total = self.models['total'].predict(total_scaled)[0]
                
                # Calculate betting value
                home_win_value = self.calculate_betting_value(home_win_prob, game.get('home_moneyline', 100))
                away_win_value = self.calculate_betting_value(1 - home_win_prob, game.get('away_moneyline', 100))
                
                # Calculate confidence
                confidence = max(home_win_prob, 1 - home_win_prob)
                
                prediction = {
                    'game_id': game['game_id'],
                    'home_team': game['home_team'],
                    'away_team': game['away_team'],
                    'home_team_strength': round(home_strength, 3),
                    'away_team_strength': round(away_strength, 3),
                    'home_win_prob': round(home_win_prob, 3),
                    'predicted_spread': round(predicted_spread, 1),
                    'predicted_total': round(predicted_total, 1),
                    'home_win_value': round(home_win_value, 3),
                    'away_win_value': round(away_win_value, 3),
                    'confidence': round(confidence, 3),
                    'recommendation': self.get_recommendation(home_win_value, away_win_value, home_win_prob),
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                predictions.append(prediction)
                
            except Exception as e:
                print(f"⚠️ Error predicting game {game.get('game_id', 'unknown')}: {e}")
                continue
        
        return pd.DataFrame(predictions)
    
    def calculate_betting_value(self, probability, american_odds):
        """Calculate betting value"""
        try:
            if american_odds > 0:
                decimal_odds = (american_odds / 100) + 1
            else:
                decimal_odds = (100 / abs(american_odds)) + 1
            
            expected_return = (probability * decimal_odds) - 1
            return expected_return
        except:
            return 0
    
    def get_recommendation(self, home_win_value, away_win_value, home_win_prob):
        """Get betting recommendation"""
        if home_win_value > 0.05:
            return f"HOME WIN (Value: {home_win_value:.3f})"
        elif away_win_value > 0.05:
            return f"AWAY WIN (Value: {away_win_value:.3f})"
        else:
            return "NO BET"
    
    def run_live_prediction_system(self):
        """Run the complete live prediction system"""
        print("🏈 Live NFL Prediction System")
        print("=" * 40)
        
        # Load data
        print("📊 Loading data from Google Sheets...")
        games_df = self.load_sheet_data("historical_game_results_2021_2024")
        
        if games_df.empty:
            print("❌ Missing required data. Please check your Google Sheets.")
            return None
        
        # Calculate team strengths
        self.calculate_team_strengths(games_df)
        
        # Engineer features
        games_df = self.engineer_features(games_df)
        
        # Train models
        print("\n🚀 Training models with real data...")
        results = {}
        
        moneyline_model, moneyline_score = self.build_moneyline_model(games_df)
        if moneyline_model is not None:
            results['moneyline'] = moneyline_score
        
        spread_model, spread_score = self.build_spread_model(games_df)
        if spread_model is not None:
            results['spread'] = spread_score
        
        total_model, total_score = self.build_total_model(games_df)
        if total_model is not None:
            results['total'] = total_score
        
        if not results:
            print("❌ No models could be trained. Please check your data.")
            return None
        
        print(f"\n✅ Models trained successfully!")
        print(f"📊 Model Performance:")
        for model_type, score in results.items():
            print(f"  {model_type.capitalize()}: {score:.3f}")
        
        # Make predictions
        predictions_df = self.predict_upcoming_games()
        
        if not predictions_df.empty:
            # Save predictions to Google Sheets
            self.save_predictions_to_sheet(predictions_df, "live_predictions")
            
            # Print summary
            print("\n📊 Live Predictions Summary:")
            print("-" * 40)
            for _, pred in predictions_df.iterrows():
                print(f"{pred['away_team']} @ {pred['home_team']}")
                print(f"  Home Win Prob: {pred['home_win_prob']:.1%}")
                print(f"  Predicted Spread: {pred['predicted_spread']:.1f}")
                print(f"  Predicted Total: {pred['predicted_total']:.1f}")
                print(f"  Recommendation: {pred['recommendation']}")
                print(f"  Confidence: {pred['confidence']:.1%}")
                print()
        
        return predictions_df

def main():
    """Main function to run the live prediction system"""
    # Configuration
    credentials_path = "C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json"
    spreadsheet_id = "1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU"
    
    # Initialize and run system
    nfl_system = LiveNFLPredictionSystem(credentials_path, spreadsheet_id)
    predictions_df = nfl_system.run_live_prediction_system()
    
    if predictions_df is not None:
        print("✅ Live prediction system completed successfully!")
        print("📊 Check your Google Sheets for the latest predictions in the 'live_predictions' tab.")
    else:
        print("❌ Live prediction system failed. Please check your data and try again.")

if __name__ == "__main__":
    main()
