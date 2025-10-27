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

def create_team_features(df):
    """Create team-based features for prediction"""
    print("🔧 Creating team features...")
    
    # Group by team and calculate rolling averages
    team_stats = {}
    
    for team in df['away_team'].unique():
        if pd.isna(team):
            continue
            
        team_data = df[(df['away_team'] == team) | (df['home_team'] == team)].copy()
        team_data = team_data.sort_values('gameday')
        
        # Calculate rolling averages (only using past data)
        team_stats[team] = {
            'games_played': 0,
            'wins': 0,
            'home_wins': 0,
            'away_wins': 0,
            'points_for': 0,
            'points_against': 0,
            'recent_form': []  # Last 5 games results
        }
    
    # Calculate cumulative stats for each game
    for idx, row in df.iterrows():
        if pd.isna(row['away_team']) or pd.isna(row['home_team']):
            continue
            
        away_team = row['away_team']
        home_team = row['home_team']
        
        # Get current stats (before this game)
        away_stats = team_stats.get(away_team, {})
        home_stats = team_stats.get(home_team, {})
        
        # Add features to the row
        df.at[idx, 'away_games_played'] = away_stats.get('games_played', 0)
        df.at[idx, 'home_games_played'] = home_stats.get('games_played', 0)
        df.at[idx, 'away_win_pct'] = away_stats.get('wins', 0) / max(away_stats.get('games_played', 1), 1)
        df.at[idx, 'home_win_pct'] = home_stats.get('wins', 0) / max(home_stats.get('games_played', 1), 1)
        df.at[idx, 'away_avg_points_for'] = away_stats.get('points_for', 0) / max(away_stats.get('games_played', 1), 1)
        df.at[idx, 'home_avg_points_for'] = home_stats.get('points_for', 0) / max(home_stats.get('games_played', 1), 1)
        df.at[idx, 'away_avg_points_against'] = away_stats.get('points_against', 0) / max(away_stats.get('games_played', 1), 1)
        df.at[idx, 'home_avg_points_against'] = home_stats.get('points_against', 0) / max(home_stats.get('games_played', 1), 1)
        
        # Recent form (last 5 games)
        away_recent = away_stats.get('recent_form', [])
        home_recent = home_stats.get('recent_form', [])
        df.at[idx, 'away_recent_form'] = np.mean(away_recent[-5:]) if away_recent else 0
        df.at[idx, 'home_recent_form'] = np.mean(home_recent[-5:]) if home_recent else 0
        
        # Update stats after this game (if game is completed)
        if (pd.notna(row['away_score']) and pd.notna(row['home_score']) and 
            row['away_score'] != '' and row['home_score'] != ''):
            try:
                away_score = float(row['away_score'])
                home_score = float(row['home_score'])
            except (ValueError, TypeError):
                continue
            
            # Update away team stats
            team_stats[away_team]['games_played'] += 1
            team_stats[away_team]['points_for'] += away_score
            team_stats[away_team]['points_against'] += home_score
            if away_score > home_score:
                team_stats[away_team]['wins'] += 1
                team_stats[away_team]['recent_form'].append(1)
            else:
                team_stats[away_team]['recent_form'].append(0)
            
            # Update home team stats
            team_stats[home_team]['games_played'] += 1
            team_stats[home_team]['points_for'] += home_score
            team_stats[home_team]['points_against'] += away_score
            if home_score > away_score:
                team_stats[home_team]['wins'] += 1
                team_stats[home_team]['home_wins'] += 1
                team_stats[home_team]['recent_form'].append(1)
            else:
                team_stats[home_team]['recent_form'].append(0)
    
    return df

