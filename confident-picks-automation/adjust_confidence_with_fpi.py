import pandas as pd
import numpy as np
from google.oauth2 import service_account
from googleapiclient.discovery import build

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

def load_sheet_data(spreadsheet_id, sheet_name):
    """Load data from Google Sheets"""
    service = get_sheets_service()
    range_name = f"'{sheet_name}'!A:ZZ"
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

def determine_fpi_favorite(row):
    """Determine which team ESPN FPI favors"""
    # Try to extract FPI data from the row
    # FPI typically shows game projection with probabilities
    
    # Look for FPI-related columns
    fpi_cols = [col for col in row.index if 'fpi' in str(col).lower() or 'espn' in str(col).lower()]
    
    if not fpi_cols:
        return None, None
    
    # Try to parse FPI data
    # ESPN FPI format is typically: "Team A XX% vs Team B YY%"
    # or separate columns for home/away win probability
    
    away_team = row.get('away_team', '')
    home_team = row.get('home_team', '')
    
    # Look for FPI win probability columns
    home_win_prob = None
    away_win_prob = None
    
    # Check common FPI column names
    for col in fpi_cols:
        col_value = str(row.get(col, '')).lower()
        
        # Try to extract probabilities
        if 'home' in col.lower() and '%' in str(row.get(col, '')):
            try:
                prob_str = str(row.get(col, '')).replace('%', '').strip()
                home_win_prob = float(prob_str) / 100
            except:
                pass
        
        if 'away' in col.lower() and '%' in str(row.get(col, '')):
            try:
                prob_str = str(row.get(col, '')).replace('%', '').strip()
                away_win_prob = float(prob_str) / 100
            except:
                pass
    
    # If we found probabilities, determine favorite
    if home_win_prob is not None and away_win_prob is not None:
        if home_win_prob > away_win_prob:
            return home_team, home_win_prob
        else:
            return away_team, away_win_prob
    
    # Fallback: look for any numeric FPI values
    # Higher FPI = stronger team
    for col in fpi_cols:
        try:
            fpi_value = float(row.get(col, 0))
            # If FPI is positive, likely home team favored
            # If negative, away team favored
            if fpi_value > 0:
                return home_team, min(0.5 + abs(fpi_value) / 100, 0.95)
            elif fpi_value < 0:
                return away_team, min(0.5 + abs(fpi_value) / 100, 0.95)
        except:
            continue
    
    return None, None

def adjust_confidence_with_fpi(df):
    """Adjust confidence scores based on FPI agreement"""
    print("🔧 Adjusting confidence scores with ESPN FPI data...")
    
    adjusted_confidences = []
    agreements = 0
    disagreements = 0
    no_fpi_data = 0
    
    for idx, row in df.iterrows():
        # Get our prediction
        predicted_winner = row.get('predicted_winner', '')
        base_confidence = row.get('winner_confidence', 0.5)
        
        # Convert base_confidence to float
        try:
            base_confidence = float(base_confidence)
        except:
            base_confidence = 0.5
        
        # Get FPI favorite
        fpi_favorite, fpi_prob = determine_fpi_favorite(row)
        
        # Adjust confidence based on FPI agreement
        if fpi_favorite is None or pd.isna(fpi_favorite) or fpi_favorite == '':
            # No FPI data - keep original confidence
            adjusted_confidence = base_confidence
            no_fpi_data += 1
        elif predicted_winner == fpi_favorite:
            # Agreement - boost confidence
            # Weighted average: 70% our model, 30% FPI agreement boost
            boost = 0.05 + (fpi_prob - 0.5) * 0.1  # Up to 10% boost for high FPI confidence
            adjusted_confidence = min(base_confidence + boost, 0.99)
            agreements += 1
        else:
            # Disagreement - lower confidence
            # Reduce confidence based on how confident FPI is
            penalty = 0.05 + (fpi_prob - 0.5) * 0.15  # Up to 15% penalty for high FPI disagreement
            adjusted_confidence = max(base_confidence - penalty, 0.51)
            disagreements += 1
        
        adjusted_confidences.append(round(adjusted_confidence, 3))
    
    print(f"✅ Processed {len(df)} games:")
    print(f"   - Agreements with FPI: {agreements}")
    print(f"   - Disagreements with FPI: {disagreements}")
    print(f"   - No FPI data: {no_fpi_data}")
    
    return adjusted_confidences

def update_sheet(adjusted_confidences, ba_col_idx):
    """Update Google Sheet with adjusted confidence scores"""
    print("📤 Updating Google Sheet with FPI-adjusted confidence...")
    
    service = get_sheets_service()
    
    # Prepare values for Column BA
    ba_values = [[conf] for conf in adjusted_confidences]
    
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
    print("📊 Comparing our predictions with ESPN FPI")
    print("📊 Adjusting confidence scores based on agreement")
    print("=" * 60)
    
    # Load upcoming_games data
    print("📊 Loading upcoming_games data...")
    df = load_sheet_data(SPREADSHEET_ID, 'upcoming_games')
    
    if df.empty:
        print("❌ No data available!")
        return False
    
    print(f"✅ Loaded {len(df)} games")
    
    # Show available columns
    print(f"\n📋 Available columns:")
    for i, col in enumerate(df.columns[:60]):  # Show first 60 columns
        print(f"   {col_to_a1(i)}: {col}")
    
    # Check if we have FPI data
    fpi_cols = [col for col in df.columns if 'fpi' in str(col).lower() or 'espn' in str(col).lower()]
    print(f"\n🔍 Found {len(fpi_cols)} FPI-related columns:")
    for col in fpi_cols:
        print(f"   - {col}")
    
    # Adjust confidence with FPI
    adjusted_confidences = adjust_confidence_with_fpi(df)
    
    # Find Column BA (index 52)
    ba_col_idx = 52  # BA is the 53rd column (0-indexed = 52)
    
    # Update sheet
    update_sheet(adjusted_confidences, ba_col_idx)
    
    print("\n✅ FPI-ADJUSTED CONFIDENCE SCORES SUCCESSFULLY POPULATED!")
    print(f"   - Column BA (winner_confidence_fpi): {len(adjusted_confidences)} scores")
    
    # Show sample results
    print("\n📊 Sample FPI-adjusted confidence scores:")
    for i in range(min(10, len(adjusted_confidences))):
        orig_conf = df.iloc[i].get('winner_confidence', 0.5)
        try:
            orig_conf = float(orig_conf)
        except:
            orig_conf = 0.5
        
        adj_conf = adjusted_confidences[i]
        change = adj_conf - orig_conf
        
        direction = "↑" if change > 0 else "↓" if change < 0 else "→"
        print(f"   Game {i+1}: {orig_conf:.1%} → {adj_conf:.1%} {direction} ({change:+.1%})")
    
    return True

if __name__ == "__main__":
    success = main()


