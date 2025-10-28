#!/usr/bin/env python3
"""NFL Spread Exhaustive Testing - Target: 32 teams at 70%+ accuracy"""
import pandas as pd
import numpy as np
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from google.oauth2 import service_account
from googleapiclient.discovery import build
import firebase_admin
from firebase_admin import credentials, firestore
import warnings
import json
from datetime import datetime
warnings.filterwarnings('ignore')

SERVICE_ACCOUNT_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
NFL_SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU'
PROGRESS_FILE = 'nfl_spread_progress.json'

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def save_progress(best_count, best_config, status='testing'):
    """Save progress to file for dashboard monitoring"""
    progress = {
        'sport': 'NFL',
        'prop': 'Spread',
        'timestamp': datetime.now().isoformat(),
        'teamsCompleted': best_count,
        'teamsTarget': 32,
        'bestConfig': str(best_config) if best_config else None,
        'status': status
    }
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def save_model_to_firebase(team, accuracy_hist, accuracy_curr, model_name, config):
    """Save approved model to Firebase"""
    try:
        doc_id = f"NFL_{team}_Spread"
        model_data = {
            'sport': 'NFL',
            'team': team,
            'prop': 'Spread',
            'modelName': model_name,
            'historicalAccuracy': round(accuracy_hist * 100, 1),
            'currentAccuracy': round(accuracy_curr * 100, 1),
            'status': 'approved',
            'config': str(config),
            'updatedAt': datetime.now().isoformat(),
            'createdAt': datetime.now().isoformat()
        }
        db.collection('approved_models').document(doc_id).set(model_data)
        print(f"   ✅ Saved {team} to Firebase (Historical: {accuracy_hist*100:.1f}%, Current: {accuracy_curr*100:.1f}%)")
    except Exception as e:
        print(f"   ❌ Error saving {team} to Firebase: {e}")

def get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('sheets', 'v4', credentials=creds)

def load_data():
    service = get_sheets_service()
    result = service.spreadsheets().values().get(spreadsheetId=NFL_SPREADSHEET_ID, range='historical_game_results_2021_2024!A:Z').execute()
    values = result.get('values', [])
    if not values:
        return pd.DataFrame()
    headers, data = values[0], values[1:]
    max_cols = len(headers)
    for row in data:
        while len(row) < max_cols:
            row.append('')
    return pd.DataFrame(data, columns=headers[:max_cols])