def add_espn_fpi_features(df):
    """Add ESPN FPI features (mock data for now - will integrate real FPI later)"""
    print("📊 Adding ESPN FPI features...")
    
    # Mock FPI data - will be replaced with real ESPN FPI scraping
    fpi_data = {
        'KC': {'fpi': 7.9, 'offense': 5.5, 'defense': 2.4, 'special_teams': 0.0},
        'DET': {'fpi': 6.2, 'offense': 4.1, 'defense': 2.1, 'special_teams': 0.0},
        'GB': {'fpi': 5.9, 'offense': 4.2, 'defense': 1.7, 'special_teams': 0.0},
        'LAR': {'fpi': 5.8, 'offense': 3.8, 'defense': 2.0, 'special_teams': 0.0},
        'SF': {'fpi': 5.5, 'offense': 3.5, 'defense': 2.0, 'special_teams': 0.0},
        'PHI': {'fpi': 5.2, 'offense': 3.8, 'defense': 1.4, 'special_teams': 0.0},
        'BUF': {'fpi': 4.8, 'offense': 3.2, 'defense': 1.6, 'special_teams': 0.0},
        'DAL': {'fpi': 4.5, 'offense': 3.1, 'defense': 1.4, 'special_teams': 0.0},
        'BAL': {'fpi': 4.2, 'offense': 2.8, 'defense': 1.4, 'special_teams': 0.0},
        'MIA': {'fpi': 3.9, 'offense': 3.5, 'defense': 0.4, 'special_teams': 0.0},
        'PIT': {'fpi': 3.6, 'offense': 2.1, 'defense': 1.5, 'special_teams': 0.0},
        'NE': {'fpi': 3.3, 'offense': 2.0, 'defense': 1.3, 'special_teams': 0.0},
        'DEN': {'fpi': 3.0, 'offense': 2.2, 'defense': 0.8, 'special_teams': 0.0},
        'NYJ': {'fpi': 2.7, 'offense': 1.8, 'defense': 0.9, 'special_teams': 0.0},
        'CLE': {'fpi': 2.4, 'offense': 1.5, 'defense': 0.9, 'special_teams': 0.0},
        'TB': {'fpi': 2.1, 'offense': 1.8, 'defense': 0.3, 'special_teams': 0.0},
        'ATL': {'fpi': 1.8, 'offense': 1.5, 'defense': 0.3, 'special_teams': 0.0},
        'IND': {'fpi': 1.5, 'offense': 1.2, 'defense': 0.3, 'special_teams': 0.0},
        'NO': {'fpi': 1.2, 'offense': 0.9, 'defense': 0.3, 'special_teams': 0.0},
        'CIN': {'fpi': 0.9, 'offense': 0.6, 'defense': 0.3, 'special_teams': 0.0},
        'MIN': {'fpi': 0.6, 'offense': 0.3, 'defense': 0.3, 'special_teams': 0.0},
        'CAR': {'fpi': 0.3, 'offense': 0.0, 'defense': 0.3, 'special_teams': 0.0},
        'HOU': {'fpi': 0.0, 'offense': 0.0, 'defense': 0.0, 'special_teams': 0.0},
        'NYG': {'fpi': -0.3, 'offense': -0.3, 'defense': 0.0, 'special_teams': 0.0},
        'WAS': {'fpi': -0.6, 'offense': -0.6, 'defense': 0.0, 'special_teams': 0.0},
        'LV': {'fpi': -0.9, 'offense': -0.9, 'defense': 0.0, 'special_teams': 0.0},
        'JAX': {'fpi': -1.2, 'offense': -1.2, 'defense': 0.0, 'special_teams': 0.0},
        'TEN': {'fpi': -1.5, 'offense': -1.5, 'defense': 0.0, 'special_teams': 0.0},
        'ARI': {'fpi': -1.8, 'offense': -1.8, 'defense': 0.0, 'special_teams': 0.0},
        'LAC': {'fpi': -2.1, 'offense': -2.1, 'defense': 0.0, 'special_teams': 0.0},
        'SEA': {'fpi': -2.4, 'offense': -2.4, 'defense': 0.0, 'special_teams': 0.0},
        'CHI': {'fpi': -2.7, 'offense': -2.7, 'defense': 0.0, 'special_teams': 0.0}
    }
    
    # Add FPI features
    for idx, row in df.iterrows():
        away_team = row['away_team']
        home_team = row['home_team']
        
        if away_team in fpi_data and home_team in fpi_data:
            away_fpi = fpi_data[away_team]
            home_fpi = fpi_data[home_team]
            
            df.at[idx, 'away_fpi'] = away_fpi['fpi']
            df.at[idx, 'home_fpi'] = home_fpi['fpi']
            df.at[idx, 'fpi_differential'] = home_fpi['fpi'] - away_fpi['fpi']
            
            df.at[idx, 'away_offense_fpi'] = away_fpi['offense']
            df.at[idx, 'home_offense_fpi'] = home_fpi['offense']
            df.at[idx, 'away_defense_fpi'] = away_fpi['defense']
            df.at[idx, 'home_defense_fpi'] = home_fpi['defense']
            
            # Matchup advantages
            df.at[idx, 'home_off_vs_away_def'] = home_fpi['offense'] - away_fpi['defense']
            df.at[idx, 'away_off_vs_home_def'] = away_fpi['offense'] - home_fpi['defense']
        else:
            # Default values for teams not in FPI data
            df.at[idx, 'away_fpi'] = 0
            df.at[idx, 'home_fpi'] = 0
            df.at[idx, 'fpi_differential'] = 0
            df.at[idx, 'away_offense_fpi'] = 0
            df.at[idx, 'home_offense_fpi'] = 0
            df.at[idx, 'away_defense_fpi'] = 0
            df.at[idx, 'home_defense_fpi'] = 0
            df.at[idx, 'home_off_vs_away_def'] = 0
            df.at[idx, 'away_off_vs_home_def'] = 0
    
    return df

