import pandas as pd
import numpy as np
from google.oauth2 import service_account
from googleapiclient.discovery import build
import re

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'
SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU'

def get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

def col_to_a1(col_idx):
    """Convert 0-indexed column number to A1-style column letter"""
    letter = ''
    while col_idx >= 0:
        letter = chr(col_idx % 26 + ord('A')) + letter
        col_idx = col_idx // 26 - 1
    return letter

def load_sheet_data(spreadsheet_id, sheet_name, range_name=None):
    """Load data from Google Sheets"""
    service = get_sheets_service()
    
    if range_name is None:
        range_name = f"'{sheet_name}'!A:CZ"
    else:
        range_name = f"'{sheet_name}'!{range_name}"
    
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])

    if not values:
        return pd.DataFrame()

    headers = values[0]
    data = values[1:]

    max_cols = len(headers)
    for row in data:
        if len(row) > max_cols:
            max_cols = len(row)
    
    headers_extended = headers + [f'col_{i}' for i in range(len(headers), max_cols)]
    
    data_aligned = []
    for row in data:
        aligned_row = row + [None] * (max_cols - len(row))
        data_aligned.append(aligned_row)

    df = pd.DataFrame(data_aligned, columns=headers_extended)
    return df

def load_fpi_data():
    """Load ESPN FPI data from BY:CI columns, rows 5-113"""
    print("📊 Loading ESPN FPI data from BY5:CI113...")
    
    service = get_sheets_service()
    
    try:
        # Load FPI data range
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='upcoming_games!BY5:CI113'
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print("❌ No FPI data found in range BY5:CI113")
            return None
        
        print(f"✅ Loaded FPI data: {len(values)} rows")
        
        # Check if first row is headers
        print(f"\n📋 FPI Table Structure:")
        if values:
            print(f"   Headers (Row 5): {values[0]}")
            print(f"   Sample data (Row 6): {values[1] if len(values) > 1 else 'N/A'}")
        
        # Convert to DataFrame
        headers = values[0] if values else []
        data = values[1:] if len(values) > 1 else []
        
        # Align data
        max_cols = len(headers)
        for row in data:
            if len(row) > max_cols:
                max_cols = len(row)
        
        headers_extended = headers + [f'fpi_col_{i}' for i in range(len(headers), max_cols)]
        
        data_aligned = []
        for row in data:
            aligned_row = row + [None] * (max_cols - len(row))
            data_aligned.append(aligned_row)
        
        fpi_df = pd.DataFrame(data_aligned, columns=headers_extended)
        
        print(f"✅ FPI DataFrame created: {len(fpi_df)} games, {len(fpi_df.columns)} columns")
        print(f"   Columns: {list(fpi_df.columns)}")
        
        return fpi_df
        
    except Exception as e:
        print(f"❌ Error loading FPI data: {e}")
        return None

def parse_percentage(value):
    """Parse percentage string to float"""
    if pd.isna(value) or value == '':
        return None
    
    value_str = str(value).strip()
    value_str = value_str.replace('%', '')
    
    try:
        float_val = float(value_str)
        if float_val > 1:
            return float_val / 100
        else:
            return float_val
    except:
        return None

def extract_fpi_prediction(fpi_row, away_team, home_team):
    """Extract FPI prediction from FPI data row"""
    # FPI data might have columns like:
    # - Team names
    # - Win probabilities
    # - Projected scores
    # - Favorite/underdog
    
    # Try to find which team FPI favors
    fpi_favorite = None
    fpi_confidence = None
    
    # Check all columns in FPI row for team names and probabilities
    for col_name, value in fpi_row.items():
        if pd.isna(value) or value == '':
            continue
        
        value_str = str(value).lower()
        
        # Look for team names
        if away_team and away_team.lower() in value_str:
            # Check if this column has a probability
            prob = parse_percentage(value)
            if prob and prob > 0.5:
                fpi_favorite = away_team
                fpi_confidence = prob
        
        if home_team and home_team.lower() in value_str:
            prob = parse_percentage(value)
            if prob and prob > 0.5:
                fpi_favorite = home_team
                fpi_confidence = prob
        
        # Look for probability values (might be in separate columns)
        if '%' in str(value) or (isinstance(value, (int, float)) and 0 < float(value) <= 100):
            prob = parse_percentage(value)
            if prob and prob > 0.5:
                # Try to determine which team this probability is for
                # This might require looking at adjacent columns
                pass
    
    return fpi_favorite, fpi_confidence

