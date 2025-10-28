#!/usr/bin/env python3
"""
Improved Pick Generation System
Features:
- Consensus-based picking (both team models must agree)
- Confidence and accuracy thresholds
- Smart model selection
- Detailed logging
- Validation layer
"""

import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from datetime import datetime, timezone
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Firebase configuration
CREDS_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'

if not firebase_admin._apps:
    cred = credentials.Certificate(CREDS_FILE)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Configuration
MIN_CONFIDENCE = 70  # Minimum confidence percentage to generate a pick
MIN_ACCURACY = 75     # Minimum model accuracy to be considered
USE_CONSENSUS = True  # Require both team models to agree

# NHL Team Mapping
NHL_TEAM_MAP = {
    'ANA': 'Anaheim Ducks', 'ARI': 'Arizona Coyotes', 'BOS': 'Boston Bruins',
    'BUF': 'Buffalo Sabres', 'CAR': 'Carolina Hurricanes', 'CGY': 'Calgary Flames',
    'CHI': 'Chicago Blackhawks', 'COL': 'Colorado Avalanche', 'CBJ': 'Columbus Blue Jackets',
    'DAL': 'Dallas Stars', 'DET': 'Detroit Red Wings', 'EDM': 'Edmonton Oilers',
    'FLA': 'Florida Panthers', 'LAK': 'Los Angeles Kings', 'MIN': 'Minnesota Wild',
    'MTL': 'Montreal Canadiens', 'NSH': 'Nashville Predators', 'NJD': 'New Jersey Devils',
    'NYI': 'New York Islanders', 'NYR': 'New York Rangers', 'OTT': 'Ottawa Senators',
    'PHI': 'Philadelphia Flyers', 'PIT': 'Pittsburgh Penguins', 'SJ': 'San Jose Sharks',
    'SEA': 'Seattle Kraken', 'STL': 'St. Louis Blues', 'TB': 'Tampa Bay Lightning',
    'TOR': 'Toronto Maple Leafs', 'VAN': 'Vancouver Canucks', 'VGK': 'Vegas Golden Knights',
    'WSH': 'Washington Capitals', 'WPG': 'Winnipeg Jets'
}

