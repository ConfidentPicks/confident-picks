#!/usr/bin/env python3
"""Debug NHL team name matching"""

import firebase_admin
from firebase_admin import credentials, firestore
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Firebase
CREDS_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'

if not firebase_admin._apps:
    cred = credentials.Certificate(CREDS_FILE)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Get NHL models
docs = db.collection('approved_models').where(filter=firestore.FieldFilter('status', '==', 'approved')).stream()

nhl_teams_in_models = set()
for doc in docs:
    data = doc.to_dict()
    if data.get('sport', '').upper() == 'NHL':
        team = data.get('team', '').upper()
        nhl_teams_in_models.add(team)

print("NHL TEAMS IN MODELS:")
for team in sorted(nhl_teams_in_models):
    print(f"  {team}")

# Get teams from sheet
SERVICE_ACCOUNT_FILE = CREDS_FILE
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
NHL_SHEET_ID = '1Hel-NsCxmk07nM0AH4VkJFB9hSK23X7XOxtA4wyRNRo'

def get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build('sheets', 'v4', credentials=creds)

service = get_sheets_service()
result = service.spreadsheets().values().get(
    spreadsheetId=NHL_SHEET_ID,
    range='Upcoming_Games!A:I'
).execute()

values = result.get('values', [])
if len(values) > 1:
    print("\nTEAMS IN UPCOMING_GAMES SHEET:")
    teams_in_sheet = set()
    for row in values[1:]:
        if len(row) > 4:
            away = row[3].upper()
            home = row[4].upper()
            teams_in_sheet.add(away)
            teams_in_sheet.add(home)
            print(f"  {away} @ {home}")
    
    print("\nTEAMS IN SHEET (UNIQUE):")
    for team in sorted(teams_in_sheet):
        print(f"  {team}")
    
    print("\nMATCHING ANALYSIS:")
    print(f"Teams in models: {len(nhl_teams_in_models)}")
    print(f"Teams in sheet: {len(teams_in_sheet)}")
    print(f"Teams in both: {len(nhl_teams_in_models & teams_in_sheet)}")
    
    if nhl_teams_in_models & teams_in_sheet:
        print("\nMatching teams:")
        for team in sorted(nhl_teams_in_models & teams_in_sheet):
            print(f"  {team}")
    
    print("\nTeams in sheet but NOT in models:")
    for team in sorted(teams_in_sheet - nhl_teams_in_models):
        print(f"  {team}")

