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

def verify_with_correct_mapping():
    """Verify accuracy using the correct column mapping from our earlier findings"""
    print("=" * 70)
    print("VERIFYING WITH CORRECT COLUMN MAPPING")
    print("=" * 70)
    
    service = get_sheets_service()
    
    # Based on our earlier findings:
    # AA (Column 27): spread_line
    # AY (Column 51): predicted_home_cover  
    # AZ (Column 52): Actual_Cover_Home
    # I (Column 9): away_score
    # K (Column 11): home_score
    
    # Get the data using the correct column indices
    range_name = "upcoming_games!I2:K110"  # away_score, home_score
    
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = result.get('values', [])
    
    if not values:
        print("No data found!")
        return
    
    print("First 10 rows of scores:")
    print("-" * 70)
    
    for i, row in enumerate(values[:10]):
        if len(row) >= 2:
            away_score = row[0] if len(row) > 0 else "N/A"
            home_score = row[1] if len(row) > 1 else "N/A"
            print(f"Row {i+2}: Away={away_score}, Home={home_score}")
    
    # Now get predictions and actuals
    range_name2 = "upcoming_games!AY2:AZ110"  # predicted_home_cover, Actual_Cover_Home
    
    result2 = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name2).execute()
    values2 = result2.get('values', [])
    
    print("\nFirst 10 rows of predictions and actuals:")
    print("-" * 70)
    
    for i, row in enumerate(values2[:10]):
        if len(row) >= 2:
            predicted = row[0] if len(row) > 0 else "N/A"
            actual = row[1] if len(row) > 1 else "N/A"
            print(f"Row {i+2}: Predicted={predicted}, Actual={actual}")
    
    # Calculate accuracy
    correct = 0
    total = 0
    
    print("\nCalculating accuracy:")
    print("-" * 70)
    
    for i, row in enumerate(values2):
        if len(row) >= 2:
            predicted = row[0]
            actual = row[1]
            
            if predicted in ["YES", "NO"] and actual in ["YES", "NO"]:
                is_correct = predicted == actual
                if is_correct:
                    correct += 1
                total += 1
                print(f"Row {i+2}: Predicted={predicted}, Actual={actual}, {'CORRECT' if is_correct else 'WRONG'}")
    
    if total > 0:
        accuracy = correct / total
        print(f"\n" + "=" * 70)
        print(f"ACCURACY RESULTS:")
        print(f"Total games: {total}")
        print(f"Correct predictions: {correct}")
        print(f"Wrong predictions: {total - correct}")
        print(f"Accuracy: {accuracy:.3f} ({accuracy:.1%})")
        
        if accuracy >= 0.60:
            print("\nSUCCESS: Home spread accuracy is 60%+ as required!")
        else:
            print("\nFAILURE: Home spread accuracy is below 60%")
    else:
        print("No valid predictions found!")

if __name__ == "__main__":
    verify_with_correct_mapping()

