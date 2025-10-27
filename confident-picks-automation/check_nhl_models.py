import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize Firebase
cred_path = os.path.join(os.path.dirname(__file__), 'confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json')
try:
    firebase_admin.get_app()
except:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("\n" + "=" * 80)
print("NHL APPROVED MODELS - CURRENT STATUS")
print("=" * 80)

# Get all NHL approved models
models = db.collection('approved_models').where('league', '==', 'NHL').stream()

teams_dict = {}
for doc in models:
    data = doc.to_dict()
    team = data.get('team', 'N/A')
    prop = data.get('prop', 'N/A')
    model_name = data.get('modelName', 'N/A')
    hist_acc = data.get('historicalAccuracy', 0)
    curr_acc = data.get('currentAccuracy', 0)
    
    if team not in teams_dict:
        teams_dict[team] = []
    teams_dict[team].append({
        'prop': prop,
        'model': model_name,
        'historical': hist_acc,
        'current': curr_acc
    })

if not teams_dict:
    print("\n❌ No approved models found in Firebase!")
    print("\nThis means the NHL exhaustive testing hasn't saved any models yet.")
    print("The terminal output shows it found 8 teams with 70%+ accuracy,")
    print("but they may not have been saved to Firebase.")
else:
    print(f"\n✅ Found {len(teams_dict)} teams with approved models:\n")
    
    for idx, (team, models) in enumerate(sorted(teams_dict.items()), 1):
        print(f"{idx}. {team}")
        for model in models:
            print(f"   • {model['prop']}: {model['model']}")
            print(f"     Historical: {model['historical']:.1f}% | Current: {model['current']:.1f}%")
        print()

print("=" * 80)
print(f"SUMMARY: {len(teams_dict)} teams ready (Target: 15+ teams)")
print("=" * 80)

# Also check the dashboard HTML file
print("\n📊 Checking dashboard for model testing progress...")
dashboard_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'model-dashboard.html')
if os.path.exists(dashboard_path):
    print(f"✅ Dashboard exists at: {dashboard_path}")
    print("   Open this file in a browser to see real-time model testing progress")
else:
    print("❌ Dashboard not found")

print()


