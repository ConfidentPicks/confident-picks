#!/usr/bin/env python3
"""Generate picks using approved models from Firebase"""

import firebase_admin
from firebase_admin import credentials, firestore
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime
import numpy as np

# Firebase setup
CREDS_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'

if not firebase_admin._apps:
    cred = credentials.Certificate(CREDS_FILE)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Google Sheets setup
SERVICE_ACCOUNT_FILE = CREDS_FILE
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
NFL_SHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU'
NHL_SHEET_ID = '1Hel-NsCxmk07nM0AH4VkJFB9hSK23X7XOxtA4wyRNRo'

def get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build('sheets', 'v4', credentials=creds)

def get_approved_models():
    """Fetch all approved models from Firebase"""
    print("\nFetching approved models from Firebase...")
    
    models = {}
    docs = db.collection('approved_models').where(filter=firestore.FieldFilter('status', '==', 'approved')).stream()
    
    for doc in docs:
        data = doc.to_dict()
        sport = data.get('sport', '').upper()
        team = data.get('team', '').upper()
        prop = data.get('prop', '').lower()
        
        key = f"{sport}_{team}_{prop}"
        models[key] = {
            'model_name': data.get('modelName', data.get('model_name')),
            'historical_accuracy': data.get('historicalAccuracy', data.get('historical_accuracy', 0)),
            'current_accuracy': data.get('currentAccuracy', data.get('current_accuracy', 0)),
            'config': data.get('config', {})
        }
    
    print(f"Found {len(models)} approved models")
    return models

def get_upcoming_nfl_games():
    """Fetch upcoming NFL games from Google Sheets"""
    print("\nFetching upcoming NFL games...")
    
    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=NFL_SHEET_ID,
        range='upcoming_games!A:Z'
    ).execute()
    
    values = result.get('values', [])
    if not values:
        return pd.DataFrame()
    
    df = pd.DataFrame(values[1:], columns=values[0])
    
    # Filter for truly upcoming games (no scores yet)
    df_upcoming = df[(df['away_score'] == '') | (df['away_score'].isna()) | 
                     (df['home_score'] == '') | (df['home_score'].isna())]
    
    print(f"Found {len(df_upcoming)} upcoming NFL games (out of {len(df)} total)")
    return df_upcoming

def get_upcoming_nhl_games():
    """Fetch upcoming NHL games from Google Sheets"""
    print("\nFetching upcoming NHL games...")
    
    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=NHL_SHEET_ID,
        range='Upcoming_Games!A:I'
    ).execute()
    
    values = result.get('values', [])
    if not values or len(values) <= 1:
        return pd.DataFrame()
    
    df = pd.DataFrame(values[1:], columns=values[0])
    print(f"Found {len(df)} upcoming NHL games")
    return df

