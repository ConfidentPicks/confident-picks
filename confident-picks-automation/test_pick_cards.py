#!/usr/bin/env python3

"""
TEST PICK CARD GENERATION
=========================

This script creates pick cards in a test collection to avoid interfering
with the live system. Reasoning is split into 3 parts for better organization.

INTEGRATION OPTIONS:
1. Add to your existing run_all_models.py script
2. Run as a separate scheduled task
3. Call from your existing Firebase push scripts

USAGE:
- Run manually: python create_test_pick_cards.py
- Integrate: Import and call create_test_pick_cards()
"""

import pandas as pd
import numpy as np
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import firebase_admin
from firebase_admin import credentials, firestore
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

def get_firestore_client():
    """Get Firestore client"""
    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
        firebase_admin.initialize_app(cred)
    return firestore.client()

def generate_pick_reasoning_split(pick_type, team, predicted_winner, winner_confidence, team_accuracy, spread_accuracy=None):
    """Generate standardized reasoning split into 3 parts"""
    
    if pick_type == "moneyline":
        confidence_level = "HIGH" if team_accuracy >= 70 else "MEDIUM"
        
        reasoning_part1 = f"Model Prediction: {team} to win ({winner_confidence} confidence)"
        reasoning_part2 = f"Team Performance: {team_accuracy}% moneyline accuracy this season"
        reasoning_part3 = f"Signal Alignment: Model and performance both favor {team} - {confidence_level} confidence (everything aligned)"
    
    elif pick_type == "spread":
        confidence_level = "MEDIUM"  # Always medium for spread picks due to conflicting signals
        spread_type = "home" if spread_accuracy else "away"
        
        reasoning_part1 = f"Model Prediction: {predicted_winner} to win ({winner_confidence} confidence)"
        reasoning_part2 = f"Team Performance: {team} has {spread_accuracy}% spread {spread_type} accuracy"
        reasoning_part3 = f"Signal Conflict: Model favors {predicted_winner}, but {team} excels at covering spreads - MEDIUM confidence (conflicting signals)"
    
    return reasoning_part1, reasoning_part2, reasoning_part3

