import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
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

def col_to_a1(col_idx):
    """Convert 0-indexed column number to A1-style column letter"""
    letter = ''
    while col_idx >= 0:
        letter = chr(col_idx % 26 + ord('A')) + letter
        col_idx = col_idx // 26 - 1
    return letter

def load_sheet_data(spreadsheet_id, sheet_name):
    """Load data from Google Sheets"""
    service = get_sheets_service()
    range_name = f"'{sheet_name}'!A:ZZ"
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
    
    headers_extended = headers + [f'col_{i}' for i in range(len(headers), max_cols)]
    
    data_aligned = []
    for row in data:
        aligned_row = row + [None] * (max_cols - len(row))
        data_aligned.append(aligned_row)

    df = pd.DataFrame(data_aligned, columns=headers_extended)
    return df

def create_features(df):
    """Create features from game data"""
    print("🔧 Creating features...")
    
    # Convert numeric columns
    numeric_cols = ['away_score', 'home_score', 'total', 'spread_line', 'total_line']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Sort by date
    df['gameday'] = pd.to_datetime(df['gameday'], errors='coerce')
    df = df.sort_values('gameday').reset_index(drop=True)
    
    # Initialize team stats
    team_stats = {}
    for team in df['away_team'].unique():
        if pd.notna(team):
            team_stats[team] = {
                'games_played': 0,
                'wins': 0,
                'points_for': 0,
                'points_against': 0,
                'recent_form': [],
                'home_wins': 0,
                'away_wins': 0,
                'recent_scores': [],
                'streak': 0,
                'home_games': 0,
                'away_games': 0
            }
    
    # Calculate features for each game
    for idx, row in df.iterrows():
        if pd.isna(row['away_team']) or pd.isna(row['home_team']):
            continue
            
        away_team = row['away_team']
        home_team = row['home_team']
        
        away_stats = team_stats.get(away_team, {})
        home_stats = team_stats.get(home_team, {})
        
        away_games = max(away_stats.get('games_played', 0), 1)
        home_games = max(home_stats.get('games_played', 0), 1)
        
        # Create features
        df.at[idx, 'away_win_pct'] = away_stats.get('wins', 0) / away_games
        df.at[idx, 'home_win_pct'] = home_stats.get('wins', 0) / home_games
        df.at[idx, 'away_avg_points_for'] = away_stats.get('points_for', 0) / away_games
        df.at[idx, 'home_avg_points_for'] = home_stats.get('points_for', 0) / home_games
        df.at[idx, 'away_avg_points_against'] = away_stats.get('points_against', 0) / away_games
        df.at[idx, 'home_avg_points_against'] = home_stats.get('points_against', 0) / home_games
        
        away_recent = away_stats.get('recent_form', [])
        home_recent = home_stats.get('recent_form', [])
        df.at[idx, 'away_recent_form'] = np.mean(away_recent[-5:]) if away_recent else 0
        df.at[idx, 'home_recent_form'] = np.mean(home_recent[-5:]) if home_recent else 0
        
        away_scores = away_stats.get('recent_scores', [])
        home_scores = home_stats.get('recent_scores', [])
        df.at[idx, 'away_scoring_trend'] = np.mean(away_scores[-3:]) if len(away_scores) >= 3 else 0
        df.at[idx, 'home_scoring_trend'] = np.mean(home_scores[-3:]) if len(home_scores) >= 3 else 0
        
        df.at[idx, 'away_streak'] = away_stats.get('streak', 0)
        df.at[idx, 'home_streak'] = home_stats.get('streak', 0)
        df.at[idx, 'home_field_advantage'] = 2.5
        
        try:
            away_rest = float(row.get('away_rest', 0))
            home_rest = float(row.get('home_rest', 0))
            df.at[idx, 'rest_advantage'] = home_rest - away_rest
        except:
            df.at[idx, 'rest_advantage'] = 0
        
        try:
            temp = float(row.get('temp', 70))
            wind = float(row.get('wind', 0))
            df.at[idx, 'weather_impact'] = abs(temp - 70) + wind * 0.1
        except:
            df.at[idx, 'weather_impact'] = 0
        
        away_point_diff = (away_stats.get('points_for', 0) / away_games) - (away_stats.get('points_against', 0) / away_games)
        home_point_diff = (home_stats.get('points_for', 0) / home_games) - (home_stats.get('points_against', 0) / home_games)
        df.at[idx, 'point_differential_advantage'] = home_point_diff - away_point_diff
        
        df.at[idx, 'home_home_win_pct'] = home_stats.get('home_wins', 0) / max(home_stats.get('home_games', 1), 1)
        df.at[idx, 'away_away_win_pct'] = away_stats.get('away_wins', 0) / max(away_stats.get('away_games', 1), 1)
        
        df.at[idx, 'home_offensive_efficiency'] = home_stats.get('points_for', 0) / max(home_stats.get('games_played', 1), 1)
        df.at[idx, 'away_offensive_efficiency'] = away_stats.get('points_for', 0) / max(away_stats.get('games_played', 1), 1)
        df.at[idx, 'home_defensive_efficiency'] = home_stats.get('points_against', 0) / max(home_stats.get('games_played', 1), 1)
        df.at[idx, 'away_defensive_efficiency'] = away_stats.get('points_against', 0) / max(away_stats.get('games_played', 1), 1)
        
        df.at[idx, 'home_momentum'] = np.mean(home_recent[-3:]) if len(home_recent) >= 3 else 0
        df.at[idx, 'away_momentum'] = np.mean(away_recent[-3:]) if len(away_recent) >= 3 else 0
        
        # Update team stats after game (if completed)
        if (pd.notna(row['away_score']) and pd.notna(row['home_score']) and 
            row['away_score'] != '' and row['home_score'] != ''):
            try:
                away_score = float(row['away_score'])
                home_score = float(row['home_score'])
                
                team_stats[away_team]['games_played'] += 1
                team_stats[away_team]['away_games'] += 1
                team_stats[away_team]['points_for'] += away_score
                team_stats[away_team]['points_against'] += home_score
                team_stats[away_team]['recent_scores'].append(away_score)
                
                if away_score > home_score:
                    team_stats[away_team]['wins'] += 1
                    team_stats[away_team]['away_wins'] += 1
                    team_stats[away_team]['recent_form'].append(1)
                    team_stats[away_team]['streak'] = max(0, team_stats[away_team]['streak']) + 1
                else:
                    team_stats[away_team]['recent_form'].append(0)
                    team_stats[away_team]['streak'] = min(0, team_stats[away_team]['streak']) - 1
                
                team_stats[home_team]['games_played'] += 1
                team_stats[home_team]['home_games'] += 1
                team_stats[home_team]['points_for'] += home_score
                team_stats[home_team]['points_against'] += away_score
                team_stats[home_team]['recent_scores'].append(home_score)
                
                if home_score > away_score:
                    team_stats[home_team]['wins'] += 1
                    team_stats[home_team]['home_wins'] += 1
                    team_stats[home_team]['recent_form'].append(1)
                    team_stats[home_team]['streak'] = max(0, team_stats[home_team]['streak']) + 1
                else:
                    team_stats[home_team]['recent_form'].append(0)
                    team_stats[home_team]['streak'] = min(0, team_stats[home_team]['streak']) - 1
                    
            except (ValueError, TypeError):
                continue
    
    return df

