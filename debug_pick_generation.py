#!/usr/bin/env python3
"""Debug why no picks are being generated"""

import firebase_admin
from firebase_admin import credentials, firestore
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

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

def get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build('sheets', 'v4', credentials=creds)

# Get models
docs = db.collection('approved_models').where(filter=firestore.FieldFilter('status', '==', 'approved')).stream()

nfl_models = {}
for doc in docs:
    data = doc.to_dict()
    sport = data.get('sport', '').upper()
    if sport == 'NFL':
        team = data.get('team', '').upper()
        prop = data.get('prop', '')
        key = f"{sport}_{team}_{prop}"
        nfl_models[key] = {
            'accuracy': data.get('current_accuracy', 0),
            'prop': prop
        }

print("NFL MODELS:")
for key, model in sorted(nfl_models.items())[:10]:
    print(f"  {key}: {model['accuracy']}%")

# Get upcoming games
service = get_sheets_service()
result = service.spreadsheets().values().get(
    spreadsheetId=NFL_SHEET_ID,
    range='upcoming_games!A:Z'
).execute()

values = result.get('values', [])
df = pd.DataFrame(values[1:], columns=values[0])
df_upcoming = df[(df['away_score'] == '') | (df['away_score'].isna()) | 
                 (df['home_score'] == '') | (df['home_score'].isna())]

print(f"\nUPCOMING GAMES: {len(df_upcoming)}")
for _, game in df_upcoming.head(5).iterrows():
    away = game['away_team'].upper()
    home = game['home_team'].upper()
    print(f"  {away} @ {home}")
    
    # Check if we have models for these teams
    away_ml = f"NFL_{away}_Moneyline"
    home_ml = f"NFL_{home}_Moneyline"
    away_total = f"NFL_{away}_Total"
    home_total = f"NFL_{home}_Total"
    
    if away_ml in nfl_models:
        print(f"    Found {away} Moneyline model: {nfl_models[away_ml]['accuracy']}%")
    if home_ml in nfl_models:
        print(f"    Found {home} Moneyline model: {nfl_models[home_ml]['accuracy']}%")
    if away_total in nfl_models:
        print(f"    Found {away} Total model: {nfl_models[away_total]['accuracy']}%")
    if home_total in nfl_models:
        print(f"    Found {home} Total model: {nfl_models[home_total]['accuracy']}%")

