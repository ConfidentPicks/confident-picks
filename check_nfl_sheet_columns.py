#!/usr/bin/env python3
"""Check what columns exist in the NFL upcoming_games sheet"""

from google.oauth2 import service_account
from googleapiclient.discovery import build

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
    range='upcoming_games!A1:Z1'
).execute()

values = result.get('values', [])
if values:
    print("Columns in upcoming_games sheet:")
    for i, col in enumerate(values[0]):
        print(f"  Column {chr(65+i)}: {col}")
else:
    print("No columns found")

# Also check a sample row
result2 = service.spreadsheets().values().get(
    spreadsheetId=NFL_SHEET_ID,
    range='upcoming_games!A2:Z2'
).execute()

values2 = result2.get('values', [])
if values2:
    print("\nSample data (row 2):")
    for i, val in enumerate(values2[0]):
        print(f"  {values[0][i]}: {val}")