def prepare_features(df):
    """Prepare features for the model"""
    print("🔧 Preparing features...")
    
    # Select features for the model
    feature_columns = [
        'away_games_played', 'home_games_played',
        'away_win_pct', 'home_win_pct',
        'away_avg_points_for', 'home_avg_points_for',
        'away_avg_points_against', 'home_avg_points_against',
        'away_recent_form', 'home_recent_form',
        'away_fpi', 'home_fpi', 'fpi_differential',
        'away_offense_fpi', 'home_offense_fpi',
        'away_defense_fpi', 'home_defense_fpi',
        'home_off_vs_away_def', 'away_off_vs_home_def'
    ]
    
    # Add additional features
    df['home_field_advantage'] = 2.5  # Standard home field advantage
    df['rest_differential'] = pd.to_numeric(df['home_rest'], errors='coerce') - pd.to_numeric(df['away_rest'], errors='coerce')
    df['rest_differential'] = df['rest_differential'].fillna(0)
    
    feature_columns.extend(['home_field_advantage', 'rest_differential'])
    
    # Create feature matrix
    X = df[feature_columns].copy()
    
    # Handle missing values
    X = X.fillna(0)
    
    # Create target variable (1 = home team wins, 0 = away team wins)
    # Only use completed games
    completed_games = df.dropna(subset=['away_score', 'home_score'])
    y = []
    valid_indices = []
    
    for idx in completed_games.index:
        try:
            away_score = float(completed_games.loc[idx, 'away_score'])
            home_score = float(completed_games.loc[idx, 'home_score'])
        except (ValueError, TypeError):
            continue
        
        if home_score > away_score:
            y.append(1)  # Home team wins
        else:
            y.append(0)  # Away team wins
        
        valid_indices.append(idx)
    
    X_clean = X.loc[valid_indices].copy()
    y = np.array(y)
    
    return X_clean, y, feature_columns

def train_winner_model(X, y, feature_columns):
    """Train multiple models and select the best one"""
    print("🤖 Training winner prediction models...")
    
    # Split data for validation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
        'XGBoost': xgb.XGBClassifier(n_estimators=100, random_state=42),
        'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000)
    }
    
    best_model = None
    best_score = 0
    best_name = ""
    
    print("\n📊 Model Performance:")
    print("-" * 50)
    
    for name, model in models.items():
        if name == 'Logistic Regression':
            model.fit(X_train_scaled, y_train)
            train_pred = model.predict(X_train_scaled)
            test_pred = model.predict(X_test_scaled)
        else:
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
    
    print("-" * 50)
    print(f"🏆 Best Model: {best_name} (Test Accuracy: {best_score:.3f})")
    
    # Feature importance
    if hasattr(best_model, 'feature_importances_'):
        feature_importance = pd.DataFrame({
            'feature': feature_columns,
            'importance': best_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n🔍 Top 10 Most Important Features:")
        for _, row in feature_importance.head(10).iterrows():
            print(f"  {row['feature']:25s}: {row['importance']:.3f}")
    
    return best_model, scaler, feature_columns, best_score

def evaluate_model(model, X, y, feature_columns, scaler=None):
    """Evaluate model performance"""
    print("\n📊 Model Evaluation:")
    print("=" * 60)
    
    # Cross-validation
    if scaler:
        X_scaled = scaler.transform(X)
        cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='accuracy')
    else:
        cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
    
    print(f"Cross-Validation Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
    
    # Overall accuracy
    if scaler:
        X_scaled = scaler.transform(X)
        predictions = model.predict(X_scaled)
    else:
        predictions = model.predict(X)
    
    accuracy = accuracy_score(y, predictions)
    print(f"Overall Accuracy: {accuracy:.3f}")
    
    return accuracy

def main():
    print("🏈 WINNER PREDICTION MODEL")
    print("=" * 60)
    print("🎯 Target: 60%+ accuracy on historical data")
    print("🎯 Target: 60%+ accuracy on current season")
    print("=" * 60)
    
    # Load data
    print("📊 Loading data from Google Sheets...")
    df = load_sheet_data(SPREADSHEET_ID, 'upcoming_games')
    
    if df.empty:
        print("❌ No data loaded!")
        return
    
    print(f"✅ Loaded {len(df)} games")
    
    # Filter for completed games only (non-empty scores)
    completed_df = df[
        (df['away_score'].notna()) & (df['home_score'].notna()) &
        (df['away_score'] != '') & (df['home_score'] != '')
    ].copy()
    print(f"✅ Found {len(completed_df)} completed games")
    
    if len(completed_df) < 100:
        print("❌ Not enough completed games for training!")
        return
    
    # Create features
    df_with_features = create_team_features(completed_df)
    df_with_features = add_espn_fpi_features(df_with_features)
    
    # Prepare features
    X, y, feature_columns = prepare_features(df_with_features)
    
    print(f"✅ Prepared {len(X)} samples with {len(feature_columns)} features")
    
    # Train model
    model, scaler, feature_columns, best_score = train_winner_model(X, y, feature_columns)
    
    # Evaluate model
    accuracy = evaluate_model(model, X, y, feature_columns, scaler)
    
    print(f"\n🎯 RESULTS:")
    print(f"   Historical Accuracy: {accuracy:.1%}")
    
    if accuracy >= 0.60:
        print("   ✅ TARGET ACHIEVED! (60%+ accuracy)")
    else:
        print("   ❌ TARGET NOT MET - Need to improve model")
        print("   🔄 Will iterate and improve...")
    
    return model, scaler, feature_columns, accuracy

if __name__ == "__main__":
    model, scaler, feature_columns, accuracy = main()
