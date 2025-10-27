#!/usr/bin/env python3

"""
Simple Live NFL Predictions
==========================

This script makes predictions for games in the live_picks_sheets tab
using the trained models from historical data.
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
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, r2_score
import xgboost as xgb

# Data processing
from datetime import datetime, timedelta
import os

class SimpleLivePredictions:
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
                        team_score = pd.to_numeric(game['home_score'], errors='coerce')
                        opponent_score = pd.to_numeric(game['away_score'], errors='coerce')
                        if team_score > opponent_score:
                            wins += 1
                    else:
                        # Team was away
                        team_score = pd.to_numeric(game['away_score'], errors='coerce')
                        opponent_score = pd.to_numeric(game['home_score'], errors='coerce')
                        if team_score > opponent_score:
                            wins += 1
                    
                    total_points_for += team_score if not pd.isna(team_score) else 0
                    total_points_against += opponent_score if not pd.isna(opponent_score) else 0
                
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
    
    def train_simple_model(self, games_df):
        """Train a simple moneyline prediction model"""
        print("🎯 Training Simple Moneyline Model...")
        
        # Convert numeric columns
        numeric_cols = ['home_score', 'away_score', 'spread_line', 'total_line', 'home_rest', 'away_rest']
        for col in numeric_cols:
            if col in games_df.columns:
                games_df[col] = pd.to_numeric(games_df[col], errors='coerce')
        
        # Create features
        games_df['home_win'] = (games_df['home_score'] > games_df['away_score']).astype(int)
        games_df['home_team_strength'] = games_df['home_team'].map(self.team_strengths).fillna(0.5)
        games_df['away_team_strength'] = games_df['away_team'].map(self.team_strengths).fillna(0.5)
        games_df['strength_diff'] = games_df['home_team_strength'] - games_df['away_team_strength']
        
        # Weather features
        if 'temp' in games_df.columns:
            games_df['temp'] = pd.to_numeric(games_df['temp'], errors='coerce').fillna(65)
            games_df['cold_game'] = (games_df['temp'] < 40).astype(int)
        else:
            games_df['cold_game'] = 0
            
        if 'wind' in games_df.columns:
            games_df['wind'] = pd.to_numeric(games_df['wind'], errors='coerce').fillna(5)
            games_df['windy_game'] = (games_df['wind'] > 10).astype(int)
        else:
            games_df['windy_game'] = 0
            
        games_df['dome_game'] = (games_df['roof'] == 'dome').astype(int) if 'roof' in games_df.columns else 0
        games_df['rest_advantage'] = games_df['home_rest'] - games_df['away_rest']
        
        # Prepare features and target
        feature_cols = ['strength_diff', 'cold_game', 'windy_game', 'dome_game', 'rest_advantage', 'spread_line']
        
        # Filter out rows with missing data
        df_clean = games_df.dropna(subset=feature_cols + ['home_win'])
        
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
        model = xgb.XGBClassifier(random_state=42, n_estimators=50, eval_metric='logloss')
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"  Accuracy: {accuracy:.3f}")
        
        # Store model
        self.models['moneyline'] = model
        self.scalers['moneyline'] = scaler
        
        return model, accuracy
    
    def predict_live_games(self):
        """Make predictions for live games"""
        print("🔮 Making predictions for live games...")
        
        # Load live games
        live_df = self.load_sheet_data("live_picks_sheets")
        
        if live_df.empty:
            print("⚠️ No live games found")
            return pd.DataFrame()
        
        predictions = []
        
        for _, game in live_df.iterrows():
            try:
                # Get team strengths
                home_strength = self.team_strengths.get(game['home_team'], 0.5)
                away_strength = self.team_strengths.get(game['away_team'], 0.5)
                strength_diff = home_strength - away_strength
                
                # Prepare features
                temp = pd.to_numeric(game.get('temp', 65), errors='coerce')
                wind = pd.to_numeric(game.get('wind', 5), errors='coerce')
                
                features = {
                    'strength_diff': strength_diff,
                    'cold_game': 1 if temp < 40 else 0,
                    'windy_game': 1 if wind > 10 else 0,
                    'dome_game': 1 if game.get('roof') == 'dome' else 0,
                    'rest_advantage': 0,  # We don't have rest data in live games
                    'spread_line': pd.to_numeric(game.get('spread_line', 0), errors='coerce')
                }
                
                # Make prediction
                feature_vector = np.array([features[col] for col in [
                    'strength_diff', 'cold_game', 'windy_game', 'dome_game', 'rest_advantage', 'spread_line'
                ]]).reshape(1, -1)
                
                # Scale features
                feature_scaled = self.scalers['moneyline'].transform(feature_vector)
                
                # Get prediction
                home_win_prob = self.models['moneyline'].predict_proba(feature_scaled)[0][1]
                
                # Calculate betting value
                home_moneyline = pd.to_numeric(game.get('home_moneyline', 100), errors='coerce')
                away_moneyline = pd.to_numeric(game.get('away_moneyline', 100), errors='coerce')
                
                home_win_value = self.calculate_betting_value(home_win_prob, home_moneyline)
                away_win_value = self.calculate_betting_value(1 - home_win_prob, away_moneyline)
                
                # Calculate confidence
                confidence = max(home_win_prob, 1 - home_win_prob)
                
                prediction = {
                    'game_id': game['game_id'],
                    'matchup': game['matchup'],
                    'home_team': game['home_team'],
                    'away_team': game['away_team'],
                    'home_team_strength': round(home_strength, 3),
                    'away_team_strength': round(away_strength, 3),
                    'home_win_prob': round(home_win_prob, 3),
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
    
    def run_simple_predictions(self):
        """Run the simple prediction system"""
        print("🏈 Simple Live NFL Predictions")
        print("=" * 40)
        
        # Load historical data
        print("📊 Loading historical data...")
        games_df = self.load_sheet_data("historical_game_results_2021_2024")
        
        if games_df.empty:
            print("❌ No historical data found")
            return None
        
        # Calculate team strengths
        self.calculate_team_strengths(games_df)
        
        # Train model
        print("\n🚀 Training model...")
        model, accuracy = self.train_simple_model(games_df)
        
        if model is None:
            print("❌ Model training failed")
            return None
        
        print(f"✅ Model trained with {accuracy:.3f} accuracy")
        
        # Make predictions
        predictions_df = self.predict_live_games()
        
        if not predictions_df.empty:
            # Save predictions to Google Sheets
            self.save_predictions_to_sheet(predictions_df, "live_predictions")
            
            # Print summary
            print("\n📊 Live Predictions Summary:")
            print("-" * 40)
            for _, pred in predictions_df.iterrows():
                print(f"{pred['matchup']}")
                print(f"  Home Win Prob: {pred['home_win_prob']:.1%}")
                print(f"  Recommendation: {pred['recommendation']}")
                print(f"  Confidence: {pred['confidence']:.1%}")
                print()
        
        return predictions_df

def main():
    """Main function to run the simple prediction system"""
    # Configuration
    credentials_path = "C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json"
    spreadsheet_id = "1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU"
    
    # Initialize and run system
    nfl_system = SimpleLivePredictions(credentials_path, spreadsheet_id)
    predictions_df = nfl_system.run_simple_predictions()
    
    if predictions_df is not None:
        print("✅ Simple prediction system completed successfully!")
        print("📊 Check your Google Sheets for the latest predictions in the 'live_predictions' tab.")
    else:
        print("❌ Simple prediction system failed. Please check your data and try again.")

if __name__ == "__main__":
    main()



