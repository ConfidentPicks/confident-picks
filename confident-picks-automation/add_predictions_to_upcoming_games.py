#!/usr/bin/env python3

"""
Add Predictions to Upcoming Games
================================

This script adds predictions to the upcoming_games tab without messing up the structure
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Google Sheets integration
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ML Libraries
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import xgboost as xgb

# Data processing
from datetime import datetime
import os

class UpcomingGamesPredictor:
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
    
    def load_sheet_data(self, sheet_name):
        """Load data from Google Sheets"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!A:ZZ"
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                print(f"⚠️ No data found in {sheet_name}")
                return pd.DataFrame()
            
            # Handle rows with different lengths
            max_cols = max(len(row) for row in values)
            headers = values[0] + [''] * (max_cols - len(values[0]))
            
            # Pad rows to match header length
            data_rows = []
            for row in values[1:]:
                padded_row = row + [''] * (max_cols - len(row))
                data_rows.append(padded_row)
            
            # Convert to DataFrame
            df = pd.DataFrame(data_rows, columns=headers)
            
            print(f"✅ Loaded {len(df)} rows from {sheet_name}")
            return df
            
        except Exception as e:
            print(f"❌ Error loading data from {sheet_name}: {e}")
            return pd.DataFrame()
    
    def update_upcoming_games_predictions(self, upcoming_df, predictions):
        """Update the upcoming_games sheet with predictions"""
        try:
            print("\n📝 Writing predictions to upcoming_games...")
            
            # Find prediction column indices
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range="upcoming_games!1:1"
            ).execute()
            
            headers = result.get('values', [[]])[0]
            
            # Find prediction column indices
            col_indices = {}
            for i, header in enumerate(headers):
                if 'predicted_winner' in header.lower():
                    col_indices['predicted_winner'] = i
                elif 'home_win_probability' in header.lower():
                    col_indices['home_win_probability'] = i
                elif 'away_win_probability' in header.lower():
                    col_indices['away_win_probability'] = i
                elif 'confidence_score' in header.lower():
                    col_indices['confidence_score'] = i
                elif 'betting_recommendation' in header.lower():
                    col_indices['betting_recommendation'] = i
                elif 'betting_value' in header.lower():
                    col_indices['betting_value'] = i
                elif 'model_last_updated' in header.lower():
                    col_indices['model_last_updated'] = i
            
            print(f"Found prediction columns at: {col_indices}")
            
            # Update predictions in batches
            updates = []
            
            for idx, row in upcoming_df.iterrows():
                game_id = row.get('game_id', '')
                
                if game_id in predictions:
                    pred = predictions[game_id]
                    row_num = idx + 2  # +2 because row 1 is headers
                    
                    # Add updates for each prediction column
                    for col_name, col_idx in col_indices.items():
                        if col_name == 'predicted_winner':
                            updates.append({'range': f"upcoming_games!{chr(65+col_idx)}{row_num}", 'values': [[pred['predicted_winner']]]})
                        elif col_name == 'home_win_probability':
                            updates.append({'range': f"upcoming_games!{chr(65+col_idx)}{row_num}", 'values': [[pred['home_win_probability']]]})
                        elif col_name == 'away_win_probability':
                            updates.append({'range': f"upcoming_games!{chr(65+col_idx)}{row_num}", 'values': [[pred['away_win_probability']]]})
                        elif col_name == 'confidence_score':
                            updates.append({'range': f"upcoming_games!{chr(65+col_idx)}{row_num}", 'values': [[pred['confidence_score']]]})
                        elif col_name == 'betting_recommendation':
                            updates.append({'range': f"upcoming_games!{chr(65+col_idx)}{row_num}", 'values': [[pred['betting_recommendation']]]})
                        elif col_name == 'betting_value':
                            updates.append({'range': f"upcoming_games!{chr(65+col_idx)}{row_num}", 'values': [[pred['betting_value']]]})
                        elif col_name == 'model_last_updated':
                            updates.append({'range': f"upcoming_games!{chr(65+col_idx)}{row_num}", 'values': [[pred['model_last_updated']]]})
                    
                    print(f"  ✓ {row.get('away_team', '?')} @ {row.get('home_team', '?')}: {pred['predicted_winner']} ({pred['confidence_score']:.1%} confidence)")
            
            # Execute batch updates (in chunks to avoid rate limits)
            chunk_size = 50
            for i in range(0, len(updates), chunk_size):
                chunk = updates[i:i+chunk_size]
                self.service.spreadsheets().values().batchUpdate(
                    spreadsheetId=self.spreadsheet_id,
                    body={'valueInputOption': 'USER_ENTERED', 'data': chunk}
                ).execute()
                print(f"  Updated chunk {i//chunk_size + 1}/{(len(updates)-1)//chunk_size + 1}")
            
            print("✅ Successfully updated upcoming_games with predictions!")
            
        except Exception as e:
            print(f"❌ Error updating predictions: {e}")
    
    def calculate_team_strengths(self, games_df):
        """Calculate team strength ratings from historical data"""
        print("📊 Calculating team strength ratings...")
        
        team_strengths = {}
        all_teams = set(games_df['home_team'].unique()) | set(games_df['away_team'].unique())
        
        for team in all_teams:
            team_games = games_df[(games_df['home_team'] == team) | (games_df['away_team'] == team)]
            
            if len(team_games) > 0:
                wins = 0
                total_games = len(team_games)
                total_points_for = 0
                total_points_against = 0
                
                for _, game in team_games.iterrows():
                    home_score = pd.to_numeric(game['home_score'], errors='coerce')
                    away_score = pd.to_numeric(game['away_score'], errors='coerce')
                    
                    if pd.isna(home_score) or pd.isna(away_score):
                        continue
                    
                    if game['home_team'] == team:
                        team_score = home_score
                        opponent_score = away_score
                        if home_score > away_score:
                            wins += 1
                    else:
                        team_score = away_score
                        opponent_score = home_score
                        if away_score > home_score:
                            wins += 1
                    
                    total_points_for += team_score
                    total_points_against += opponent_score
                
                win_pct = wins / total_games if total_games > 0 else 0.5
                points_diff = total_points_for - total_points_against
                strength = (win_pct * 0.6 + (points_diff / (total_games * 10)) * 0.4)
                strength = max(0.1, min(0.9, strength))
                team_strengths[team] = strength
            else:
                team_strengths[team] = 0.5
        
        self.team_strengths = team_strengths
        print(f"✅ Calculated strength ratings for {len(team_strengths)} teams")
        
        return team_strengths
    
    def train_prediction_model(self, games_df):
        """Train prediction model"""
        print("🎯 Training Prediction Model...")
        
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
        
        # Prepare features
        feature_cols = ['strength_diff', 'cold_game', 'windy_game', 'dome_game', 'rest_advantage', 'spread_line']
        
        # Filter out rows with missing data
        df_clean = games_df.dropna(subset=feature_cols + ['home_win'])
        
        print(f"  Training data: {len(df_clean)} games")
        
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
        
        print(f"  Model Accuracy: {accuracy:.1%}")
        
        # Store model
        self.models['moneyline'] = model
        self.scalers['moneyline'] = scaler
        
        return model, accuracy
    
    def predict_game(self, game_row):
        """Make a prediction for a single game"""
        try:
            home_team = game_row.get('home_team', '')
            away_team = game_row.get('away_team', '')
            
            home_strength = self.team_strengths.get(home_team, 0.5)
            away_strength = self.team_strengths.get(away_team, 0.5)
            strength_diff = home_strength - away_strength
            
            # Prepare features
            temp = pd.to_numeric(game_row.get('temp', 65), errors='coerce')
            if pd.isna(temp):
                temp = 65
                
            wind = pd.to_numeric(game_row.get('wind', 5), errors='coerce')
            if pd.isna(wind):
                wind = 5
                
            spread_line = pd.to_numeric(game_row.get('spread_line', 0), errors='coerce')
            if pd.isna(spread_line):
                spread_line = 0
            
            features = {
                'strength_diff': strength_diff,
                'cold_game': 1 if temp < 40 else 0,
                'windy_game': 1 if wind > 10 else 0,
                'dome_game': 1 if game_row.get('roof', '').lower() in ['dome', 'indoor'] else 0,
                'rest_advantage': 0,
                'spread_line': spread_line
            }
            
            # Make prediction
            feature_vector = np.array([features[col] for col in [
                'strength_diff', 'cold_game', 'windy_game', 'dome_game', 'rest_advantage', 'spread_line'
            ]]).reshape(1, -1)
            
            # Scale features
            feature_scaled = self.scalers['moneyline'].transform(feature_vector)
            
            # Get prediction probabilities
            probabilities = self.models['moneyline'].predict_proba(feature_scaled)[0]
            home_win_prob = float(probabilities[1])
            away_win_prob = float(probabilities[0])
            
            # Calculate confidence
            confidence = max(home_win_prob, away_win_prob)
            
            # Determine winner
            predicted_winner = home_team if home_win_prob > 0.5 else away_team
            
            # Calculate betting value
            home_moneyline = pd.to_numeric(game_row.get('home_moneyline', 100), errors='coerce')
            away_moneyline = pd.to_numeric(game_row.get('away_moneyline', 100), errors='coerce')
            
            if pd.isna(home_moneyline):
                home_moneyline = 100
            if pd.isna(away_moneyline):
                away_moneyline = 100
            
            home_value = self.calculate_betting_value(home_win_prob, home_moneyline)
            away_value = self.calculate_betting_value(away_win_prob, away_moneyline)
            
            # Get recommendation
            if home_value > 0.05:
                recommendation = f"BET HOME ({home_team})"
                betting_value = home_value
            elif away_value > 0.05:
                recommendation = f"BET AWAY ({away_team})"
                betting_value = away_value
            else:
                recommendation = "NO BET"
                betting_value = max(home_value, away_value)
            
            return {
                'predicted_winner': predicted_winner,
                'home_win_probability': round(home_win_prob, 3),
                'away_win_probability': round(away_win_prob, 3),
                'confidence_score': round(confidence, 3),
                'betting_recommendation': recommendation,
                'betting_value': round(betting_value, 3),
                'model_last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"⚠️ Error predicting game: {e}")
            return None
    
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
    
    def run_upcoming_games_predictions(self):
        """Run the upcoming games prediction system"""
        print("🏈 Upcoming Games Prediction System")
        print("=" * 60)
        
        # Load historical data
        print("\n📊 Loading historical data...")
        games_df = self.load_sheet_data("historical_game_results_2021_2024")
        
        if games_df.empty:
            print("❌ No historical data found")
            return
        
        # Calculate team strengths
        self.calculate_team_strengths(games_df)
        
        # Train model
        print("\n🚀 Training model...")
        model, accuracy = self.train_prediction_model(games_df)
        
        if model is None:
            print("❌ Model training failed")
            return
        
        print(f"✅ Model ready with {accuracy:.1%} accuracy")
        
        # Load upcoming games
        print("\n🔮 Making predictions for upcoming games...")
        upcoming_df = self.load_sheet_data("upcoming_games")
        
        if upcoming_df.empty:
            print("⚠️ No upcoming games found")
            return
        
        # Make predictions for all games
        predictions = {}
        for idx, game in upcoming_df.iterrows():
            # Skip games that already have results
            if game.get('result', '') != '' and game.get('result', '') != '0':
                continue
            
            prediction = self.predict_game(game)
            if prediction:
                game_id = game.get('game_id', idx)
                predictions[game_id] = prediction
        
        # Update the upcoming games sheet
        self.update_upcoming_games_predictions(upcoming_df, predictions)
        
        print("\n" + "=" * 60)
        print("✅ Upcoming games prediction system complete!")
        print(f"\n📊 Updated {len(predictions)} games in upcoming_games")
        print("   Check your upcoming_games tab for predictions!")

def main():
    """Main function"""
    # Configuration
    credentials_path = "C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json"
    spreadsheet_id = "1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU"
    
    # Initialize and run
    system = UpcomingGamesPredictor(credentials_path, spreadsheet_id)
    system.run_upcoming_games_predictions()

if __name__ == "__main__":
    main()



