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

def analyze_spread_opportunities():
    """Analyze spread opportunities for high-performing teams"""
    print("=" * 80)
    print("SPREAD OPPORTUNITIES ANALYSIS")
    print("=" * 80)
    
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
        ("MIA", "ATL", "ATL"),  # (away, home, predicted_winner)
        ("CHI", "BAL", "BAL"),
        ("BUF", "CAR", "CAR"),
        ("NYJ", "CIN", "CIN"),
        ("SF", "HOU", "HOU"),
        ("CLE", "NE", "NE"),
        ("NYG", "PHI", "PHI"),
        ("TB", "NO", "NO"),
        ("DAL", "DEN", "DEN"),
        ("TEN", "IND", "IND"),
        ("GB", "PIT", "PIT"),
        ("WAS", "KC", "KC")
    ]
    
    print("Analyzing spread opportunities for high-performing teams:")
    print("-" * 80)
    
    spread_opportunities = []
    
    for i, (away_team, home_team, predicted_winner) in enumerate(games, 1):
        game = f"{away_team} @ {home_team}"
        print(f"\nGame {i}: {game}")
        print(f"Predicted Winner: {predicted_winner}")
        
        # Check each team for spread opportunities
        for team in [away_team, home_team]:
            if team in high_performers and team != predicted_winner:
                stats = high_performers[team]
                
                if team == home_team:
                    spread_type = "home"
                    spread_accuracy = stats['spread_home']
                else:
                    spread_type = "away"
                    spread_accuracy = stats['spread_away']
                
                print(f"  {team} Spread {spread_type}: {spread_accuracy}% accuracy")
                
                if spread_accuracy >= 50:
                    confidence = "HIGH" if spread_accuracy >= 70 else "MEDIUM"
                    spread_opportunities.append({
                        'game': game,
                        'team': team,
                        'spread_type': spread_type,
                        'accuracy': spread_accuracy,
                        'confidence': confidence
                    })
                    print(f"    *** SPREAD OPPORTUNITY: {team} Spread {spread_type} ({confidence}) ***")
                else:
                    print(f"    Spread accuracy too low ({spread_accuracy}% < 50%)")
    
    print(f"\n{'='*80}")
    print("SPREAD OPPORTUNITIES SUMMARY")
    print(f"{'='*80}")
    
    if spread_opportunities:
        for i, opp in enumerate(spread_opportunities, 1):
            print(f"{i}. {opp['game']}: {opp['team']} Spread {opp['spread_type']}")
            print(f"   Accuracy: {opp['accuracy']}%")
            print(f"   Confidence: {opp['confidence']}")
            print()
    else:
        print("No spread opportunities found with 50%+ accuracy threshold")
        print("\nLet's check with a lower threshold (40%+):")
        
        # Check with 40% threshold
        spread_opportunities_40 = []
        for i, (away_team, home_team, predicted_winner) in enumerate(games, 1):
            game = f"{away_team} @ {home_team}"
            
            for team in [away_team, home_team]:
                if team in high_performers and team != predicted_winner:
                    stats = high_performers[team]
                    
                    if team == home_team:
                        spread_type = "home"
                        spread_accuracy = stats['spread_home']
                    else:
                        spread_type = "away"
                        spread_accuracy = stats['spread_away']
                    
                    if spread_accuracy >= 40:
                        confidence = "HIGH" if spread_accuracy >= 70 else "MEDIUM" if spread_accuracy >= 50 else "LOW"
                        spread_opportunities_40.append({
                            'game': game,
                            'team': team,
                            'spread_type': spread_type,
                            'accuracy': spread_accuracy,
                            'confidence': confidence
                        })
        
        if spread_opportunities_40:
            print(f"\nSPREAD OPPORTUNITIES (40%+ threshold): {len(spread_opportunities_40)}")
            for i, opp in enumerate(spread_opportunities_40, 1):
                print(f"{i}. {opp['game']}: {opp['team']} Spread {opp['spread_type']}")
                print(f"   Accuracy: {opp['accuracy']}%")
                print(f"   Confidence: {opp['confidence']}")
                print()
        else:
            print("Still no spread opportunities with 40%+ threshold")

if __name__ == "__main__":
    analyze_spread_opportunities()

