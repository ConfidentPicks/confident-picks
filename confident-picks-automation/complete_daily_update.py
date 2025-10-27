import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from google.oauth2 import service_account
from googleapiclient.discovery import build
import warnings
from datetime import datetime
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
    
    headers_extended = headers + [f'col_{i}' for i in range(len(headers), max_cols)]
    
    data_aligned = []
    for row in data:
        aligned_row = row + [None] * (max_cols - len(row))
        data_aligned.append(aligned_row)

    df = pd.DataFrame(data_aligned, columns=headers_extended)
    return df

# ============================================================================
# WINNER PREDICTION MODEL
# ============================================================================

def create_winner_features(df):
    """Create features for winner prediction"""
    # Convert numeric columns
    numeric_cols = ['away_score', 'home_score', 'total', 'spread_line', 'total_line']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['gameday'] = pd.to_datetime(df['gameday'], errors='coerce')
    df = df.sort_values('gameday').reset_index(drop=True)
    
    team_stats = {}
    for team in df['away_team'].unique():
        if pd.notna(team):
            team_stats[team] = {
                'games_played': 0, 'wins': 0, 'points_for': 0, 'points_against': 0,
                'recent_form': [], 'home_wins': 0, 'away_wins': 0, 'recent_scores': [],
                'streak': 0, 'home_games': 0, 'away_games': 0
            }
    
    for idx, row in df.iterrows():
        if pd.isna(row['away_team']) or pd.isna(row['home_team']):
            continue
            
        away_team = row['away_team']
        home_team = row['home_team']
        away_stats = team_stats.get(away_team, {})
        home_stats = team_stats.get(home_team, {})
        away_games = max(away_stats.get('games_played', 0), 1)
        home_games = max(home_stats.get('games_played', 0), 1)
        
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
            df.at[idx, 'rest_advantage'] = float(row.get('home_rest', 0)) - float(row.get('away_rest', 0))
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

def train_winner_model(historical_df):
    """Train winner prediction model"""
    print("      Training winner model...")
    
    completed = historical_df[
        (historical_df['away_score'].notna()) & (historical_df['home_score'].notna()) &
        (historical_df['away_score'] != '') & (historical_df['home_score'] != '')
    ].copy()
    
    df_with_features = create_winner_features(completed)
    
    feature_columns = [
        'away_win_pct', 'home_win_pct', 'away_avg_points_for', 'home_avg_points_for',
        'away_avg_points_against', 'home_avg_points_against', 'away_recent_form', 'home_recent_form',
        'away_scoring_trend', 'home_scoring_trend', 'away_streak', 'home_streak',
        'home_field_advantage', 'rest_advantage', 'weather_impact',
        'point_differential_advantage', 'home_home_win_pct', 'away_away_win_pct',
        'home_offensive_efficiency', 'away_offensive_efficiency',
        'home_defensive_efficiency', 'away_defensive_efficiency',
        'home_momentum', 'away_momentum'
    ]
    
    X = df_with_features[feature_columns].copy().fillna(0)
    
    y = []
    for idx, row in df_with_features.iterrows():
        try:
            away_score = float(row['away_score'])
            home_score = float(row['home_score'])
            y.append(1 if home_score > away_score else 0)
        except (ValueError, TypeError):
            continue
    
    y = np.array(y)
    
    model = RandomForestClassifier(
        n_estimators=300, max_depth=12, min_samples_split=3,
        min_samples_leaf=1, max_features='sqrt', random_state=42
    )
    
    model.fit(X, y)
    print(f"         ✓ Trained on {len(X)} games")
    
    return model, feature_columns

def make_winner_predictions(model, df, feature_columns):
    """Make winner predictions"""
    df_with_features = create_winner_features(df)
    X = df_with_features[feature_columns].copy().fillna(0)
    
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)
    
    predicted_winners = []
    winner_confidences = []
    
    for idx, row in df_with_features.iterrows():
        away_team = row.get('away_team', '')
        home_team = row.get('home_team', '')
        
        pred = predictions[idx] if idx < len(predictions) else 0
        prob = probabilities[idx] if idx < len(probabilities) else [0.5, 0.5]
        
        if pred == 1:
            predicted_winner = home_team
            confidence = prob[1]
        else:
            predicted_winner = away_team
            confidence = prob[0]
        
        predicted_winners.append(predicted_winner)
        winner_confidences.append(round(confidence, 3))
    
    print(f"         ✓ {len(predicted_winners)} winner predictions")
    return predicted_winners, winner_confidences

# Continue in next message due to length...



