#!/usr/bin/env python3
"""Check for games without scores (truly upcoming)"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

SERVICE_ACCOUNT_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
NFL_SHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU'

def get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build('sheets', 'v4', credentials=creds)

service = get_sheets_service()
result = service.spreadsheets().values().get(
    spreadsheetId=NFL_SHEET_ID,
    range='upcoming_games!A:Z'
).execute()

values = result.get('values', [])
df = pd.DataFrame(values[1:], columns=values[0])

print(f"Total games in sheet: {len(df)}")

# Check for games without scores
df['has_score'] = (df['away_score'].notna()) & (df['away_score'] != '') & (df['home_score'].notna()) & (df['home_score'] != '')
upcoming = df[~df['has_score']]

print(f"Games without scores: {len(upcoming)}")

if len(upcoming) > 0:
    print("\nFirst 5 upcoming games:")
    for _, game in upcoming.head().iterrows():
        print(f"  {game['away_team']} @ {game['home_team']} - {game['gameday']}")
else:
    print("\nNo upcoming games found (all have scores)")
    print("\nLast 5 games in sheet:")
    for _, game in df.tail().iterrows():
        print(f"  {game['away_team']} @ {game['home_team']} - {game['gameday']} - {game['away_score']}-{game['home_score']}")

