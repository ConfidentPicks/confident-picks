#!/usr/bin/env python3

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
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

def check_actual_home_spread_accuracy():
    """Check the actual home spread accuracy using the correct columns"""
    print("=" * 70)
    print("CHECKING ACTUAL HOME SPREAD ACCURACY - CORRECT COLUMNS")
    print("=" * 70)
    
    service = get_sheets_service()
    
    # Get the specific columns we need
    range_name = "upcoming_games!AY2:BA110"  # predicted_home_cover, Actual_Cover_Home, Home_Cover_Confidence
    
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = result.get('values', [])
    
    if not values:
        print("No data found!")
        return
    
    print(f"Loaded {len(values)} rows of data")
    
    # Check first few rows
    print("\nFirst 10 rows:")
    print("-" * 50)
    for i, row in enumerate(values[:10]):
        predicted = row[0] if len(row) > 0 else "N/A"
        actual = row[1] if len(row) > 1 else "N/A"
        confidence = row[2] if len(row) > 2 else "N/A"
        print(f"Row {i+2}: Predicted={predicted}, Actual={actual}, Confidence={confidence}")
    
    # Calculate accuracy
    correct = 0
    total = 0
    
    for i, row in enumerate(values):
        if len(row) >= 2:
            predicted = row[0]
            actual = row[1]
            
            if predicted in ["YES", "NO"] and actual in ["YES", "NO"]:
                if predicted == actual:
                    correct += 1
                total += 1
    
    if total > 0:
        accuracy = correct / total
        print(f"\nACTUAL HOME SPREAD ACCURACY: {accuracy:.3f} ({correct}/{total})")
        
        if accuracy >= 0.60:
            print("SUCCESS: Home spread accuracy is 60%+ as required!")
        else:
            print("FAILURE: Home spread accuracy is below 60%")
    else:
        print("No valid predictions found!")

def check_what_columns_im_writing_to():
    """Check what columns my model is actually writing to"""
    print("\n" + "=" * 70)
    print("CHECKING WHAT COLUMNS MY MODEL IS WRITING TO")
    print("=" * 70)
    
    service = get_sheets_service()
    
    # Check columns YA (51) and AB (53) - what my model thinks it's writing to
    range_name = "upcoming_games!YA2:AB10"  # Columns 51 and 53
    
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = result.get('values', [])
    
    if not values:
        print("No data found!")
        return
    
    print("Columns YA (51) and AB (53) - what my model thinks it's writing to:")
    print("-" * 50)
    for i, row in enumerate(values[:10]):
        col_ya = row[0] if len(row) > 0 else "N/A"
        col_ab = row[1] if len(row) > 1 else "N/A"
        print(f"Row {i+2}: YA={col_ya}, AB={col_ab}")
    
    # Check columns AY (50) and AZ (51) - the actual prediction columns
    range_name2 = "upcoming_games!AY2:AZ10"  # Columns 50 and 51
    
    result2 = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name2).execute()
    values2 = result2.get('values', [])
    
    print("\nColumns AY (50) and AZ (51) - the actual prediction columns:")
    print("-" * 50)
    for i, row in enumerate(values2[:10]):
        col_ay = row[0] if len(row) > 0 else "N/A"
        col_az = row[1] if len(row) > 1 else "N/A"
        print(f"Row {i+2}: AY={col_ay}, AZ={col_az}")

if __name__ == "__main__":
    check_actual_home_spread_accuracy()
    check_what_columns_im_writing_to()

