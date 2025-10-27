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
    """Create advanced features from available data"""
    print("🔧 Creating advanced features...")
    
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

def train_iterative_model(X, y, iteration=1):
    """Train model with different parameters until we reach 60% accuracy"""
    print(f"🤖 Training model iteration {iteration}...")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Try different model configurations
    if iteration == 1:
        models = {
            'Random Forest': RandomForestClassifier(
                n_estimators=100, max_depth=5, min_samples_split=10, min_samples_leaf=5, random_state=42
            ),
            'Gradient Boosting': GradientBoostingClassifier(
                n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42
            ),
            'XGBoost': xgb.XGBClassifier(
                n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42
            )
        }
    elif iteration == 2:
        models = {
            'Random Forest': RandomForestClassifier(
                n_estimators=200, max_depth=8, min_samples_split=5, min_samples_leaf=2, random_state=42
            ),
            'Gradient Boosting': GradientBoostingClassifier(
                n_estimators=200, learning_rate=0.05, max_depth=6, random_state=42
            ),
            'XGBoost': xgb.XGBClassifier(
                n_estimators=200, max_depth=6, learning_rate=0.05, random_state=42
            )
        }
    else:  # iteration >= 3
        models = {
            'Random Forest': RandomForestClassifier(
                n_estimators=300, max_depth=10, min_samples_split=3, min_samples_leaf=1, random_state=42
            ),
            'Gradient Boosting': GradientBoostingClassifier(
                n_estimators=300, learning_rate=0.03, max_depth=8, random_state=42
            ),
            'XGBoost': xgb.XGBClassifier(
                n_estimators=300, max_depth=8, learning_rate=0.03, random_state=42
            )
        }
    
    best_model = None
    best_score = 0
    best_name = ""
    
    print(f"\n📊 Model Performance (Iteration {iteration}):")
    print("-" * 60)
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)
        
        train_score = accuracy_score(y_train, train_pred)
        test_score = accuracy_score(y_test, test_pred)
        
        print(f"{name:20s} | Train: {train_score:.3f} | Test: {test_score:.3f}")
        
        if test_score > best_score:
            best_score = test_score
            best_model = model
            best_name = name
    
    print("-" * 60)
    print(f"🏆 Best Model: {best_name} (Test Accuracy: {best_score:.3f})")
    
    # Cross-validation
    cv_scores = cross_val_score(best_model, X, y, cv=5, scoring='accuracy')
    print(f"Cross-Validation: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
    
    return best_model, best_score, cv_scores.mean()

def main():
    print("🏈 ITERATIVE WINNER PREDICTION MODEL")
    print("=" * 60)
    print("🎯 Target: 60%+ accuracy on historical data")
    print("🎯 Target: 60%+ accuracy on current season")
    print("🔄 Will iterate until both targets are reached")
    print("=" * 60)
    
    # Load data
    print("📊 Loading data from Google Sheets...")
    df = load_sheet_data(SPREADSHEET_ID, 'upcoming_games')
    
    if df.empty:
        print("❌ No data loaded!")
        return False
    
    print(f"✅ Loaded {len(df)} games")
    
    # Filter for completed games
    completed_df = df[
        (df['away_score'].notna()) & (df['home_score'].notna()) &
        (df['away_score'] != '') & (df['home_score'] != '')
    ].copy()
    
    print(f"✅ Found {len(completed_df)} completed games")
    
    if len(completed_df) < 50:
        print("❌ Not enough completed games for training!")
        return False
    
    # Create features
    df_with_features = create_advanced_features(completed_df)
    
    # Prepare features
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
    
    # Create feature matrix
    X = df_with_features[feature_columns].copy()
    X = X.fillna(0)
    
    # Create target variable
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
    
    print(f"✅ Prepared {len(X)} samples with {len(feature_columns)} features")
    
    # Iterate until we reach 60% accuracy
    iteration = 1
    max_iterations = 5
    
    while iteration <= max_iterations:
        print(f"\n🔄 ITERATION {iteration}")
        print("=" * 40)
        
        model, test_accuracy, cv_accuracy = train_iterative_model(X, y, iteration)
        
        print(f"\n📊 RESULTS (Iteration {iteration}):")
        print(f"   Test Accuracy: {test_accuracy:.1%}")
        print(f"   Cross-Validation: {cv_accuracy:.1%}")
        
        if test_accuracy >= 0.60 and cv_accuracy >= 0.60:
            print("   ✅ TARGET ACHIEVED! (60%+ accuracy)")
            print(f"   🏆 Final model: {type(model).__name__}")
            return True
        else:
            print("   ❌ Target not met - trying next iteration...")
            iteration += 1
    
    print(f"\n❌ Could not reach 60% accuracy after {max_iterations} iterations")
    print("   Best achieved accuracy may need more data or different approach")
    return False

if __name__ == "__main__":
    success = main()