def train_model(historical_df):
    """Train the winner prediction model"""
    print("🤖 Training winner prediction model...")
    
    # Filter for completed games
    completed = historical_df[
        (historical_df['away_score'].notna()) & (historical_df['home_score'].notna()) &
        (historical_df['away_score'] != '') & (historical_df['home_score'] != '')
    ].copy()
    
    print(f"✅ Training on {len(completed)} completed games")
    
    # Create features
    df_with_features = create_features(completed)
    
    # Feature columns
    feature_columns = [
        'away_win_pct', 'home_win_pct',
        'away_avg_points_for', 'home_avg_points_for',
        'away_avg_points_against', 'home_avg_points_against',
        'away_recent_form', 'home_recent_form',
        'away_scoring_trend', 'home_scoring_trend',
        'away_streak', 'home_streak',
        'home_field_advantage', 'rest_advantage', 'weather_impact',
        'point_differential_advantage', 'home_home_win_pct', 'away_away_win_pct',
        'home_offensive_efficiency', 'away_offensive_efficiency',
        'home_defensive_efficiency', 'away_defensive_efficiency',
        'home_momentum', 'away_momentum'
    ]
    
    # Create training data
    X = df_with_features[feature_columns].copy()
    X = X.fillna(0)
    
    y = []
    for idx, row in df_with_features.iterrows():
        try:
            away_score = float(row['away_score'])
            home_score = float(row['home_score'])
            
            if home_score > away_score:
                y.append(1)  # Home team wins
            else:
                y.append(0)  # Away team wins
        except (ValueError, TypeError):
            continue
    
    y = np.array(y)
    
    # Train model
    model = RandomForestClassifier(
        n_estimators=300, 
        max_depth=12,
        min_samples_split=3,
        min_samples_leaf=1,
        max_features='sqrt',
        random_state=42
    )
    
    model.fit(X, y)
    
    print(f"✅ Model trained successfully")
    
    return model, feature_columns

