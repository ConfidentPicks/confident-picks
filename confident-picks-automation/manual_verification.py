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

def verify_home_spread_accuracy_manually():
    """Manually verify home spread accuracy with detailed analysis"""
    print("=" * 70)
    print("MANUAL VERIFICATION OF HOME SPREAD ACCURACY")
    print("=" * 70)
    
    service = get_sheets_service()
    
    # Get the specific columns we need: AY (predicted), AZ (actual), AA (spread_line)
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
                spread_line = float(row[0])  # AA column
                predicted = row[1]  # AY column
                actual = row[2]  # AZ column
                
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
        print(f"MANUAL VERIFICATION RESULTS:")
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
    else:
        print("No valid predictions found!")

def check_if_predictions_are_realistic():
    """Check if the predictions seem realistic"""
    print("\n" + "=" * 70)
    print("CHECKING IF PREDICTIONS ARE REALISTIC")
    print("=" * 70)
    
    service = get_sheets_service()
    
    # Get spread lines and predictions
    range_name = "upcoming_games!AA2:AY110"  # spread_line, predicted_home_cover
    
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = result.get('values', [])
    
    if not values:
        print("No data found!")
        return
    
    yes_predictions = 0
    no_predictions = 0
    
    for i, row in enumerate(values):
        if len(row) >= 2:
            try:
                spread_line = float(row[0])
                predicted = row[1]
                
                if predicted == "YES":
                    yes_predictions += 1
                elif predicted == "NO":
                    no_predictions += 1
                    
            except (ValueError, TypeError):
                continue
    
    total_predictions = yes_predictions + no_predictions
    if total_predictions > 0:
        yes_rate = yes_predictions / total_predictions
        print(f"YES predictions: {yes_predictions} ({yes_rate:.1%})")
        print(f"NO predictions: {no_predictions} ({1-yes_rate:.1%})")
        
        if yes_rate > 0.8 or yes_rate < 0.2:
            print("WARNING: Prediction distribution seems unrealistic!")
        else:
            print("Prediction distribution seems reasonable.")

if __name__ == "__main__":
    verify_home_spread_accuracy_manually()
    check_if_predictions_are_realistic()