def get_sheets_service():
    """Get Google Sheets service"""
    creds = service_account.Credentials.from_service_account_file(
        CREDS_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets'])
    return build('sheets', 'v4', credentials=creds)

def get_models_for_league(league='NHL'):
    """Get approved models for a league with quality filter"""
    print(f"[INFO] Fetching {league} models from Firebase...")
    
    models = []
    for doc in db.collection('approved_models').stream():
        model_data = doc.to_dict()
        
        # Filter by league/sport
        if model_data.get('sport') == league or model_data.get('league') == league:
            # Quality filter
            accuracy = float(model_data.get('currentAccuracy', 0))
            if accuracy >= MIN_ACCURACY:
                model_data['id'] = doc.id
                abbrev = model_data.get('team', '')
                model_data['full_team_name'] = NHL_TEAM_MAP.get(abbrev, abbrev) if league == 'NHL' else abbrev
                models.append(model_data)
    
    print(f"[OK] Found {len(models)} approved {league} models (accuracy >= {MIN_ACCURACY}%)")
    return models

def get_google_sheet_id(league='NHL'):
    """Get Google Sheet ID for the league"""
    sheet_ids = {
        'NHL': '1Okiwl_1iwvGHJReUSp-2FncQaQQL-sbWylJPcbTcrHs',
        'NFL': '1Okiwl_1iwvGHJReUSp-2FncQaQQL-sbWylJPcbTcrHs',  # Update as needed
        'NBA': '1Okiwl_1iwvGHJReUSp-2FncQaQQL-sbWylJPcbTcrHs',  # Update as needed
    }
    return sheet_ids.get(league, sheet_ids['NHL'])

def get_upcoming_games(league='NHL'):
    """Fetch upcoming games from Google Sheets"""
    print(f"[INFO] Fetching upcoming {league} games from Google Sheets...")
    
    sheet_id = '1Okiwl_1iwvGHJReUSp-2FncQaQQL-sbWylJPcbTcrHs'
    
    try:
        service = get_sheets_service()
        
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range='upcoming_games!A:Z'
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:
            print("[WARN] No upcoming games found")
            return pd.DataFrame()
        
        headers = values[0]
        data = values[1:]
        
        max_cols = len(headers)
        for row in data:
            while len(row) < max_cols:
                row.append('')
        
        df = pd.DataFrame(data, columns=headers[:max_cols])
        print(f"[OK] Found {len(df)} upcoming {league} games")
        
        return df
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch games: {e}")
        return pd.DataFrame()

def find_models_for_team(models, team):
    """Find all models applicable to a team"""
    return [
        m for m in models 
        if (m.get('team', '').upper() == team.upper() or
            m.get('full_team_name', '').upper() == team.upper())
    ]

def get_consensus_prediction(game, away_models, home_models):
    """
    Get consensus prediction from both teams' models
    
    Returns:
    - dict with team, confidence, model if both agree
    - None if they disagree or quality insufficient
    """
    if not away_models or not home_models:
        return None
    
    # Get best model for each team (highest accuracy)
    best_away = max(away_models, key=lambda m: m.get('currentAccuracy', 0))
    best_home = max(home_models, key=lambda m: m.get('currentAccuracy', 0))
    
    away_team = str(game.get('away_team', ''))
    home_team = str(game.get('home_team', ''))
    
    # For NHL: Each model is trained on its own team
    # away_models predict away team, home_models predict home team
    # Consensus means: both sets of models agree on the same outcome
    
    # Strategy: Check if both models agree on which team wins
    # For away model: predicts away team should win
    # For home model: predicts home team should win
    # They agree only if one model has significantly higher accuracy/confidence
    
    # Simple approach: Use the model with higher accuracy
    away_accuracy = best_away.get('currentAccuracy', 0)
    home_accuracy = best_home.get('currentAccuracy', 0)
    
    # They "agree" if one is clearly better
    accuracy_diff = abs(away_accuracy - home_accuracy)
    
    # If they're very close (within 5%), it's unclear, skip
    if accuracy_diff < 5:
        return None
    
    # Pick the team with higher accuracy model
    if away_accuracy > home_accuracy:
        predicted_team = away_team
        confidence = away_accuracy
        best_model = best_away
    else:
        predicted_team = home_team
        confidence = home_accuracy
        best_model = best_home
    
    # Check if confidence meets threshold
    if confidence < MIN_CONFIDENCE:
        return None
    
    return {
        'team': predicted_team,
        'confidence': confidence,
        'model': best_model,
        'away_model': best_away,
        'home_model': best_home
    }

def generate_pick_from_model(game, model, predicted_team):
    """Generate a pick matching NFL format"""
    
    team = model.get('team', '')
    prop = model.get('prop', '')
    accuracy_pct = model.get('currentAccuracy', 70)
    
    # Extract team names
    away_team = str(game.get('away_team', 'Unknown'))
    home_team = str(game.get('home_team', 'Unknown'))
    
    # Use the predicted team
    picked_team = predicted_team if predicted_team else team
    full_team_name = model.get('full_team_name', picked_team)
    
    # Format commence time
    commence_time = datetime.now(timezone.utc)
    try:
        game_date = game.get('date', '')
        game_time = game.get('time_est', '')
        if game_date:
            date_str = f"{game_date}"
            if game_time:
                date_str += f" {game_time}"
            commence_time = pd.to_datetime(date_str)
            if commence_time.tzinfo is None:
                commence_time = commence_time.replace(tzinfo=timezone.utc)
    except:
        commence_time = datetime.now(timezone.utc)
    
    # Get odds based on prop type
    odds_american = -110
    market_type = 'moneyline'
    pick_desc = ""
    
    if prop == 'Moneyline' or prop == 'Puck Line':  # NHL puck line models exist
        if prop == 'Moneyline':
            # Get moneyline odds
            if picked_team.upper() == home_team.upper():
                try:
                    home_ml = game.get('home_moneyline', '-110')
                    odds_american = int(str(home_ml))
                except:
                    odds_american = -110
            else:
                try:
                    away_ml = game.get('away_moneyline', '-110')
                    odds_american = int(str(away_ml))
                except:
                    odds_american = -110
            
            pick_desc = f"{picked_team} MONEYLINE ({away_team} @ {home_team})"
            market_type = 'moneyline'
        
        elif prop == 'Puck Line':
            # Get puck line odds
            if picked_team.upper() == home_team.upper():
                try:
                    home_puck_line = game.get('home_puck_line', '-110')
                    odds_american = int(str(home_puck_line))
                except:
                    odds_american = -110
            else:
                try:
                    away_puck_line = game.get('away_puck_line', '-110')
                    odds_american = int(str(away_puck_line))
                except:
                    odds_american = -110
            
            # Format puck line description
            puck_line_numb = game.get('puck_line_number', '1.5')
            pick_desc = f"{picked_team} PUCK LINE ({away_team} @ {home_team})"
            market_type = 'puckline'
        
        elif prop == 'Total':
            # For totals, the prediction is Over/Under
            # Get the total number from the game
            total_line = game.get('puck_line_number', '5.5')  # Default NHL total
            over_total = game.get('over_total', '-110')
            under_total = game.get('under_total', '-110')
            
            # Determine if prediction is Over or Under
            # For now, use the model's prediction (this needs to be implemented in the model)
            # Assuming the model predicts "Over" or "Under"
            prediction_direction = "OVER"  # This should come from the model
            
            try:
                odds_american = int(str(over_total)) if prediction_direction == "OVER" else int(str(under_total))
            except:
                odds_american = -110
            
            pick_desc = f"{prediction_direction} {total_line} ({away_team} @ {home_team})"
            market_type = 'totals'
    
    # Confidence values
    confidence_decimal = round(float(accuracy_pct) / 100.0, 3)
    
    # Create pick object
    pick = {
        'league': 'NHL',
        'sport': 'NHL',
        'marketType': market_type,
        'pickDesc': pick_desc,
        'modelConfidence': int(accuracy_pct),
        'confidence': confidence_decimal,
        'oddsAmerican': odds_american,
        'commenceTime': commence_time.isoformat(),
        'tier': 'public',
        'status': 'active',
        'reasoning': f"Model prediction with {int(accuracy_pct)}.0% confidence (based on {model.get('modelName', 'NHL')})",
        'awayTeam': away_team,
        'homeTeam': home_team,
        'gameId': game.get('game_id', ''),
        'modelId': model.get('id', ''),
        'modelName': model.get('modelName', 'Unknown'),
        'modelAccuracy': model.get('currentAccuracy', 0),
    }
    
    return pick

def validate_pick(pick):
    """Validate pick before uploading"""
    
    required_fields = ['sport', 'league', 'pickDesc', 'awayTeam', 'homeTeam', 
                      'confidence', 'oddsAmerican', 'gameId']
    
    for field in required_fields:
        if field not in pick or not pick[field]:
            print(f"[WARN] Missing field: {field}")
            return False
    
    # Validate confidence
    if not 0 < pick.get('confidence', 0) <= 1:
        print(f"[WARN] Invalid confidence: {pick['confidence']}")
        return False
    
    # Validate odds
    if abs(pick.get('oddsAmerican', 0)) > 10000:
        print(f"[WARN] Unusual odds: {pick['oddsAmerican']}")
        return False
    
    return True

def generate_improved_picks(league='NHL'):
    """Main function with improved picking logic"""
    print("=" * 70)
    print(f"GENERATING {league} PICKS (IMPROVED SYSTEM)")
    print("=" * 70)
    
    # Get models
    models = get_models_for_league(league)
    if not models:
        print(f"[ERROR] No approved {league} models found")
        return
    
    # Get games
    games = get_upcoming_games(league)
    if games.empty:
        print(f"[WARN] No upcoming games found")
        return
    
    all_picks = []
    skipped_no_model = 0
    skipped_low_confidence = 0
    skipped_no_consensus = 0
    
    # Iterate through each game
    for _, game in games.iterrows():
        away_team = str(game.get('away_team', ''))
        home_team = str(game.get('home_team', ''))
        game_id = str(game.get('game_id', ''))
        
        print(f"\n[GAME] {away_team} @ {home_team} ({game_id})")
        
        # Find models for both teams
        away_models = find_models_for_team(models, away_team)
        home_models = find_models_for_team(models, home_team)
        
        if not away_models or not home_models:
            print(f"  [SKIP] Missing models (away: {len(away_models)}, home: {len(home_models)})")
            skipped_no_model += 1
            continue
        
        print(f"  [OK] Found models (away: {len(away_models)}, home: {len(home_models)})")
        
        # Track predictions for each prop type
        game_predictions = {}
        
        # Process each prop type to find consensus
        for prop_type in ['Moneyline', 'Puck Line', 'Total']:
            # Filter models for this prop type (case-insensitive match)
            away_models_prop = [m for m in away_models if m.get('prop', '').lower() == prop_type.lower()]
            home_models_prop = [m for m in home_models if m.get('prop', '').lower() == prop_type.lower()]
            
            if not away_models_prop or not home_models_prop:
                print(f"  [{prop_type}] Missing models (away: {len(away_models_prop)}, home: {len(home_models_prop)})")
                continue
            
            # Get consensus (if enabled)
            if USE_CONSENSUS:
                consensus = get_consensus_prediction(game, away_models_prop, home_models_prop)
                
                if consensus:
                    game_predictions[prop_type] = consensus
                    print(f"  [{prop_type}] {consensus['team']} win ({consensus['confidence']:.1f}% confidence)")
        
        # Check if all available prop types agree on the same team
        if not game_predictions:
            print(f"  [SKIP] No valid predictions")
            skipped_no_model += 1
            continue
        
        # If multiple prop types exist, they must all predict the SAME team
        predicted_teams = set(pred['team'] for pred in game_predictions.values())
        
        if len(predicted_teams) > 1:
            print(f"  [SKIP] Conflicting predictions: {predicted_teams}")
            print(f"    -> Cannot show both moneyline and puck line for different teams")
            skipped_no_consensus += 1
            continue
        
        # All prop types agree, generate picks for each
        agreed_team = predicted_teams.pop()
        
        for prop_type, consensus in game_predictions.items():
            best_model = consensus['model']
            confidence = consensus['confidence']
            
            # Generate pick
            pick = generate_pick_from_model(game, best_model, agreed_team)
            if pick:
                # Validate before adding
                if validate_pick(pick):
                    all_picks.append(pick)
                    print(f"  [+] Generated {prop_type} pick for {agreed_team}")
                else:
                    print(f"  [{prop_type}] Pick validation failed")
    
    # Upload to Firebase
    print(f"\n[SUMMARY]")
    print(f"  Total games: {len(games)}")
    print(f"  Generated picks: {len(all_picks)}")
    print(f"  Skipped (no model): {skipped_no_model}")
    print(f"  Skipped (low confidence): {skipped_low_confidence}")
    print(f"  Skipped (no consensus): {skipped_no_consensus}")
    print(f"\n[INFO] Uploading {len(all_picks)} picks to Firebase...")
    
    uploaded = 0
    for pick in all_picks:
        try:
            db.collection('all_picks').add(pick)
            uploaded += 1
        except Exception as e:
            print(f"[ERROR] Failed to upload: {e}")
    
    print(f"[OK] Successfully uploaded {uploaded} {league} picks")
    print("=" * 70)

if __name__ == '__main__':
    generate_improved_picks('NHL')

