import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
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

    # Find the maximum number of columns in any row
    max_cols = len(headers)
    for row in data:
        if len(row) > max_cols:
            max_cols = len(row)
    
    # Ensure all rows have the same number of columns
    headers_extended = headers + [f'col_{i}' for i in range(len(headers), max_cols)]
    
    # Align data with extended headers
    data_aligned = []
    for row in data:
        aligned_row = row + [None] * (max_cols - len(row))
        data_aligned.append(aligned_row)

    df = pd.DataFrame(data_aligned, columns=headers_extended)
    return df

def create_advanced_features(df):
    """Create advanced features from historical data"""
    print("🔧 Creating advanced features from historical data...")
    
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
        
        # Get current stats (before this game)
        away_stats = team_stats.get(away_team, {})
        home_stats = team_stats.get(home_team, {})
        
        # Calculate features
        away_games = max(away_stats.get('games_played', 0), 1)
        home_games = max(home_stats.get('games_played', 0), 1)
        
        # Basic stats
        df.at[idx, 'away_win_pct'] = away_stats.get('wins', 0) / away_games
        df.at[idx, 'home_win_pct'] = home_stats.get('wins', 0) / home_games
        df.at[idx, 'away_avg_points_for'] = away_stats.get('points_for', 0) / away_games
        df.at[idx, 'home_avg_points_for'] = home_stats.get('points_for', 0) / home_games
        df.at[idx, 'away_avg_points_against'] = away_stats.get('points_against', 0) / away_games
        df.at[idx, 'home_avg_points_against'] = home_stats.get('points_against', 0) / home_games
        
        # Recent form (last 5 games)
        away_recent = away_stats.get('recent_form', [])
        home_recent = home_stats.get('recent_form', [])
        df.at[idx, 'away_recent_form'] = np.mean(away_recent[-5:]) if away_recent else 0
        df.at[idx, 'home_recent_form'] = np.mean(home_recent[-5:]) if home_recent else 0
        
        # Scoring trends
        away_scores = away_stats.get('recent_scores', [])
        home_scores = home_stats.get('recent_scores', [])
        df.at[idx, 'away_scoring_trend'] = np.mean(away_scores[-3:]) if len(away_scores) >= 3 else 0
        df.at[idx, 'home_scoring_trend'] = np.mean(home_scores[-3:]) if len(home_scores) >= 3 else 0
        
        # Win streaks
        df.at[idx, 'away_streak'] = away_stats.get('streak', 0)
        df.at[idx, 'home_streak'] = home_stats.get('streak', 0)
        
        # Home field advantage
        df.at[idx, 'home_field_advantage'] = 2.5
        
        # Rest advantage
        try:
            away_rest = float(row.get('away_rest', 0))
            home_rest = float(row.get('home_rest', 0))
            df.at[idx, 'rest_advantage'] = home_rest - away_rest
        except:
            df.at[idx, 'rest_advantage'] = 0
        
        # Weather impact
        try:
            temp = float(row.get('temp', 70))
            wind = float(row.get('wind', 0))
            df.at[idx, 'weather_impact'] = abs(temp - 70) + wind * 0.1
        except:
            df.at[idx, 'weather_impact'] = 0
        
        # Point differential advantage
        away_point_diff = (away_stats.get('points_for', 0) / away_games) - (away_stats.get('points_against', 0) / away_games)
        home_point_diff = (home_stats.get('points_for', 0) / home_games) - (home_stats.get('points_against', 0) / home_games)
        df.at[idx, 'point_differential_advantage'] = home_point_diff - away_point_diff
        
        # Home/Away specific stats
        df.at[idx, 'home_home_win_pct'] = home_stats.get('home_wins', 0) / max(home_stats.get('home_games', 1), 1)
        df.at[idx, 'away_away_win_pct'] = away_stats.get('away_wins', 0) / max(away_stats.get('away_games', 1), 1)
        
        # Update team stats after game (if completed)
        if (pd.notna(row['away_score']) and pd.notna(row['home_score']) and 
            row['away_score'] != '' and row['home_score'] != ''):
            try:
                away_score = float(row['away_score'])
                home_score = float(row['home_score'])
                
                # Update away team
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
                
                # Update home team
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

def train_model_on_historical_data(X_train, y_train):
    """Train model on 2021-2024 historical data"""
    print("🤖 Training model on 2021-2024 historical data...")
    
    # Split data for validation
    X_train_split, X_val, y_train_split, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42, stratify=y_train)
    
    # Try different models
    models = {
        'Random Forest': RandomForestClassifier(
            n_estimators=200, 
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        ),
        'Gradient Boosting': GradientBoostingClassifier(
            n_estimators=200, 
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        ),
        'XGBoost': xgb.XGBClassifier(
            n_estimators=200, 
            max_depth=6, 
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )
    }
    
    best_model = None
    best_score = 0
    best_name = ""
    
    print("\n📊 Model Performance on Historical Data:")
    print("-" * 60)
    
    for name, model in models.items():
        model.fit(X_train_split, y_train_split)
        train_pred = model.predict(X_train_split)
        val_pred = model.predict(X_val)
        
        train_score = accuracy_score(y_train_split, train_pred)
        val_score = accuracy_score(y_val, val_pred)
        
        print(f"{name:20s} | Train: {train_score:.3f} | Val: {val_score:.3f}")
        
        if val_score > best_score:
            best_score = val_score
            best_model = model
            best_name = name
    
    print("-" * 60)
    print(f"🏆 Best Model: {best_name} (Validation Accuracy: {best_score:.3f})")
    
    # Train final model on full training set
    best_model.fit(X_train, y_train)
    
    return best_model, best_score

