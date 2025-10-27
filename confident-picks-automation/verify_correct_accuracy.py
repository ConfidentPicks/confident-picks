#!/usr/bin/env python3

import pandas as pd
import numpy as np
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import warnings
warnings.filterwarnings('ignore')

# Configuration
SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU'
SERVICE_ACCOUNT_FILE = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_sheets_service():
    """Get Google Sheets service"""
    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('sheets', 'v4', credentials=credentials)

def verify_home_spread_accuracy_correctly():
    """Verify home spread accuracy using the correct columns"""
    print("=" * 70)
    print("VERIFYING HOME SPREAD ACCURACY - CORRECT COLUMNS")
    print("=" * 70)
    
    service = get_sheets_service()
    
    # Get the correct columns: AA (spread_line), AY (predicted_home_cover), AZ (Actual_Cover_Home)
    range_name = "upcoming_games!AA2:AZ110"  # spread_line, predicted_home_cover, Actual_Cover_Home
    
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = result.get('values', [])
    
    if not values:
        print("No data found!")
        return
    
    print(f"Loaded {len(values)} rows of data")
    
    correct = 0
    total = 0
    wrong_predictions = []
    
    print("\nDetailed analysis of each game:")
    print("-" * 70)
    
    for i, row in enumerate(values):
        if len(row) >= 3:
            try:
                spread_line = float(row[0])  # AA column (spread_line)
                predicted = row[1]  # AY column (predicted_home_cover)
                actual = row[2]  # AZ column (Actual_Cover_Home)
                
                if predicted in ["YES", "NO"] and actual in ["YES", "NO"]:
                    is_correct = predicted == actual
                    if is_correct:
                        correct += 1
                    else:
                        wrong_predictions.append({
                            'row': i+2,
                            'spread': spread_line,
                            'predicted': predicted,
                            'actual': actual
                        })
                    total += 1
                    
                    print(f"Row {i+2}: Spread={spread_line}, Predicted={predicted}, Actual={actual}, {'CORRECT' if is_correct else 'WRONG'}")
                    
            except (ValueError, TypeError) as e:
                print(f"Row {i+2}: Error processing - {e}")
                continue
    
    if total > 0:
        accuracy = correct / total
        print(f"\n" + "=" * 70)
        print(f"VERIFICATION RESULTS:")
        print(f"Total games: {total}")
        print(f"Correct predictions: {correct}")
        print(f"Wrong predictions: {total - correct}")
        print(f"Accuracy: {accuracy:.3f} ({accuracy:.1%})")
        
        if len(wrong_predictions) > 0:
            print(f"\nWrong predictions:")
            for wp in wrong_predictions:
                print(f"  Row {wp['row']}: Spread={wp['spread']}, Predicted={wp['predicted']}, Actual={wp['actual']}")
        
        if accuracy >= 0.60:
            print("\nSUCCESS: Home spread accuracy is 60%+ as required!")
        else:
            print("\nFAILURE: Home spread accuracy is below 60%")
            
        # Check if this seems realistic
        if accuracy > 0.90:
            print("\nWARNING: Accuracy > 90% seems suspiciously high!")
            print("This might indicate data leakage or other issues.")
        elif accuracy < 0.50:
            print("\nWARNING: Accuracy < 50% is worse than random!")
    else:
        print("No valid predictions found!")

if __name__ == "__main__":
    verify_home_spread_accuracy_correctly()

