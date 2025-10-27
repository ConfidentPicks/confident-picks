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

def create_comprehensive_pick_cards():
    """Create comprehensive pick cards with moneyline and spread picks"""
    print("=" * 80)
    print("COMPREHENSIVE PICK CARDS FOR 10/26/2025")
    print("=" * 80)
    
    service = get_sheets_service()
    
    # Get game data and predictions for rows 111-122
    range_name = "upcoming_games!I111:K122"  # Away, Home teams
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
    
    all_picks = []
    
    for i, (game_row, pred_row) in enumerate(zip(games_data, predictions_data)):
        row_number = 111 + i
        game = games[i] if i < len(games) else f"Game {row_number}"
        
        if len(game_row) >= 2 and len(pred_row) >= 3:
            away_team = game_row[0] if len(game_row) > 0 else ""
            home_team = game_row[1] if len(game_row) > 1 else ""
            predicted_winner = pred_row[0] if len(pred_row) > 0 else ""
            winner_confidence = pred_row[2] if len(pred_row) > 2 else ""
            
            print(f"\n{'='*60}")
            print(f"GAME {i+1}: {away_team} @ {home_team}")
            print(f"{'='*60}")
            print(f"Predicted Winner: {predicted_winner}")
            print(f"Model Confidence: {winner_confidence}")
            
            game_picks = []
            
            # Check moneyline picks (predicted winner is high performer)
            if predicted_winner in high_performers:
                stats = high_performers[predicted_winner]
                confidence_level = "HIGH" if stats['moneyline'] >= 70 else "MEDIUM"
                
                reasoning = f"""
{confidence_level} CONFIDENCE MONEYLINE PICK:
• Model predicts {predicted_winner} to win with {winner_confidence} confidence
• {predicted_winner} has {stats['moneyline']}% moneyline accuracy this season
• {'High-performing team with proven track record' if stats['moneyline'] >= 70 else 'Solid performing team above baseline'}"""
                
                pick = {
                    'game': game,
                    'pick': f"{predicted_winner} Moneyline",
                    'confidence': confidence_level,
                    'reasoning': reasoning.strip()
                }
                game_picks.append(pick)
                all_picks.append(pick)
                
                print(f"MONEYLINE PICK: {predicted_winner} ({confidence_level} confidence)")
            
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
                        confidence_level = "HIGH" if spread_accuracy >= 70 else "MEDIUM"
                        
                        reasoning = f"""
{confidence_level} CONFIDENCE SPREAD PICK:
• Model predicts {predicted_winner} to win, but {team} has excellent spread record
• {team} has {spread_accuracy}% spread {spread_type} accuracy this season
• Alternative pick when moneyline prediction conflicts with team performance
• {'High-performing spread team' if spread_accuracy >= 70 else 'Solid spread performer'}"""
                        
                        pick = {
                            'game': game,
                            'pick': f"{team} Spread {spread_type.title()}",
                            'confidence': confidence_level,
                            'reasoning': reasoning.strip()
                        }
                        game_picks.append(pick)
                        all_picks.append(pick)
                        
                        print(f"SPREAD PICK: {team} Spread {spread_type.title()} ({confidence_level} confidence)")
            
            if not game_picks:
                print("No picks meet criteria for this game")
    
    # Summary
    print(f"\n{'='*80}")
    print("FINAL SUMMARY")
    print(f"{'='*80}")
    
    high_confidence = [p for p in all_picks if p['confidence'] == 'HIGH']
    medium_confidence = [p for p in all_picks if p['confidence'] == 'MEDIUM']
    
    print(f"HIGH CONFIDENCE PICKS: {len(high_confidence)}")
    for pick in high_confidence:
        print(f"  • {pick['game']}: {pick['pick']}")
    
    print(f"\nMEDIUM CONFIDENCE PICKS: {len(medium_confidence)}")
    for pick in medium_confidence:
        print(f"  • {pick['game']}: {pick['pick']}")
    
    total_picks = len(all_picks)
    print(f"\nTOTAL PUBLISHABLE PICKS: {total_picks} out of 12 games ({total_picks/12*100:.1f}%)")
    
    # Show detailed reasoning for each pick
    print(f"\n{'='*80}")
    print("DETAILED PICK CARDS")
    print(f"{'='*80}")
    
    for i, pick in enumerate(all_picks, 1):
        print(f"\n{i}. {pick['game']}: {pick['pick']}")
        print(f"   Confidence: {pick['confidence']}")
        print(f"   Reasoning: {pick['reasoning']}")

if __name__ == "__main__":
    create_comprehensive_pick_cards()