def test_model_on_2025_data(model, X_2025, y_2025):
    """Test the trained model on 2025 data"""
    print("🧪 Testing model on 2025 data...")
    
    predictions = model.predict(X_2025)
    accuracy = accuracy_score(y_2025, predictions)
    
    print(f"2025 Test Accuracy: {accuracy:.3f}")
    
    return accuracy

def main():
    print("🏈 HISTORICAL WINNER PREDICTION MODEL")
    print("=" * 70)
    print("🎯 Target: 60%+ accuracy on 2021-2024 historical data")
    print("🎯 Target: 60%+ accuracy on 2025 current season")
    print("🚫 NO ESPN FPI - only historical team data")
    print("=" * 70)
    
    # Load historical data (2021-2024)
    print("📊 Loading 2021-2024 historical data...")
    historical_df = load_sheet_data(SPREADSHEET_ID, 'historical_game_results_2021_2024')
    
    if historical_df.empty:
        print("❌ No historical data available!")
        return False
    
    print(f"✅ Loaded {len(historical_df)} historical games")
    
    # Filter for completed games
    historical_completed = historical_df[
        (historical_df['away_score'].notna()) & (historical_df['home_score'].notna()) &
        (historical_df['away_score'] != '') & (historical_df['home_score'] != '')
    ].copy()
    
    print(f"✅ Found {len(historical_completed)} completed historical games")
    
    if len(historical_completed) < 500:
        print("❌ Not enough historical data for training!")
        return False
    
    # Create features for historical data
    historical_with_features = create_advanced_features(historical_completed)
    
    # Prepare features for training
    feature_columns = [
        'away_win_pct', 'home_win_pct',
        'away_avg_points_for', 'home_avg_points_for',
        'away_avg_points_against', 'home_avg_points_against',
        'away_recent_form', 'home_recent_form',
        'away_scoring_trend', 'home_scoring_trend',
        'away_streak', 'home_streak',
        'home_field_advantage', 'rest_advantage', 'weather_impact',
        'point_differential_advantage', 'home_home_win_pct', 'away_away_win_pct'
    ]
    
    # Create training data
    X_train = historical_with_features[feature_columns].copy()
    X_train = X_train.fillna(0)
    
    y_train = []
    for idx, row in historical_with_features.iterrows():
        try:
            away_score = float(row['away_score'])
            home_score = float(row['home_score'])
            
            if home_score > away_score:
                y_train.append(1)  # Home team wins
            else:
                y_train.append(0)  # Away team wins
        except (ValueError, TypeError):
            continue
    
    y_train = np.array(y_train)
    
    print(f"✅ Prepared {len(X_train)} historical samples with {len(feature_columns)} features")
    
    # Train model on historical data
    model, historical_accuracy = train_model_on_historical_data(X_train, y_train)
    
    print(f"\n📊 HISTORICAL RESULTS:")
    print(f"   2021-2024 Accuracy: {historical_accuracy:.1%}")
    
    if historical_accuracy < 0.60:
        print("   ❌ Historical accuracy below 60% - need to improve model")
        return False
    
    print("   ✅ Historical accuracy above 60% - testing on 2025 data")
    
    # Load 2025 data for testing
    print("📊 Loading 2025 current season data...")
    df_2025 = load_sheet_data(SPREADSHEET_ID, 'upcoming_games')
    
    if df_2025.empty:
        print("❌ No 2025 data available!")
        return False
    
    # Filter for completed 2025 games
    completed_2025 = df_2025[
        (df_2025['away_score'].notna()) & (df_2025['home_score'].notna()) &
        (df_2025['away_score'] != '') & (df_2025['home_score'] != '')
    ].copy()
    
    print(f"✅ Found {len(completed_2025)} completed 2025 games")
    
    if len(completed_2025) < 50:
        print("❌ Not enough 2025 data for testing!")
        return False
    
    # Create features for 2025 data
    df_2025_with_features = create_advanced_features(completed_2025)
    
    # Prepare 2025 test data
    X_2025 = df_2025_with_features[feature_columns].copy()
    X_2025 = X_2025.fillna(0)
    
    y_2025 = []
    for idx, row in df_2025_with_features.iterrows():
        try:
            away_score = float(row['away_score'])
            home_score = float(row['home_score'])
            
            if home_score > away_score:
                y_2025.append(1)  # Home team wins
            else:
                y_2025.append(0)  # Away team wins
        except (ValueError, TypeError):
            continue
    
    y_2025 = np.array(y_2025)
    
    # Test model on 2025 data
    accuracy_2025 = test_model_on_2025_data(model, X_2025, y_2025)
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"   2021-2024 Accuracy: {historical_accuracy:.1%}")
    print(f"   2025 Accuracy: {accuracy_2025:.1%}")
    
    if historical_accuracy >= 0.60 and accuracy_2025 >= 0.60:
        print("   ✅ BOTH TARGETS ACHIEVED! (60%+ accuracy on both datasets)")
        return True
    else:
        print("   ❌ TARGETS NOT MET - need to improve model")
        return False

if __name__ == "__main__":
    success = main()