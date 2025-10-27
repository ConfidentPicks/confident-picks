from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'
SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU'

def get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

def col_to_a1(col_idx):
    letter = ''
    while col_idx >= 0:
        letter = chr(col_idx % 26 + ord('A')) + letter
        col_idx = col_idx // 26 - 1
    return letter

service = get_sheets_service()
result = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range='upcoming_games!A1:CZ1'
).execute()

headers = result.get('values', [[]])[0]

print("🔍 CHECKING SPREAD-RELATED COLUMNS:")
print("=" * 60)

target_cols = ['Predicted_Cover_Home', 'Home_Cover_Confidence', 
               'Predicted_Cover_Away', 'Away_Cover_Confidence',
               'home_cover_ confidence', 'away_cover_confidence']

for i, header in enumerate(headers):
    if any(target.lower() in str(header).lower() for target in target_cols):
        print(f"{col_to_a1(i)} ({i}): {header}")

print("\n📋 User's editable columns (from previous info):")
print("   BA - Predicted_Cover_Home")
print("   BC - home_cover_ confidence") 
print("   BD - Predicted_Cover_Away")
print("   BF - away_cover_confidence")


