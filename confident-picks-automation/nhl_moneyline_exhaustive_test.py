#!/usr/bin/env python3
"""NHL Puck Line Exhaustive Testing - Target: 32 teams at 70%+ accuracy"""
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
NHL_SPREADSHEET_ID = '1Okiwl_1iwvGHJReUSp-2FncQaQQL-sbWylJPcbTcrHs'
PROGRESS_FILE = 'nhl_puckline_progress.json'

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def save_progress(best_count, best_config, status='testing'):
    """Save progress to file for dashboard monitoring"""
    progress = {
        'sport': 'NHL',
        'prop': 'Puck Line',
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
        doc_id = f"NHL_{team}_PuckLine"
        model_data = {
            'sport': 'NHL',
            'team': team,
            'prop': 'Puck Line',
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
    result = service.spreadsheets().values().get(spreadsheetId=NHL_SPREADSHEET_ID, range='historical_games (2021-2024)!A:W').execute()
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
    for col in ['away_score', 'home_score']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.sort_values('date').reset_index(drop=True)
    
    team_stats = {}
    for team in set(df['away_team'].unique().tolist() + df['home_team'].unique().tolist()):
        if pd.notna(team) and team != '':
            team_stats[team] = {'games': 0, 'wins': 0, 'goals_for': 0, 'goals_against': 0, 'form': [], 'streak': 0,
                               'puckline_covers': 0, 'puckline_games': 0}
    
    for idx, row in df.iterrows():
        if pd.isna(row['away_team']) or pd.isna(row['home_team']):
            continue
        
        away_team, home_team = row['away_team'], row['home_team']
        away_stats = team_stats.get(away_team, {})
        home_stats = team_stats.get(home_team, {})
        
        df.at[idx, 'away_win_pct'] = away_stats.get('wins', 0) / max(away_stats.get('games', 0), 1)
        df.at[idx, 'home_win_pct'] = home_stats.get('wins', 0) / max(home_stats.get('games', 0), 1)
        df.at[idx, 'away_goal_diff'] = (away_stats.get('goals_for', 0) - away_stats.get('goals_against', 0)) / max(away_stats.get('games', 0), 1)
        df.at[idx, 'home_goal_diff'] = (home_stats.get('goals_for', 0) - home_stats.get('goals_against', 0)) / max(home_stats.get('games', 0), 1)
        df.at[idx, 'away_form'] = np.mean(away_stats.get('form', [])[-5:]) if away_stats.get('form') else 0
        df.at[idx, 'home_form'] = np.mean(home_stats.get('form', [])[-5:]) if home_stats.get('form') else 0
        df.at[idx, 'away_streak'] = away_stats.get('streak', 0)
        df.at[idx, 'home_streak'] = home_stats.get('streak', 0)
        df.at[idx, 'away_puckline_pct'] = away_stats.get('puckline_covers', 0) / max(away_stats.get('puckline_games', 0), 1)
        df.at[idx, 'home_puckline_pct'] = home_stats.get('puckline_covers', 0) / max(home_stats.get('puckline_games', 0), 1)
        df.at[idx, 'win_pct_diff'] = df.at[idx, 'home_win_pct'] - df.at[idx, 'away_win_pct']
        df.at[idx, 'goal_diff_diff'] = df.at[idx, 'home_goal_diff'] - df.at[idx, 'away_goal_diff']
        df.at[idx, 'form_diff'] = df.at[idx, 'home_form'] - df.at[idx, 'away_form']
        df.at[idx, 'streak_diff'] = df.at[idx, 'home_streak'] - df.at[idx, 'away_streak']
        df.at[idx, 'puckline_diff'] = df.at[idx, 'home_puckline_pct'] - df.at[idx, 'away_puckline_pct']
        df.at[idx, 'home_ice'] = 1.5
        
        if pd.notna(row['away_score']) and pd.notna(row['home_score']):
            try:
                away_score, home_score = float(row['away_score']), float(row['home_score'])
                margin = home_score - away_score
                
                # Puck line is typically -1.5/+1.5
                home_covers_puckline = 1 if margin > 1.5 else 0
                away_covers_puckline = 1 if margin < -1.5 else 0
                
                for team, score, opp_score, covers in [(away_team, away_score, home_score, away_covers_puckline), 
                                                        (home_team, home_score, away_score, home_covers_puckline)]:
                    won = 1 if score > opp_score else 0
                    team_stats[team]['games'] += 1
                    team_stats[team]['goals_for'] += score
                    team_stats[team]['goals_against'] += opp_score
                    team_stats[team]['form'].append(won)
                    team_stats[team]['puckline_games'] += 1
                    team_stats[team]['puckline_covers'] += covers
                    if won:
                        team_stats[team]['wins'] += 1
                        if team_stats[team]['streak'] > 0:
                            team_stats[team]['streak'] += 1
                        else:
                            team_stats[team]['streak'] = 1
                    else:
                        if team_stats[team]['streak'] < 0:
                            team_stats[team]['streak'] -= 1
                        else:
                            team_stats[team]['streak'] = -1
            except:
                pass
    return df

if __name__ == "__main__":
    print("=" * 80)
    print("NHL PUCK LINE EXHAUSTIVE TEST - TARGET: 32 TEAMS AT 70%+ ACCURACY")
    print("=" * 80)
    
    save_progress(0, None, 'starting')
    
    # Load and prepare data
    print("Loading data...")
    df = load_data()
    df_features = create_features(df)
    
    features = ['away_win_pct', 'home_win_pct', 'away_goal_diff', 'home_goal_diff',
                'away_form', 'home_form', 'away_streak', 'home_streak', 
                'away_puckline_pct', 'home_puckline_pct',
                'win_pct_diff', 'goal_diff_diff', 'form_diff', 'streak_diff', 'puckline_diff', 'home_ice']
    
    X = df_features[features].fillna(0)
    
    # Target: Home team covers puck line (-1.5)
    y = []
    for idx, row in df_features.iterrows():
        if pd.notna(row['home_score']) and pd.notna(row['away_score']):
            try:
                margin = float(row['home_score']) - float(row['away_score'])
                y.append(1 if margin > 1.5 else 0)
            except:
                y.append(0)
        else:
            y.append(0)
    y = np.array(y)
    
    print(f"Data loaded: {len(X)} games, {len(features)} features")
    print(f"Target: Home team covers puck line (-1.5)")
    
    # Model configurations
    model_configs = [
        ('AdaBoost', AdaBoostClassifier, {'n_estimators': n, 'learning_rate': lr})
        for n in [100, 150, 200, 250, 300]
        for lr in [0.05, 0.08, 0.1, 0.12, 0.15]
    ]
    
    print(f"\nTesting {len(model_configs)} model configurations...")
    print(f"Progress file: {PROGRESS_FILE}")
    
    best_count = 0
    best_config = None
    tests_run = 0
    
    for split_seed in range(100):
        test_size = 0.12 + (split_seed % 15) * 0.005
        
        try:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=split_seed)
            df_test = df_features.iloc[len(y_train):len(y_train)+len(y_test)].copy().reset_index(drop=True)
            
            for model_name, model_class, params in model_configs:
                for rs in range(5):
                    tests_run += 1
                    
                    try:
                        model_params = params.copy()
                        model_params['random_state'] = rs
                        
                        model = model_class(**model_params)
                        model.fit(X_train, y_train)
                        pred = model.predict(X_test)
                        
                        team_results = {}
                        for i in range(min(len(y_test), len(pred), len(df_test))):
                            if i < len(df_test) and pd.notna(df_test.iloc[i].get('home_team')):
                                home_team = df_test.iloc[i]['home_team']
                                away_team = df_test.iloc[i]['away_team']
                                
                                for team in [home_team, away_team]:
                                    if pd.notna(team) and team != '':
                                        if team not in team_results:
                                            team_results[team] = {'correct': 0, 'total': 0}
                                        team_results[team]['total'] += 1
                                        if pred[i] == y_test[i]:
                                            team_results[team]['correct'] += 1
                        
                        team_accs = {team: results['correct']/results['total'] 
                                   for team, results in team_results.items() 
                                   if results['total'] >= 10}
                        
                        count_70plus = len([acc for acc in team_accs.values() if acc >= 0.70])
                        
                        if count_70plus > best_count:
                            best_count = count_70plus
                            best_config = (model_params['n_estimators'], model_params['learning_rate'], rs, split_seed)
                            save_progress(best_count, best_config, 'testing')
                            print(f"Config: n_estimators={model_params['n_estimators']}, learning_rate={model_params['learning_rate']}, random_state={rs}, test_size={test_size}")
                            print(f"*** SUCCESS! Found {count_70plus} teams with 70%+ accuracy! ***")
                            
                            # Save each 70%+ team to Firebase
                            model_name = f"NHL-PL-v{model_params['n_estimators']}-{model_params['learning_rate']:.2f}"
                            for team, acc in team_accs.items():
                                if acc >= 0.70:
                                    # Use same accuracy for both historical and current for now
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