def adjust_confidence_with_fpi(df, fpi_df):
    """Adjust confidence scores based on FPI agreement"""
    print("\n🔧 Adjusting confidence scores with ESPN FPI comparison...")
    
    adjusted_confidences = []
    agreements = 0
    disagreements = 0
    no_fpi_data = 0
    
    # FPI data is for rows 5-113, which corresponds to games in the main sheet
    # Rows 5-113 in the sheet = rows 4-112 in 0-indexed DataFrame (subtract 1 for header)
    fpi_start_row = 4  # Row 5 in sheet = index 4 in DataFrame
    fpi_end_row = 112   # Row 113 in sheet = index 112 in DataFrame
    
    for idx, row in df.iterrows():
        # Get our prediction
        predicted_winner = row.get('predicted_winner', '')
        base_confidence_str = row.get('winner_confidence', '0.5')
        base_confidence = parse_percentage(base_confidence_str)
        if base_confidence is None:
            base_confidence = 0.5
        
        # Get teams
        away_team = row.get('away_team', '')
        home_team = row.get('home_team', '')
        
        # Check if this row has corresponding FPI data
        # FPI data starts at row 5 (index 4) and goes to row 113 (index 112)
        # Main data starts at row 2 (index 0)
        # So FPI row = main row + 4
        fpi_row_idx = idx - fpi_start_row
        
        if fpi_row_idx >= 0 and fpi_row_idx < len(fpi_df):
            # Get FPI data for this game
            fpi_row = fpi_df.iloc[fpi_row_idx]
            
            # Extract FPI prediction
            fpi_favorite, fpi_prob = extract_fpi_prediction(fpi_row, away_team, home_team)
            
            if fpi_favorite and fpi_prob:
                # Compare predictions
                if predicted_winner == fpi_favorite:
                    # Agreement - boost confidence
                    boost = 0.03 + (fpi_prob - 0.5) * 0.10
                    adjusted_confidence = min(base_confidence + boost, 0.99)
                    agreements += 1
                else:
                    # Disagreement - lower confidence
                    penalty = 0.05 + (fpi_prob - 0.5) * 0.15
                    adjusted_confidence = max(base_confidence - penalty, 0.51)
                    disagreements += 1
            else:
                # No valid FPI prediction found
                adjusted_confidence = base_confidence
                no_fpi_data += 1
        else:
            # No FPI data for this row
            adjusted_confidence = base_confidence
            no_fpi_data += 1
        
        adjusted_confidences.append(round(adjusted_confidence, 3))
    
    print(f"✅ Processed {len(df)} games:")
    print(f"   - Agreements with FPI: {agreements}")
    print(f"   - Disagreements with FPI: {disagreements}")
    print(f"   - No FPI data: {no_fpi_data}")
    
    return adjusted_confidences

def update_sheet(adjusted_confidences, ba_col_idx):
    """Update Google Sheet with adjusted confidence scores"""
    print("\n📤 Updating Google Sheet with FPI-adjusted confidence...")
    
    service = get_sheets_service()
    
    # Prepare values for Column BA
    ba_values = [[f"{conf:.1%}"] for conf in adjusted_confidences]
    
    # Update Column BA
    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': [{
            'range': f'upcoming_games!{col_to_a1(ba_col_idx)}2:{col_to_a1(ba_col_idx)}{len(adjusted_confidences) + 1}',
            'values': ba_values
        }]
    }
    
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=body).execute()
    
    print(f"✅ Updated {len(adjusted_confidences)} FPI-adjusted confidence scores in Column BA")

def main():
    print("🏈 ESPN FPI CONFIDENCE ADJUSTMENT")
    print("=" * 60)
    print("📊 Comparing our predictions with ESPN FPI (BY5:CI113)")
    print("📊 Adjusting confidence scores based on agreement")
    print("=" * 60)
    
    # Load upcoming_games data
    print("\n📊 Loading upcoming_games data...")
    df = load_sheet_data(SPREADSHEET_ID, 'upcoming_games')
    
    if df.empty:
        print("❌ No data available!")
        return False
    
    print(f"✅ Loaded {len(df)} games")
    
    # Load ESPN FPI data
    fpi_df = load_fpi_data()
    
    if fpi_df is None or fpi_df.empty:
        print("\n⚠️  No FPI data available - keeping original confidence scores")
        # Just copy original confidence to BA
        adjusted_confidences = []
        for idx, row in df.iterrows():
            base_confidence_str = row.get('winner_confidence', '0.5')
            base_confidence = parse_percentage(base_confidence_str)
            if base_confidence is None:
                base_confidence = 0.5
            adjusted_confidences.append(round(base_confidence, 3))
    else:
        # Adjust confidence with FPI
        adjusted_confidences = adjust_confidence_with_fpi(df, fpi_df)
    
    # Find Column BA (index 52)
    ba_col_idx = 52
    
    # Update sheet
    update_sheet(adjusted_confidences, ba_col_idx)
    
    print("\n✅ FPI-ADJUSTED CONFIDENCE SCORES POPULATED!")
    print(f"   - Column BA (winner_confidence_fpi): {len(adjusted_confidences)} scores")
    
    # Show sample results
    print("\n📊 Sample FPI-adjusted confidence scores:")
    for i in range(min(10, len(adjusted_confidences))):
        orig_conf_str = df.iloc[i].get('winner_confidence', '0.5')
        orig_conf = parse_percentage(orig_conf_str)
        if orig_conf is None:
            orig_conf = 0.5
        
        adj_conf = adjusted_confidences[i]
        change = adj_conf - orig_conf
        
        direction = "↑" if change > 0.001 else "↓" if change < -0.001 else "→"
        predicted_winner = df.iloc[i].get('predicted_winner', '')
        print(f"   Game {i+1} ({predicted_winner}): {orig_conf:.1%} → {adj_conf:.1%} {direction} ({change:+.1%})")
    
    return True

if __name__ == "__main__":
    success = main()