def create_test_pick_cards():
    """Create pick cards and push to Firebase test_picks collection"""
    print("=" * 80)
    print("CREATING TEST PICK CARDS FOR FIREBASE")
    print("=" * 80)
    
    service = get_sheets_service()
    db = get_firestore_client()
    
    # Get game data and predictions for rows 111-122
    range_name = "upcoming_games!H111:J122"  # Away, Home teams
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    games_data = result.get('values', [])
    
    # Get predictions
    range_name2 = "upcoming_games!AV111:AX122"  # Winner predictions and confidence
    result2 = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name2).execute()
    predictions_data = result2.get('values', [])
    
    # High-performing teams (60%+ threshold)
    high_performers = {
        'DAL': {'moneyline': 85.71, 'spread_home': 100, 'spread_away': 100},
        'CAR': {'moneyline': 85.71, 'spread_home': 66.67, 'spread_away': 66.67},
        'NYG': {'moneyline': 80, 'spread_home': 33.33, 'spread_away': 33.33},
        'ATL': {'moneyline': 80, 'spread_home': 50, 'spread_away': 50},
        'CLE': {'moneyline': 80, 'spread_home': 66.67, 'spread_away': 66.67},
        'BUF': {'moneyline': 80, 'spread_home': 33.33, 'spread_away': 33.33},
        'TB': {'moneyline': 50, 'spread_home': 100, 'spread_away': 100},
        'TEN': {'moneyline': 0, 'spread_home': 100, 'spread_away': 100},
        'WAS': {'moneyline': 50, 'spread_home': 100, 'spread_away': 100},
        'SEA': {'moneyline': 57.14, 'spread_home': 100, 'spread_away': 100},
        'GB': {'moneyline': 66.67, 'spread_home': 100, 'spread_away': 100}
    }
    
    games = [
        "MIA @ ATL", "CHI @ BAL", "BUF @ CAR", "NYJ @ CIN", "SF @ HOU",
        "CLE @ NE", "NYG @ PHI", "TB @ NO", "DAL @ DEN", "TEN @ IND",
        "GB @ PIT", "WAS @ KC"
    ]
    
    pick_cards = []
    
    for i, (game_row, pred_row) in enumerate(zip(games_data, predictions_data)):
        row_number = 111 + i
        game = games[i] if i < len(games) else f"Game {row_number}"
        
        if len(game_row) >= 2 and len(pred_row) >= 3:
            away_team = game_row[0] if len(game_row) > 0 else ""
            home_team = game_row[1] if len(game_row) > 1 else ""
            predicted_winner = pred_row[0] if len(pred_row) > 0 else ""
            winner_confidence = pred_row[2] if len(pred_row) > 2 else ""
            
            # Check moneyline picks (predicted winner is high performer)
            if predicted_winner in high_performers:
                stats = high_performers[predicted_winner]
                confidence_level = "HIGH" if stats['moneyline'] >= 70 else "MEDIUM"
                
                reasoning_part1, reasoning_part2, reasoning_part3 = generate_pick_reasoning_split(
                    "moneyline", 
                    predicted_winner, 
                    predicted_winner, 
                    winner_confidence, 
                    stats['moneyline']
                )
                
                pick_card = {
                    'game': game,
                    'away_team': away_team,
                    'home_team': home_team,
                    'pick_type': 'moneyline',
                    'pick_team': predicted_winner,
                    'confidence_level': confidence_level,
                    'model_confidence': winner_confidence,
                    'team_accuracy': stats['moneyline'],
                    'reasoning_part1': reasoning_part1,
                    'reasoning_part2': reasoning_part2,
                    'reasoning_part3': reasoning_part3,
                    'game_date': '2025-10-26',
                    'status': 'test',
                    'created_at': firestore.SERVER_TIMESTAMP
                }
                
                pick_cards.append(pick_card)
            
            # Check spread picks (high performer not predicted to win)
            for team in [away_team, home_team]:
                if team in high_performers and team != predicted_winner:
                    stats = high_performers[team]
                    
                    # Determine if it's home or away spread
                    if team == home_team:
                        spread_type = "home"
                        spread_accuracy = stats['spread_home']
                    else:
                        spread_type = "away"
                        spread_accuracy = stats['spread_away']
                    
                    # Only recommend if spread accuracy is decent (50%+)
                    if spread_accuracy >= 50:
                        reasoning_part1, reasoning_part2, reasoning_part3 = generate_pick_reasoning_split(
                            "spread", 
                            team, 
                            predicted_winner, 
                            winner_confidence, 
                            None, 
                            spread_accuracy
                        )
                        
                        pick_card = {
                            'game': game,
                            'away_team': away_team,
                            'home_team': home_team,
                            'pick_type': 'spread',
                            'pick_team': team,
                            'spread_type': spread_type,
                            'confidence_level': 'MEDIUM',
                            'model_confidence': winner_confidence,
                            'team_accuracy': spread_accuracy,
                            'reasoning_part1': reasoning_part1,
                            'reasoning_part2': reasoning_part2,
                            'reasoning_part3': reasoning_part3,
                            'game_date': '2025-10-26',
                            'status': 'test',
                            'created_at': firestore.SERVER_TIMESTAMP
                        }
                        
                        pick_cards.append(pick_card)
    
    # Push to Firebase test_picks collection
    print(f"Pushing {len(pick_cards)} pick cards to Firebase test_picks collection...")
    
    for pick_card in pick_cards:
        try:
            # Create document ID based on game and pick type
            doc_id = f"{pick_card['game'].replace(' @ ', '_vs_').replace(' ', '_')}_{pick_card['pick_type']}_{pick_card['pick_team']}"
            doc_id = doc_id.replace(' ', '_').replace('@', 'vs')
            
            # Add to test_picks collection
            doc_ref = db.collection('test_picks').document(doc_id)
            doc_ref.set(pick_card)
            
        except Exception as e:
            print(f"Error adding {pick_card['game']}: {str(e)}")
    
    print(f"Successfully created {len(pick_cards)} test pick cards in Firebase")
    return len(pick_cards)

if __name__ == "__main__":
    create_test_pick_cards()