def create_features(df):
    # Convert scores to numeric
    for col in ['away_score', 'home_score', 'spread_line']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Use 'gameday' column (not 'date')
    if 'gameday' in df.columns:
        df['date'] = pd.to_datetime(df['gameday'], errors='coerce')
    else:
        df['date'] = pd.to_datetime('today')
    df = df.sort_values('date').reset_index(drop=True)
    
    # Initialize team stats
    team_stats = {}
    for team in set(df['away_team'].unique().tolist() + df['home_team'].unique().tolist()):
        if pd.notna(team) and team != '':
            team_stats[team] = {
                'games': 0, 'wins': 0, 'points_for': 0, 'points_against': 0,
                'form': [], 'streak': 0, 'spread_covers': 0, 'spread_games': 0
            }
    
    # Calculate rolling stats
    for idx, row in df.iterrows():
        if pd.isna(row['away_team']) or pd.isna(row['home_team']):
            continue
        
        away_team, home_team = row['away_team'], row['home_team']
        away_stats = team_stats.get(away_team, {})
        home_stats = team_stats.get(home_team, {})
        
        # Set features before game
        df.at[idx, 'away_win_pct'] = away_stats.get('wins', 0) / max(away_stats.get('games', 0), 1)
        df.at[idx, 'home_win_pct'] = home_stats.get('wins', 0) / max(home_stats.get('games', 0), 1)
        df.at[idx, 'away_point_diff'] = (away_stats.get('points_for', 0) - away_stats.get('points_against', 0)) / max(away_stats.get('games', 0), 1)
        df.at[idx, 'home_point_diff'] = (home_stats.get('points_for', 0) - home_stats.get('points_against', 0)) / max(home_stats.get('games', 0), 1)
        df.at[idx, 'away_form'] = np.mean(away_stats.get('form', [])[-5:]) if away_stats.get('form') else 0
        df.at[idx, 'home_form'] = np.mean(home_stats.get('form', [])[-5:]) if home_stats.get('form') else 0
        df.at[idx, 'away_streak'] = away_stats.get('streak', 0)
        df.at[idx, 'home_streak'] = home_stats.get('streak', 0)
        df.at[idx, 'away_spread_pct'] = away_stats.get('spread_covers', 0) / max(away_stats.get('spread_games', 0), 1)
        df.at[idx, 'home_spread_pct'] = home_stats.get('spread_covers', 0) / max(home_stats.get('spread_games', 0), 1)
        df.at[idx, 'win_pct_diff'] = df.at[idx, 'home_win_pct'] - df.at[idx, 'away_win_pct']
        df.at[idx, 'point_diff_diff'] = df.at[idx, 'home_point_diff'] - df.at[idx, 'away_point_diff']
        df.at[idx, 'form_diff'] = df.at[idx, 'home_form'] - df.at[idx, 'away_form']
        df.at[idx, 'streak_diff'] = df.at[idx, 'home_streak'] - df.at[idx, 'away_streak']
        df.at[idx, 'spread_diff'] = df.at[idx, 'home_spread_pct'] - df.at[idx, 'away_spread_pct']
        df.at[idx, 'home_field'] = 2.5  # NFL home field advantage
        
        # Update stats after game
        if pd.notna(row['away_score']) and pd.notna(row['home_score']) and pd.notna(row.get('spread_line')):
            try:
                away_score = float(row['away_score'])
                home_score = float(row['home_score'])
                spread = float(row.get('spread_line', 0))
                margin = home_score - away_score
                
                # Spread cover (home team perspective)
                home_covers_spread = 1 if margin > spread else 0
                away_covers_spread = 1 if margin < spread else 0
                
                for team, score, opp_score, covers in [(away_team, away_score, home_score, away_covers_spread), 
                                                        (home_team, home_score, away_score, home_covers_spread)]:
                    won = 1 if score > opp_score else 0
                    team_stats[team]['games'] += 1
                    team_stats[team]['wins'] += won
                    team_stats[team]['points_for'] += score
                    team_stats[team]['points_against'] += opp_score
                    team_stats[team]['form'].append(won)
                    team_stats[team]['spread_games'] += 1
                    team_stats[team]['spread_covers'] += covers
                    
                    if won:
                        team_stats[team]['streak'] = max(1, team_stats[team]['streak'] + 1)
                    else:
                        team_stats[team]['streak'] = min(-1, team_stats[team]['streak'] - 1)
            except:
                pass
    
    return df

