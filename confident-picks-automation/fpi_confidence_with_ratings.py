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

def load_fpi_ratings():
    """Load ESPN FPI team ratings"""
    print("📊 Loading ESPN FPI team ratings...")
    
    service = get_sheets_service()
    
    try:
        # Load FPI Power Index table (rows 7-42)
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='upcoming_games!BY7:CI42'
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print("❌ No FPI ratings found")
            return {}
        
        print(f"✅ Loaded {len(values)} teams from FPI Power Index")
        
        # Parse FPI ratings
        # Format: [Team Name, W-L-T, FPI, RK, ...]
        fpi_ratings = {}
        
        for row in values:
            if len(row) >= 3:
                team_name = str(row[0]).strip()
                try:
                    fpi_score = float(row[2])  # FPI column
                    fpi_ratings[team_name] = fpi_score
                except:
                    continue
        
        print(f"✅ Parsed FPI ratings for {len(fpi_ratings)} teams")
        
        # Show sample
        print(f"\n📋 Sample FPI Ratings:")
        for i, (team, fpi) in enumerate(list(fpi_ratings.items())[:10]):
            print(f"   {team}: {fpi}")
        
        return fpi_ratings
        
    except Exception as e:
        print(f"❌ Error loading FPI ratings: {e}")
        return {}

def normalize_team_name(team_name):
    """Normalize team names for matching"""
    if not team_name:
        return ''
    
    # Convert to string and uppercase
    team = str(team_name).upper().strip()
    
    # Common variations
    replacements = {
        'KANSAS CITY CHIEFS': 'KC',
        'LOS ANGELES RAMS': 'LA',
        'LOS ANGELES CHARGERS': 'LAC',
        'NEW YORK JETS': 'NYJ',
        'NEW YORK GIANTS': 'NYG',
        'NEW ENGLAND PATRIOTS': 'NE',
        'SAN FRANCISCO 49ERS': 'SF',
        'TAMPA BAY BUCCANEERS': 'TB',
        'GREEN BAY PACKERS': 'GB',
        'LAS VEGAS RAIDERS': 'LV',
        'WASHINGTON COMMANDERS': 'WAS',
    }
    
    # Check if full name matches
    for full_name, abbrev in replacements.items():
        if full_name in team:
            return abbrev
    
    # Return as-is if no match
    return team

def match_team_to_fpi(team_abbrev, fpi_ratings):
    """Match team abbreviation to FPI rating"""
    if not team_abbrev or not fpi_ratings:
        return None
    
    team_upper = str(team_abbrev).upper().strip()
    
    # Try direct match first
    for fpi_team, rating in fpi_ratings.items():
        fpi_team_norm = normalize_team_name(fpi_team)
        
        if team_upper == fpi_team_norm or team_upper in fpi_team_norm or fpi_team_norm in team_upper:
            return rating
        
        # Check if abbreviation is in the full name
        if team_upper in fpi_team.upper():
            return rating
    
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

def adjust_confidence_with_fpi(df, fpi_ratings):
    """Adjust confidence scores based on FPI ratings"""
    print("\n🔧 Adjusting confidence scores with ESPN FPI ratings...")
    
    adjusted_confidences = []
    agreements = 0
    disagreements = 0
    no_fpi_data = 0
    
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
        
        # Get FPI ratings for both teams
        away_fpi = match_team_to_fpi(away_team, fpi_ratings)
        home_fpi = match_team_to_fpi(home_team, fpi_ratings)
        
        if away_fpi is not None and home_fpi is not None:
            # Determine FPI favorite (higher FPI = better team)
            if home_fpi > away_fpi:
                fpi_favorite = home_team
                fpi_diff = home_fpi - away_fpi
            else:
                fpi_favorite = away_team
                fpi_diff = away_fpi - home_fpi
            
            # Calculate FPI confidence based on rating difference
            # Typical FPI difference is 0-15 points
            fpi_confidence = min(0.5 + (fpi_diff / 20), 0.95)
            
            # Compare with our prediction
            if predicted_winner == fpi_favorite:
                # Agreement - boost confidence
                boost = 0.02 + (fpi_diff / 100)  # Larger FPI diff = bigger boost
                adjusted_confidence = min(base_confidence + boost, 0.99)
                agreements += 1
            else:
                # Disagreement - lower confidence
                penalty = 0.03 + (fpi_diff / 80)  # Larger FPI diff = bigger penalty
                adjusted_confidence = max(base_confidence - penalty, 0.51)
                disagreements += 1
        else:
            # No FPI data for one or both teams
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
    print("📊 Using ESPN FPI team ratings for confidence adjustment")
    print("📊 Higher FPI = Stronger team")
    print("=" * 60)
    
    # Load upcoming_games data
    print("\n📊 Loading upcoming_games data...")
    df = load_sheet_data(SPREADSHEET_ID, 'upcoming_games')
    
    if df.empty:
        print("❌ No data available!")
        return False
    
    print(f"✅ Loaded {len(df)} games")
    
    # Load ESPN FPI ratings
    fpi_ratings = load_fpi_ratings()
    
    if not fpi_ratings:
        print("\n⚠️  No FPI ratings available - keeping original confidence scores")
        adjusted_confidences = []
        for idx, row in df.iterrows():
            base_confidence_str = row.get('winner_confidence', '0.5')
            base_confidence = parse_percentage(base_confidence_str)
            if base_confidence is None:
                base_confidence = 0.5
            adjusted_confidences.append(round(base_confidence, 3))
    else:
        # Adjust confidence with FPI ratings
        adjusted_confidences = adjust_confidence_with_fpi(df, fpi_ratings)
    
    # Find Column BA (index 52)
    ba_col_idx = 52
    
    # Update sheet
    update_sheet(adjusted_confidences, ba_col_idx)
    
    print("\n✅ FPI-ADJUSTED CONFIDENCE SCORES POPULATED!")
    print(f"   - Column BA (winner_confidence_fpi): {len(adjusted_confidences)} scores")
    
    # Show sample results with team info
    print("\n📊 Sample FPI-adjusted confidence scores:")
    for i in range(min(15, len(adjusted_confidences))):
        orig_conf_str = df.iloc[i].get('winner_confidence', '0.5')
        orig_conf = parse_percentage(orig_conf_str)
        if orig_conf is None:
            orig_conf = 0.5
        
        adj_conf = adjusted_confidences[i]
        change = adj_conf - orig_conf
        
        direction = "↑" if change > 0.001 else "↓" if change < -0.001 else "→"
        
        predicted_winner = df.iloc[i].get('predicted_winner', '')
        away_team = df.iloc[i].get('away_team', '')
        home_team = df.iloc[i].get('home_team', '')
        
        print(f"   Game {i+1} ({away_team} @ {home_team}): Predicted {predicted_winner} - {orig_conf:.1%} → {adj_conf:.1%} {direction} ({change:+.1%})")
    
    return True

if __name__ == "__main__":
    success = main()


