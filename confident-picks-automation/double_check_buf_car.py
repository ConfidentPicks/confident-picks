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

def double_check_buf_car():
    """Double check BUF @ CAR prediction"""
    print("=" * 70)
    print("DOUBLE CHECKING BUF @ CAR PREDICTION")
    print("=" * 70)
    
    service = get_sheets_service()
    
    # Get row 113 specifically (BUF @ CAR)
    range_name = "upcoming_games!AV113:AX113"  # Winner prediction and confidence
    
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = result.get('values', [])
    
    if not values:
        print("No data found!")
        return
    
    print("Row 113 (BUF @ CAR) prediction data:")
    print("-" * 70)
    
    row = values[0]
    predicted_winner = row[0] if len(row) > 0 else "N/A"  # AV column
    winner_confidence = row[2] if len(row) > 2 else "N/A"  # AX column
    
    print(f"Predicted Winner (AV): '{predicted_winner}'")
    print(f"Winner Confidence (AX): '{winner_confidence}'")
    
    # Also check the team columns
    range_name2 = "upcoming_games!I113:J113"  # Away and Home teams
    
    result2 = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name2).execute()
    values2 = result2.get('values', [])
    
    if values2:
        row2 = values2[0]
        away_team = row2[0] if len(row2) > 0 else "N/A"  # I column
        home_team = row2[1] if len(row2) > 1 else "N/A"  # J column
        
        print(f"Away Team (I): '{away_team}'")
        print(f"Home Team (J): '{home_team}'")
        print(f"Game: {away_team} @ {home_team}")
        
        if predicted_winner == "BUF":
            print("\n*** MODEL PREDICTS BUF TO WIN ***")
            print("BUF Performance: 80% moneyline accuracy")
            print("Recommendation: BUF Moneyline - High confidence pick!")
        elif predicted_winner == "CAR":
            print("\n*** MODEL PREDICTS CAR TO WIN ***")
            print("CAR Performance: 85.71% moneyline accuracy")
            print("Recommendation: CAR Moneyline - High confidence pick!")
        else:
            print(f"\n*** MODEL PREDICTS {predicted_winner} TO WIN ***")
            print("This team is not in high performers (70%+ threshold)")

if __name__ == "__main__":
    double_check_buf_car()

