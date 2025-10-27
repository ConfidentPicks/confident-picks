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

def load_sheet_data(spreadsheet_id, sheet_name):
    """Load data from Google Sheets"""
    service = get_sheets_service()
    range_name = f"'{sheet_name}'!A:CZ"
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

def parse_percentage(value):
    """Parse percentage string to float"""
    if pd.isna(value) or value == '':
        return None
    
    # Convert to string
    value_str = str(value).strip()
    
    # Remove % sign
    value_str = value_str.replace('%', '')
    
    try:
        # Convert to float and divide by 100 if needed
        float_val = float(value_str)
        
        # If value is > 1, assume it's already a percentage
        if float_val > 1:
            return float_val / 100
        else:
            return float_val
    except:
        return None

def load_fpi_data():
    """Load ESPN FPI data from the sheet"""
    print("📊 Loading ESPN FPI data...")
    
    # Check for FPI data in the sheet
    # FPI tables are typically embedded in the sheet
    # Look for columns or ranges that contain FPI predictions
    
    service = get_sheets_service()
    
    # Try to load from a specific range where FPI data might be
    # This might be in a different tab or embedded in the main sheet
    
    try:
        # Try loading from the main sheet - look for FPI-like data
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='upcoming_games!A:CZ'
        ).execute()
        
        values = result.get('values', [])
        
        # Look for FPI-related headers
        if values:
            headers = values[0]
            
            # Look for columns that might contain FPI data
            fpi_indices = []
            for i, header in enumerate(headers):
                if header and any(keyword in str(header).lower() for keyword in ['fpi', 'espn', 'projection', 'win%', 'probability']):
                    fpi_indices.append((i, header))
            
            if fpi_indices:
                print(f"✅ Found {len(fpi_indices)} potential FPI columns:")
                for idx, header in fpi_indices:
                    print(f"   - Column {col_to_a1(idx)}: {header}")
                
                # Try to extract FPI predictions
                # This is a placeholder - actual implementation depends on FPI data format
                return None  # Will use embedded logic in main function
            else:
                print("❌ No FPI columns found in main sheet")
                return None
    except Exception as e:
        print(f"❌ Error loading FPI data: {e}")
        return None

def determine_fpi_favorite_from_espn_id(espn_id, away_team, home_team):
    """
    Determine FPI favorite based on ESPN game ID
    Since we don't have direct FPI data, we'll use a heuristic approach:
    - Check if there's embedded FPI data in the sheet
    - For now, return None to indicate no FPI data
    """
    # This would require scraping or API access to ESPN FPI
    # For now, we'll return None
    return None, None

def adjust_confidence_with_fpi(df):
    """Adjust confidence scores based on FPI agreement"""
    print("🔧 Adjusting confidence scores with ESPN FPI comparison...")
    
    adjusted_confidences = []
    agreements = 0
    disagreements = 0
    no_fpi_data = 0
    
    # Try to find FPI data in the sheet
    # Since ESPN FPI tables are embedded, we need to check if there are any additional sheets
    service = get_sheets_service()
    
    try:
        # Get all sheets in the spreadsheet
        spreadsheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = spreadsheet_metadata.get('sheets', [])
        
        print(f"\n📋 Available sheets in spreadsheet:")
        for sheet in sheets:
            sheet_name = sheet['properties']['title']
            print(f"   - {sheet_name}")
        
        # Check if there's an ESPN FPI sheet
        fpi_sheet_names = [sheet['properties']['title'] for sheet in sheets 
                          if any(keyword in sheet['properties']['title'].lower() 
                                for keyword in ['fpi', 'espn', 'projection'])]
        
        if fpi_sheet_names:
            print(f"\n✅ Found FPI-related sheets: {fpi_sheet_names}")
            # Load FPI data from these sheets
            # For now, we'll use a simple heuristic
        else:
            print("\n❌ No dedicated FPI sheets found")
            print("   Using embedded FPI data if available...")
    
    except Exception as e:
        print(f"❌ Error checking for FPI sheets: {e}")
    
    # Process each game
    for idx, row in df.iterrows():
        # Get our prediction
        predicted_winner = row.get('predicted_winner', '')
        base_confidence_str = row.get('winner_confidence', '0.5')
        
        # Parse base confidence
        base_confidence = parse_percentage(base_confidence_str)
        if base_confidence is None:
            base_confidence = 0.5
        
        # Get teams
        away_team = row.get('away_team', '')
        home_team = row.get('home_team', '')
        espn_id = row.get('espn', '')
        
        # Try to get FPI prediction
        # Since we don't have direct FPI data access yet, 
        # we'll use the current implementation as a placeholder
        
        # For now, we'll keep the base confidence
        # In a real implementation, we would:
        # 1. Look up ESPN FPI data for this game
        # 2. Compare with our prediction
        # 3. Adjust confidence accordingly
        
        adjusted_confidence = base_confidence
        no_fpi_data += 1
        
        adjusted_confidences.append(round(adjusted_confidence, 3))
    
    print(f"\n✅ Processed {len(df)} games:")
    print(f"   - Agreements with FPI: {agreements}")
    print(f"   - Disagreements with FPI: {disagreements}")
    print(f"   - No FPI data available: {no_fpi_data}")
    print(f"\n⚠️  NOTE: ESPN FPI data not directly accessible")
    print(f"   Keeping original confidence scores for now")
    print(f"   To enable FPI comparison:")
    print(f"   1. Add ESP FPI data to a dedicated sheet tab")
    print(f"   2. Or provide FPI API access")
    
    return adjusted_confidences

def update_sheet(adjusted_confidences, ba_col_idx):
    """Update Google Sheet with adjusted confidence scores"""
    print("\n📤 Updating Google Sheet with FPI-adjusted confidence...")
    
    service = get_sheets_service()
    
    # Prepare values for Column BA
    # Format as percentages
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
    print("📊 Comparing our predictions with ESPN FPI")
    print("📊 Adjusting confidence scores based on agreement")
    print("=" * 60)
    
    # Load upcoming_games data
    print("\n📊 Loading upcoming_games data...")
    df = load_sheet_data(SPREADSHEET_ID, 'upcoming_games')
    
    if df.empty:
        print("❌ No data available!")
        return False
    
    print(f"✅ Loaded {len(df)} games")
    
    # Load FPI data
    load_fpi_data()
    
    # Adjust confidence with FPI
    adjusted_confidences = adjust_confidence_with_fpi(df)
    
    # Find Column BA (index 52)
    ba_col_idx = 52  # BA is the 53rd column (0-indexed = 52)
    
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
        print(f"   Game {i+1}: {orig_conf:.1%} → {adj_conf:.1%} {direction}")
    
    return True

if __name__ == "__main__":
    success = main()