def make_predictions(model, df, feature_columns):
    """Make predictions for all games"""
    print("🔮 Making predictions for all games...")
    
    # Create features for all games
    df_with_features = create_features(df)
    
    # Prepare features
    X = df_with_features[feature_columns].copy()
    X = X.fillna(0)
    
    # Make predictions
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)
    
    # Create prediction results
    predicted_winners = []
    winner_confidences = []
    
    for idx, row in df_with_features.iterrows():
        away_team = row.get('away_team', '')
        home_team = row.get('home_team', '')
        
        # Get prediction
        pred = predictions[idx] if idx < len(predictions) else 0
        prob = probabilities[idx] if idx < len(probabilities) else [0.5, 0.5]
        
        # Determine predicted winner and confidence
        if pred == 1:  # Home team wins
            predicted_winner = home_team
            confidence = prob[1]  # Probability of home team winning
        else:  # Away team wins
            predicted_winner = away_team
            confidence = prob[0]  # Probability of away team winning
        
        predicted_winners.append(predicted_winner)
        winner_confidences.append(round(confidence, 3))
    
    return predicted_winners, winner_confidences

def update_sheet(predicted_winners, winner_confidences):
    """Update Google Sheet with predictions"""
    print("📤 Updating Google Sheet with predictions...")
    
    service = get_sheets_service()
    
    # Get column indices
    # AX = column 49 (0-indexed)
    # AZ = column 51 (0-indexed)
    ax_col = 49  # predicted_winner
    az_col = 51  # winner_confidence
    
    # Prepare updates
    updates = []
    
    # Update predicted_winner (Column AX)
    ax_values = [[winner] for winner in predicted_winners]
    updates.append({
        'range': f'upcoming_games!{col_to_a1(ax_col)}2:{col_to_a1(ax_col)}{len(predicted_winners) + 1}',
        'values': ax_values
    })
    
    # Update winner_confidence (Column AZ)
    az_values = [[conf] for conf in winner_confidences]
    updates.append({
        'range': f'upcoming_games!{col_to_a1(az_col)}2:{col_to_a1(az_col)}{len(winner_confidences) + 1}',
        'values': az_values
    })
    
    # Execute batch update
    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': updates
    }
    
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=body).execute()
    
    print(f"✅ Updated {len(predicted_winners)} predictions")

def main():
    print("🏈 WINNER PREDICTION MODEL - SHEET POPULATION")
    print("=" * 60)
    print("📊 Populating columns:")
    print("   - AX: predicted_winner")
    print("   - AZ: winner_confidence")
    print("=" * 60)
    
    # Load historical data for training
    print("📊 Loading historical data for training...")
    historical_df = load_sheet_data(SPREADSHEET_ID, 'historical_game_results_2021_2024')
    
    if historical_df.empty:
        print("❌ No historical data available!")
        return False
    
    # Train model
    model, feature_columns = train_model(historical_df)
    
    # Load 2025 data for predictions
    print("📊 Loading 2025 data for predictions...")
    df_2025 = load_sheet_data(SPREADSHEET_ID, 'upcoming_games')
    
    if df_2025.empty:
        print("❌ No 2025 data available!")
        return False
    
    print(f"✅ Loaded {len(df_2025)} games for prediction")
    
    # Make predictions
    predicted_winners, winner_confidences = make_predictions(model, df_2025, feature_columns)
    
    # Update sheet
    update_sheet(predicted_winners, winner_confidences)
    
    print("\n✅ PREDICTIONS SUCCESSFULLY POPULATED!")
    print(f"   - Column AX (predicted_winner): {len(predicted_winners)} predictions")
    print(f"   - Column AZ (winner_confidence): {len(winner_confidences)} confidence scores")
    print("\n📊 Sample predictions:")
    for i in range(min(10, len(predicted_winners))):
        print(f"   Game {i+1}: {predicted_winners[i]} (confidence: {winner_confidences[i]:.1%})")
    
    return True

if __name__ == "__main__":
    success = main()


