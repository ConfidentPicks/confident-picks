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

def clear_home_score_confidence():
    """Clear the BJ column (home_score_confidence) since we don't have a model for it yet"""
    print("=" * 70)
    print("CLEARING HOME SCORE CONFIDENCE COLUMN")
    print("=" * 70)
    
    service = get_sheets_service()
    
    # Column BJ (62): "home_score_confidence" - Should be empty until we have a home score prediction model
    bj_col = 62  # home_score_confidence
    
    # Prepare empty values - limit to 272 rows (rows 2-273)
    empty_values = [[''] for _ in range(272)]
    
    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': [
            {'range': f'upcoming_games!{col_to_a1(bj_col)}2:{col_to_a1(bj_col)}273', 'values': empty_values}
        ]
    }
    
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=body).execute()
    
    print(f"Cleared BJ column (home_score_confidence) for 272 rows")
    print("This column should remain empty until we create a home score prediction model")

def col_to_a1(col_num):
    """Convert column number to A1 notation"""
    result = ""
    while col_num > 0:
        col_num -= 1
        result = chr(col_num % 26 + ord('A')) + result
        col_num //= 26
    return result

if __name__ == "__main__":
    clear_home_score_confidence()