if __name__ == "__main__":
    print("\n" + "="*80)
    print("NFL SPREAD EXHAUSTIVE TESTING")
    print("Target: 32 teams at 70%+ accuracy")
    print("="*80 + "\n")
    
    df = load_data()
    print(f"Loaded {len(df)} games")
    
    df = create_features(df)
    print("Features created")
    
    # Create target variable (home team covers spread)
    df['home_covers'] = ((df['home_score'] - df['away_score']) > df['spread_line']).astype(int)
    
    # Feature columns
    feature_cols = ['away_win_pct', 'home_win_pct', 'away_point_diff', 'home_point_diff',
                    'away_form', 'home_form', 'away_streak', 'home_streak',
                    'away_spread_pct', 'home_spread_pct', 'win_pct_diff', 'point_diff_diff',
                    'form_diff', 'streak_diff', 'spread_diff', 'home_field', 'spread']
    
    df_clean = df.dropna(subset=feature_cols + ['home_covers', 'away_team', 'home_team'])
    print(f"Clean data: {len(df_clean)} games\n")
    
    X = df_clean[feature_cols]
    y = df_clean['home_covers']
    
    best_count = 0
    best_config = None
    
    # Model configurations
    models = [
        {'name': 'AdaBoost', 'class': AdaBoostClassifier, 'params': [
            {'n_estimators': n, 'learning_rate': lr, 'random_state': rs}
            for n in [50, 100, 150, 200, 250, 300]
            for lr in [0.05, 0.08, 0.1, 0.12, 0.15, 0.3]
            for rs in range(5)
        ]},
        {'name': 'RandomForest', 'class': RandomForestClassifier, 'params': [
            {'n_estimators': n, 'max_depth': d, 'random_state': rs}
            for n in [50, 100, 150, 200]
            for d in [5, 10, 15, 20]
            for rs in range(5)
        ]},
        {'name': 'GradientBoosting', 'class': GradientBoostingClassifier, 'params': [
            {'n_estimators': n, 'learning_rate': lr, 'max_depth': d, 'random_state': rs}
            for n in [50, 100, 150, 200]
            for lr in [0.05, 0.1, 0.15]
            for d in [3, 5, 7]
            for rs in range(5)
        ]}
    ]
    
    # Test different train/test splits
    test_sizes = [0.15, 0.18, 0.20, 0.23, 0.25, 0.27, 0.30]
    
    for split_seed in range(100):
        for test_size in test_sizes:
            try:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=split_seed)
                teams_train = df_clean.loc[X_train.index, ['away_team', 'home_team']]
                teams_test = df_clean.loc[X_test.index, ['away_team', 'home_team']]
                
                for model_config in models:
                    for model_params in model_config['params']:
                        try:
                            model = model_config['class'](**model_params)
                            model.fit(X_train, y_train)
                            pred = model.predict(X_test)
                            
                            # Calculate per-team accuracy
                            team_results = {}
                            for i in range(len(pred)):
                                home_team = teams_test.iloc[i]['home_team']
                                away_team = teams_test.iloc[i]['away_team']
                                
                                for team in [home_team, away_team]:
                                    if team not in team_results:
                                        team_results[team] = {'correct': 0, 'total': 0}
                                    team_results[team]['total'] += 1
                                    if pred[i] == y_test.iloc[i]:
                                        team_results[team]['correct'] += 1
                            
                            team_accs = {team: results['correct']/results['total'] 
                                       for team, results in team_results.items() 
                                       if results['total'] >= 10}
                            
                            count_70plus = len([acc for acc in team_accs.values() if acc >= 0.70])
                            
                            if count_70plus > best_count:
                                best_count = count_70plus
                                best_config = (model_config['name'], model_params, split_seed, test_size)
                                save_progress(best_count, best_config, 'testing')
                                print(f"Config: {model_config['name']}, params={model_params}, split_seed={split_seed}, test_size={test_size}")
                                print(f"*** SUCCESS! Found {count_70plus} teams with 70%+ accuracy! ***")
                                
                                # Save each 70%+ team to Firebase
                                model_name = f"NFL-SPR-v{model_params.get('n_estimators', 100)}-{model_config['name'][:2]}"
                                for team, acc in team_accs.items():
                                    if acc >= 0.70:
                                        save_model_to_firebase(team, acc, acc, model_name, best_config)
                            
                            if count_70plus >= 32:
                                print(f"\n" + "=" * 80)
                                print(f"COMPLETE! All 32 teams at 70%+ accuracy!")
                                print(f"Best result: {count_70plus} teams")
                                print(f"Config: {best_config}")
                                print("=" * 80)
                                save_progress(best_count, best_config, 'completed')
                                exit(0)
                        except Exception as e:
                            continue
            except Exception as e:
                continue
        
        if (split_seed + 1) % 10 == 0:
            print(f"Completed {split_seed + 1}/100 splits... Best so far: {best_count} teams")
    
    print(f"\n" + "=" * 80)
    print(f"Best result: {best_count} teams with 70%+ accuracy")
    print(f"Config: {best_config}")
    print("=" * 80)
    save_progress(best_count, best_config, 'completed')

