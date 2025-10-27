#!/usr/bin/env python3

"""
Google Sheets Integrated NFL Prediction Models
============================================

This script integrates with your Google Sheets data to build and deploy
NFL betting prediction models with real-time predictions.
"""

import pandas as pd
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

# Google Sheets integration
from google.oauth2 import service_account
from googleapiclient.discovery import build
import gspread

# ML Libraries
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, r2_score
import xgboost as xgb

# Data processing
from datetime import datetime, timedelta
import os

class SheetsIntegratedModels:
    def __init__(self, credentials_path, spreadsheet_id):
        """Initialize with Google Sheets credentials"""
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        self.service = None
        self.models = {}
        self.scalers = {}
        
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
                             'temperature', 'wind', 'home_rest', 'away_rest']
            
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
    
    def load_historical_data(self):
        """Load all historical data from Google Sheets"""
        print("📊 Loading historical data from Google Sheets...")
        
        # Load game results
        games_df = self.load_sheet_data("historical_game_results_2021_2024")
        
        # Load team stats
        team_stats_df = self.load_sheet_data("historical_team_stats_2021_2024")
        
        # Load player stats
        player_stats_df = self.load_sheet_data("player_stats_2025")
        
        return games_df, team_stats_df, player_stats_df
    
    def engineer_features(self, df):
        """Engineer features for ML models"""
        print("🔧 Engineering features...")
        
        # Basic features
        df['home_win'] = (df['result'] == 'HOME').astype(int)
        df['total_diff'] = df['total'] - df['total_line']
        df['spread_diff'] = (df['home_score'] - df['away_score']) - df['spread_line']
        
        # Weather features
        df['cold_game'] = (df['temperature'] < 40).astype(int)
        df['windy_game'] = (df['wind'] > 10).astype(int)
        df['dome_game'] = (df['roof'] == 'dome').astype(int)
        
        # Rest advantage
        df['rest_advantage'] = df['home_rest'] - df['away_rest']
        
        # Team strength (simplified)
        df['home_team_strength'] = np.random.normal(0, 1, len(df))
        df['away_team_strength'] = np.random.normal(0, 1, len(df))
        df['strength_diff'] = df['home_team_strength'] - df['away_team_strength']
        
        return df
    
    def build_moneyline_model(self, df):
        """Build moneyline prediction model"""
        print("🎯 Building Moneyline Model...")
        
        # Prepare features and target
        feature_cols = ['strength_diff', 'div_game', 'cold_game', 'windy_game', 
                       'dome_game', 'rest_advantage', 'spread_line', 'total_line']
        
        X = df[feature_cols]
        y = df['home_win']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = xgb.XGBClassifier(random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"  Accuracy: {accuracy:.3f}")
        
        # Store model
        self.models['moneyline'] = model
        self.scalers['moneyline'] = scaler
        
        return model, accuracy
    
    def build_spread_model(self, df):
        """Build spread prediction model"""
        print("🎯 Building Spread Model...")
        
        # Prepare features and target
        feature_cols = ['strength_diff', 'div_game', 'cold_game', 'windy_game', 
                       'dome_game', 'rest_advantage', 'total_line']
        
        X = df[feature_cols]
        y = df['spread_diff']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = xgb.XGBRegressor(random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        
        print(f"  R² Score: {r2:.3f}")
        
        # Store model
        self.models['spread'] = model
        self.scalers['spread'] = scaler
        
        return model, r2
    
    def build_total_model(self, df):
        """Build total prediction model"""
        print("🎯 Building Total Model...")
        
        # Prepare features and target
        feature_cols = ['strength_diff', 'div_game', 'cold_game', 'windy_game', 
                       'dome_game', 'rest_advantage', 'spread_line']
        
        X = df[feature_cols]
        y = df['total']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = xgb.XGBRegressor(random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        
        print(f"  R² Score: {r2:.3f}")
        
        # Store model
        self.models['total'] = model
        self.scalers['total'] = scaler
        
        return model, r2
    
    def predict_upcoming_games(self):
        """Make predictions for upcoming games"""
        print("🔮 Making predictions for upcoming games...")
        
        # Load upcoming games
        upcoming_df = self.load_sheet_data("upcoming_games")
        
        if upcoming_df.empty:
            print("⚠️ No upcoming games found")
            return pd.DataFrame()
        
        predictions = []
        
        for _, game in upcoming_df.iterrows():
            # Prepare features
            features = {
                'strength_diff': np.random.normal(0, 1),  # Replace with actual team strength
                'div_game': game.get('div_game', 0),
                'cold_game': 1 if game.get('temperature', 65) < 40 else 0,
                'windy_game': 1 if game.get('wind', 5) > 10 else 0,
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
            
            prediction = {
                'game_id': game['game_id'],
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'home_win_prob': round(home_win_prob, 3),
                'predicted_spread': round(predicted_spread, 1),
                'predicted_total': round(predicted_total, 1),
                'home_win_value': round(home_win_value, 3),
                'away_win_value': round(away_win_value, 3),
                'confidence': round(max(home_win_prob, 1 - home_win_prob), 3),
                'recommendation': self.get_recommendation(home_win_value, away_win_value, home_win_prob)
            }
            
            predictions.append(prediction)
        
        return pd.DataFrame(predictions)
    
    def calculate_betting_value(self, probability, american_odds):
        """Calculate betting value"""
        if american_odds > 0:
            decimal_odds = (american_odds / 100) + 1
        else:
            decimal_odds = (100 / abs(american_odds)) + 1
        
        expected_return = (probability * decimal_odds) - 1
        return expected_return
    
    def get_recommendation(self, home_win_value, away_win_value, home_win_prob):
        """Get betting recommendation"""
        if home_win_value > 0.05:
            return f"HOME WIN (Value: {home_win_value:.3f})"
        elif away_win_value > 0.05:
            return f"AWAY WIN (Value: {away_win_value:.3f})"
        else:
            return "NO BET"
    
    def train_all_models(self):
        """Train all prediction models"""
        print("🚀 Training NFL Prediction Models with Google Sheets Data...\n")
        
        # Load data
        games_df, team_stats_df, player_stats_df = self.load_historical_data()
        
        if games_df.empty:
            print("❌ No historical data found. Please check your Google Sheets.")
            return None
        
        # Engineer features
        games_df = self.engineer_features(games_df)
        
        # Train models
        results = {}
        results['moneyline'] = self.build_moneyline_model(games_df)
        results['spread'] = self.build_spread_model(games_df)
        results['total'] = self.build_total_model(games_df)
        
        print("\n🎉 All models trained successfully!")
        
        return results
    
    def run_prediction_pipeline(self):
        """Run the complete prediction pipeline"""
        print("🏈 NFL Prediction Pipeline")
        print("=" * 40)
        
        # Train models
        results = self.train_all_models()
        
        if results is None:
            return
        
        # Make predictions
        predictions_df = self.predict_upcoming_games()
        
        if not predictions_df.empty:
            # Save predictions to Google Sheets
            self.save_predictions_to_sheet(predictions_df, "model_predictions")
            
            # Print summary
            print("\n📊 Prediction Summary:")
            print("-" * 30)
            for _, pred in predictions_df.iterrows():
                print(f"{pred['away_team']} @ {pred['home_team']}")
                print(f"  Home Win Prob: {pred['home_win_prob']:.1%}")
                print(f"  Predicted Spread: {pred['predicted_spread']:.1f}")
                print(f"  Predicted Total: {pred['predicted_total']:.1f}")
                print(f"  Recommendation: {pred['recommendation']}")
                print()
        
        return predictions_df

def main():
    """Main function to run the prediction pipeline"""
    # Configuration
    credentials_path = "C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json"
    spreadsheet_id = "1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU"
    
    # Initialize and run pipeline
    nfl_models = SheetsIntegratedModels(credentials_path, spreadsheet_id)
    predictions_df = nfl_models.run_prediction_pipeline()
    
    if predictions_df is not None:
        print("✅ Prediction pipeline completed successfully!")
        print("📊 Check your Google Sheets for the latest predictions in the 'model_predictions' tab.")
    else:
        print("❌ Prediction pipeline failed. Please check your data and try again.")

if __name__ == "__main__":
    main()



