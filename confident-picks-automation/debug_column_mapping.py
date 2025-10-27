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

def check_column_mapping():
    """Check the actual column mapping for home spread predictions"""
    print("=" * 70)
    print("CHECKING COLUMN MAPPING FOR HOME SPREAD")
    print("=" * 70)
    
    service = get_sheets_service()
    
    # Get the specific columns we're interested in
    range_name = "upcoming_games!A1:BM5"  # First 5 rows, columns A to BM
    
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = result.get('values', [])
    
    if not values:
        print("No data found!")
        return
    
    headers = values[0]
    
    print("Column Headers (A to BM):")
    print("-" * 50)
    
    for i, header in enumerate(headers):
        col_letter = chr(65 + i) if i < 26 else chr(65 + i // 26 - 1) + chr(65 + i % 26)
        print(f"{col_letter}: {header}")
    
    # Check specific columns that should contain home spread data
    print("\n" + "=" * 70)
    print("CHECKING HOME SPREAD COLUMNS")
    print("=" * 70)
    
    # Column YA (51) should be predicted_home_cover
    ya_index = 51
    if ya_index < len(headers):
        print(f"Column YA (51): '{headers[ya_index]}'")
        if len(values) > 1:
            print(f"Sample values: {values[1][ya_index:ya_index+5] if ya_index < len(values[1]) else 'N/A'}")
    
    # Column AB (53) should be Home_Cover_Confidence
    ab_index = 53
    if ab_index < len(headers):
        print(f"Column AB (53): '{headers[ab_index]}'")
        if len(values) > 1:
            print(f"Sample values: {values[1][ab_index:ab_index+5] if ab_index < len(values[1]) else 'N/A'}")

def check_actual_vs_predicted():
    """Check the actual vs predicted columns"""
    print("\n" + "=" * 70)
    print("CHECKING ACTUAL VS PREDICTED COLUMNS")
    print("=" * 70)
    
    service = get_sheets_service()
    
    # Get a larger range to see more data
    range_name = "upcoming_games!A1:BM20"  # First 20 rows
    
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = result.get('values', [])
    
    if not values:
        print("No data found!")
        return
    
    headers = values[0]
    
    # Find the columns we need
    predicted_home_cover_col = None
    actual_home_cover_col = None
    
    for i, header in enumerate(headers):
        if 'predicted_home_cover' in str(header).lower():
            predicted_home_cover_col = i
        if 'actual_cover_home' in str(header).lower():
            actual_home_cover_col = i
    
    print(f"Predicted Home Cover Column: {predicted_home_cover_col}")
    print(f"Actual Home Cover Column: {actual_home_cover_col}")
    
    if predicted_home_cover_col is not None and actual_home_cover_col is not None:
        print(f"\nColumn {predicted_home_cover_col} header: '{headers[predicted_home_cover_col]}'")
        print(f"Column {actual_home_cover_col} header: '{headers[actual_home_cover_col]}'")
        
        print("\nFirst 10 rows of data:")
        print("-" * 50)
        for i in range(1, min(11, len(values))):
            pred_val = values[i][predicted_home_cover_col] if predicted_home_cover_col < len(values[i]) else "N/A"
            actual_val = values[i][actual_home_cover_col] if actual_home_cover_col < len(values[i]) else "N/A"
            print(f"Row {i+1}: Predicted={pred_val}, Actual={actual_val}")

def check_formula_accuracy():
    """Check what the accuracy formulas are actually calculating"""
    print("\n" + "=" * 70)
    print("CHECKING ACCURACY FORMULAS")
    print("=" * 70)
    
    service = get_sheets_service()
    
    # Check if there are any accuracy calculation cells
    range_name = "upcoming_games!A1:BM300"  # Large range to find formulas
    
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = result.get('values', [])
    
    if not values:
        print("No data found!")
        return
    
    # Look for cells that might contain accuracy formulas
    print("Looking for accuracy-related cells...")
    
    for i, row in enumerate(values):
        for j, cell in enumerate(row):
            if isinstance(cell, str) and ('accuracy' in cell.lower() or '%' in cell or 'countif' in cell.lower()):
                col_letter = chr(65 + j) if j < 26 else chr(65 + j // 26 - 1) + chr(65 + j % 26)
                print(f"Row {i+1}, Column {col_letter}: {cell}")

if __name__ == "__main__":
    check_column_mapping()
    check_actual_vs_predicted()
    check_formula_accuracy()