def generate_pick(game, models, sport):
    """Generate a pick for a game if we have an approved model"""
    away_team = game.get('away_team', '').upper()
    home_team = game.get('home_team', '').upper()
    
    picks = []
    
    # Check for moneyline models (try both lowercase and capitalized)
    away_ml_key = f"{sport}_{away_team}_moneyline"
    home_ml_key = f"{sport}_{home_team}_moneyline"
    away_ml_key_cap = f"{sport}_{away_team}_Moneyline"
    home_ml_key_cap = f"{sport}_{home_team}_Moneyline"
    
    # Try lowercase first, then capitalized
    if away_ml_key in models or away_ml_key_cap in models:
        model = models.get(away_ml_key, models.get(away_ml_key_cap))
        confidence = model['current_accuracy'] / 100.0
        
        if confidence >= 0.70:  # Only generate picks with 70%+ confidence
            pick = {
                'sport': sport,
                'league': sport,
                'awayTeam': away_team,
                'homeTeam': home_team,
                'game': f"{away_team} @ {home_team}",
                'pick': away_team,
                'pickDescription': f"{away_team} to win",
                'pickTeam': away_team,
                'marketType': 'moneyline',
                'confidence': confidence,
                'modelConfidence': confidence,
                'odds': float(game.get('away_moneyline', -110)),
                'oddsAmerican': int(game.get('away_moneyline', -110)),
                'reasoning': f"Model prediction with {confidence*100:.1f}% confidence (based on {model['model_name']})",
                'gameDate': game.get('gameday', game.get('game_date', '')),
                'gameTime': game.get('gametime', game.get('game_time', '')),
                'commenceTime': game.get('gameday', game.get('game_date', '')),
                'tier': 'public',
                'riskTag': 'safe',
                'source': f'{sport.lower()}-approved-model',
                'createdAt': datetime.now().isoformat(),
                'updatedAt': datetime.now().isoformat(),
                'timestamp': firestore.SERVER_TIMESTAMP,
                'status': 'active'
            }
            picks.append(pick)
    
    if home_ml_key in models or home_ml_key_cap in models:
        model = models.get(home_ml_key, models.get(home_ml_key_cap))
        confidence = model['current_accuracy'] / 100.0
        
        if confidence >= 0.70:
            pick = {
                'sport': sport,
                'league': sport,
                'awayTeam': away_team,
                'homeTeam': home_team,
                'game': f"{away_team} @ {home_team}",
                'pick': home_team,
                'pickDescription': f"{home_team} to win",
                'pickTeam': home_team,
                'marketType': 'moneyline',
                'confidence': confidence,
                'modelConfidence': confidence,
                'odds': float(game.get('home_moneyline', -110)),
                'oddsAmerican': int(game.get('home_moneyline', -110)),
                'reasoning': f"Model prediction with {confidence*100:.1f}% confidence (based on {model['model_name']})",
                'gameDate': game.get('gameday', game.get('game_date', '')),
                'gameTime': game.get('gametime', game.get('game_time', '')),
                'commenceTime': game.get('gameday', game.get('game_date', '')),
                'tier': 'public',
                'riskTag': 'safe',
                'source': f'{sport.lower()}-approved-model',
                'createdAt': datetime.now().isoformat(),
                'updatedAt': datetime.now().isoformat(),
                'timestamp': firestore.SERVER_TIMESTAMP,
                'status': 'active'
            }
            picks.append(pick)
    
    return picks

def save_picks_to_firebase(picks, collection='all_picks'):
    """Save generated picks to Firebase"""
    print(f"\nSaving {len(picks)} picks to Firebase ({collection})...")
    
    saved = 0
    for pick in picks:
        try:
            doc_id = f"{pick['sport']}_{pick['awayTeam']}_{pick['homeTeam']}_{pick['pick']}"
            db.collection(collection).document(doc_id).set(pick)
            print(f"  Saved: {pick['game']} - {pick['pick']} ({pick['confidence']*100:.1f}%)")
            saved += 1
        except Exception as e:
            print(f"  Error saving pick: {e}")
    
    print(f"\nSaved {saved}/{len(picks)} picks to {collection}")
    return saved

def main():
    print("\n" + "="*80)
    print("GENERATING PICKS FROM APPROVED MODELS")
    print("="*80)
    
    # Get approved models
    models = get_approved_models()
    
    if not models:
        print("\nNo approved models found!")
        return
    
    all_picks = []
    
    # Generate NFL picks
    try:
        nfl_games = get_upcoming_nfl_games()
        if not nfl_games.empty:
            for _, game in nfl_games.iterrows():
                picks = generate_pick(game, models, 'NFL')
                all_picks.extend(picks)
    except Exception as e:
        print(f"\nError fetching NFL games: {e}")
        print("Skipping NFL picks...")
    
    # Generate NHL picks
    try:
        nhl_games = get_upcoming_nhl_games()
        if not nhl_games.empty:
            for _, game in nhl_games.iterrows():
                picks = generate_pick(game, models, 'NHL')
                all_picks.extend(picks)
    except Exception as e:
        print(f"\nError fetching NHL games: {e}")
        print("Skipping NHL picks...")
    
    print(f"\nGenerated {len(all_picks)} total picks")
    
    if all_picks:
        # Save to Firebase
        save_picks_to_firebase(all_picks, 'all_picks')
        
        print("\n" + "="*80)
        print("PICK GENERATION COMPLETE!")
        print("="*80)
        print(f"\nGenerated {len(all_picks)} picks from approved models")
        print("Check your app to see the new picks!")
    else:
        print("\nNo picks generated. Make sure:")
        print("  1. You have upcoming games in your sheets")
        print("  2. You have approved models for those teams")
        print("  3. Models have 70%+ confidence")

if __name__ == '__main__':
    main()
