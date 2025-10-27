#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import firebase_admin
from firebase_admin import credentials, firestore
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import json

def get_scorecard_data_from_sheet():
    print('GETTING SCORECARD DATA FROM GOOGLE SHEET')
    print('=' * 50)
    
    try:
        # Initialize Google Sheets API
        scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        creds = Credentials.from_service_account_file('C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json', scopes=scope)
        service = build('sheets', 'v4', credentials=creds)
        
        # Get the spreadsheet ID (replace with your actual ID)
        spreadsheet_id = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
        
        # Get team accuracy data from the upcoming_games sheet
        # Based on your sheet structure, the team accuracy columns should be around CM-CN area
        range_name = 'upcoming_games!CM1:CN33'  # Team names and their accuracies
        result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])
        
        print('TEAM ACCURACY DATA FROM GOOGLE SHEET:')
        team_accuracies = {}
        
        for i, row in enumerate(values):
            if len(row) >= 2 and i > 0:  # Skip header row
                team_name = row[0] if len(row) > 0 else ''
                accuracy = row[1] if len(row) > 1 else '0%'
                
                if team_name and accuracy != '0%':
                    # Clean up accuracy (remove % and convert to float)
                    try:
                        accuracy_value = float(accuracy.replace('%', ''))
                        team_accuracies[team_name] = accuracy_value
                        print(f'{team_name}: {accuracy}%')
                    except:
                        print(f'Could not parse accuracy for {team_name}: {accuracy}')
        
        # Calculate overall scorecard metrics
        if team_accuracies:
            avg_accuracy = sum(team_accuracies.values()) / len(team_accuracies)
            
            # Determine grade based on average accuracy
            if avg_accuracy >= 89:
                grade = 'A+++'
            elif avg_accuracy >= 81:
                grade = 'A++'
            elif avg_accuracy >= 73:
                grade = 'A+'
            elif avg_accuracy >= 65:
                grade = 'A'
            elif avg_accuracy >= 55:
                grade = 'B'
            elif avg_accuracy >= 50:
                grade = 'C'
            elif avg_accuracy >= 45:
                grade = 'D'
            else:
                grade = 'F'
            
            print(f'\nOVERALL SCORECARD:')
            print(f'Average Accuracy: {avg_accuracy:.1f}%')
            print(f'Grade: {grade}')
            
            return {
                'grade': grade,
                'average_accuracy': avg_accuracy,
                'team_accuracies': team_accuracies,
                'total_teams': len(team_accuracies)
            }
        else:
            print('No team accuracy data found')
            return None
            
    except Exception as e:
        print(f'Error reading sheet: {str(e)}')
        return None

def update_firebase_scorecard(scorecard_data):
    print('UPDATING FIREBASE SCORECARD')
    print('=' * 50)
    
    try:
        # Initialize Firebase Admin
        cred = credentials.Certificate('C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json')
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        
        # Create scorecard document
        scorecard_doc = {
            'grade': scorecard_data['grade'],
            'average_accuracy': scorecard_data['average_accuracy'],
            'total_teams': scorecard_data['total_teams'],
            'team_accuracies': scorecard_data['team_accuracies'],
            'last_updated': '2025-10-24 18:00:00',
            'period': '180_days'  # Based on your sheet calculations
        }
        
        # Update or create the scorecard document
        db.collection('scorecard').document('current').set(scorecard_doc)
        
        print(f'Updated Firebase scorecard:')
        print(f'  Grade: {scorecard_data["grade"]}')
        print(f'  Average Accuracy: {scorecard_data["average_accuracy"]:.1f}%')
        print(f'  Total Teams: {scorecard_data["total_teams"]}')
        
        return True
        
    except Exception as e:
        print(f'Error updating Firebase: {str(e)}')
        return False

if __name__ == "__main__":
    # Step 1: Get scorecard data from Google Sheet
    scorecard_data = get_scorecard_data_from_sheet()
    
    if scorecard_data:
        # Step 2: Update Firebase with scorecard data
        success = update_firebase_scorecard(scorecard_data)
        
        if success:
            print('\n✅ Scorecard updated successfully!')
        else:
            print('\n❌ Failed to update scorecard')
    else:
        print('\n❌ Failed to get scorecard data')
