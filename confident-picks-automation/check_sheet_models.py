from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
CREDS_PATH = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'
NHL_SHEET_ID = '1Okiwl_1iwvGHJReUSp-2FncQaQQL-sbWylJPcbTcrHs'

creds = Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

print("\n" + "="*80)
print("NHL TEAM MODEL SCORING (from Google Sheet)")
print("="*80)

result = sheet.values().get(
    spreadsheetId=NHL_SHEET_ID,
    range='nhl_team_model_scoring!A1:H100'
).execute()

values = result.get('values', [])

if len(values) > 1:
    print(f"\nHeaders: {values[0]}\n")
    
    count_70_plus = 0
    teams_70_plus = []
    
    for row in values[1:]:
        if len(row) >= 7:
            team = row[0] if len(row) > 0 else ''
            prop = row[1] if len(row) > 1 else ''
            model = row[2] if len(row) > 2 else ''
            hist_acc = row[5] if len(row) > 5 else '0'
            curr_acc = row[6] if len(row) > 6 else '0'
            
            try:
                curr_pct = float(str(curr_acc).replace('%','')) if curr_acc else 0
                if curr_pct >= 70:
                    count_70_plus += 1
                    teams_70_plus.append({
                        'team': team,
                        'prop': prop,
                        'model': model,
                        'hist': hist_acc,
                        'curr': curr_acc
                    })
            except:
                pass
    
    print(f"Teams/Props at 70%+ Current Season Accuracy:\n")
    for item in teams_70_plus:
        print(f"  {item['team']:6} | {item['prop']:15} | {item['model']:20} | Hist: {item['hist']:>6} | Curr: {item['curr']:>6}")
    
    print("\n" + "="*80)
    print(f"TOTAL AT 70%+: {count_70_plus}")
    print("="*80)
else:
    print("No data found in sheet")

print()


