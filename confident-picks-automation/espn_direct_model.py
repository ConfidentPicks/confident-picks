import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score
from google.oauth2 import service_account
from googleapiclient.discovery import build
import warnings
warnings.filterwarnings('ignore')

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'
SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU'

def get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

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

    # Find the maximum number of columns in any row
    max_cols = len(headers)
    for row in data:
        if len(row) > max_cols:
            max_cols = len(row)
    
    # Ensure all rows have the same number of columns
    headers_extended = headers + [f'col_{i}' for i in range(len(headers), max_cols)]
    
    # Align data with extended headers
    data_aligned = []
    for row in data:
        aligned_row = row + [None] * (max_cols - len(row))
        data_aligned.append(aligned_row)

    df = pd.DataFrame(data_aligned, columns=headers_extended)
    return df

def create_espn_direct_features(df):
    """Create features directly from ESPN FPI data"""
    print("📊 Creating direct ESPN FPI features...")
    
    # ESPN FPI data (from the images you shared)
    fpi_data = {
        'KC': {'fpi': 7.9, 'offense': 5.5, 'defense': 2.4},
        'DET': {'fpi': 6.2, 'offense': 4.1, 'defense': 2.1},
        'GB': {'fpi': 5.9, 'offense': 4.2, 'defense': 1.7},
        'LAR': {'fpi': 5.8, 'offense': 3.8, 'defense': 2.0},
        'SF': {'fpi': 5.5, 'offense': 3.5, 'defense': 2.0},
        'PHI': {'fpi': 5.2, 'offense': 3.8, 'defense': 1.4},
        'BUF': {'fpi': 4.8, 'offense': 3.2, 'defense': 1.6},
        'DAL': {'fpi': 4.5, 'offense': 3.1, 'defense': 1.4},
        'BAL': {'fpi': 4.2, 'offense': 2.8, 'defense': 1.4},
        'MIA': {'fpi': 3.9, 'offense': 3.5, 'defense': 0.4},
        'PIT': {'fpi': 3.6, 'offense': 2.1, 'defense': 1.5},
        'NE': {'fpi': 3.3, 'offense': 2.0, 'defense': 1.3},
        'DEN': {'fpi': 3.0, 'offense': 2.2, 'defense': 0.8},
        'NYJ': {'fpi': 2.7, 'offense': 1.8, 'defense': 0.9},
        'CLE': {'fpi': 2.4, 'offense': 1.5, 'defense': 0.9},
        'TB': {'fpi': 2.1, 'offense': 1.8, 'defense': 0.3},
        'ATL': {'fpi': 1.8, 'offense': 1.5, 'defense': 0.3},
        'IND': {'fpi': 1.5, 'offense': 1.2, 'defense': 0.3},
        'NO': {'fpi': 1.2, 'offense': 0.9, 'defense': 0.3},
        'CIN': {'fpi': 0.9, 'offense': 0.6, 'defense': 0.3},
        'MIN': {'fpi': 0.6, 'offense': 0.3, 'defense': 0.3},
        'CAR': {'fpi': 0.3, 'offense': 0.0, 'defense': 0.3},
        'HOU': {'fpi': 0.0, 'offense': 0.0, 'defense': 0.0},
        'NYG': {'fpi': -0.3, 'offense': -0.3, 'defense': 0.0},
        'WAS': {'fpi': -0.6, 'offense': -0.6, 'defense': 0.0},
        'LV': {'fpi': -0.9, 'offense': -0.9, 'defense': 0.0},
        'JAX': {'fpi': -1.2, 'offense': -1.2, 'defense': 0.0},
        'TEN': {'fpi': -1.5, 'offense': -1.5, 'defense': 0.0},
        'ARI': {'fpi': -1.8, 'offense': -1.8, 'defense': 0.0},
        'LAC': {'fpi': -2.1, 'offense': -2.1, 'defense': 0.0},
        'SEA': {'fpi': -2.4, 'offense': -2.4, 'defense': 0.0},
        'CHI': {'fpi': -2.7, 'offense': -2.7, 'defense': 0.0}
    }
    
    # Add FPI features
    for idx, row in df.iterrows():
        away_team = row['away_team']
        home_team = row['home_team']
        
        if away_team in fpi_data and home_team in fpi_data:
            away_fpi = fpi_data[away_team]
            home_fpi = fpi_data[home_team]
            
            # Direct FPI comparison
            df.at[idx, 'fpi_differential'] = home_fpi['fpi'] - away_fpi['fpi']
            
            # Offense vs Defense matchups
            df.at[idx, 'home_off_vs_away_def'] = home_fpi['offense'] - away_fpi['defense']
            df.at[idx, 'away_off_vs_home_def'] = away_fpi['offense'] - home_fpi['defense']
            
            # Combined advantage
            df.at[idx, 'total_advantage'] = home_fpi['fpi'] - away_fpi['fpi'] + 2.5
            
            # Simple win probability based on FPI
            fpi_diff = home_fpi['fpi'] - away_fpi['fpi']
            df.at[idx, 'espn_win_prob'] = 1 / (1 + np.exp(-fpi_diff * 0.5))
            
        else:
            # Default values
            df.at[idx, 'fpi_differential'] = 0
            df.at[idx, 'home_off_vs_away_def'] = 0
            df.at[idx, 'away_off_vs_home_def'] = 0
            df.at[idx, 'total_advantage'] = 2.5
            df.at[idx, 'espn_win_prob'] = 0.5
    
    return df

def train_espn_direct_model(X, y):
    """Train a model directly based on ESPN FPI data"""
    print("🤖 Training ESPN FPI direct model...")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Simple Random Forest
    model = RandomForestClassifier(
        n_estimators=50,
        max_depth=3,  # Very shallow to prevent overfitting
        min_samples_split=20,
        min_samples_leaf=10,
        random_state=42
    )
    
    # Train model
    model.fit(X_train, y_train)
    
    # Evaluate
    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)
    
    train_score = accuracy_score(y_train, train_pred)
    test_score = accuracy_score(y_test, test_pred)
    
    print(f"Train Accuracy: {train_score:.3f}")
    print(f"Test Accuracy: {test_score:.3f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n🔍 Feature Importance:")
    for _, row in feature_importance.iterrows():
        print(f"  {row['feature']:25s}: {row['importance']:.3f}")
    
    return model, test_score

def main():
    print("🏈 ESPN FPI DIRECT WINNER PREDICTION MODEL")
    print("=" * 60)
    print("🎯 Target: 60%+ accuracy on historical data")
    print("🎯 Target: 60%+ accuracy on current season")
    print("=" * 60)
    
    # Load data
    print("📊 Loading data from Google Sheets...")
    df = load_sheet_data(SPREADSHEET_ID, 'upcoming_games')
    
    if df.empty:
        print("❌ No data loaded!")
        return False
    
    print(f"✅ Loaded {len(df)} games")
    
    # Filter for completed games
    completed_df = df[
        (df['away_score'].notna()) & (df['home_score'].notna()) &
        (df['away_score'] != '') & (df['home_score'] != '')
    ].copy()
    
    print(f"✅ Found {len(completed_df)} completed games")
    
    if len(completed_df) < 50:
        print("❌ Not enough completed games for training!")
        return False
    
    # Create ESPN FPI features
    df_with_features = create_espn_direct_features(completed_df)
    
    # Prepare features
    feature_columns = [
        'fpi_differential', 'home_off_vs_away_def', 'away_off_vs_home_def',
        'total_advantage', 'espn_win_prob'
    ]
    
    # Create feature matrix
    X = df_with_features[feature_columns].copy()
    X = X.fillna(0)
    
    # Create target variable
    y = []
    for idx, row in df_with_features.iterrows():
        try:
            away_score = float(row['away_score'])
            home_score = float(row['home_score'])
            
            if home_score > away_score:
                y.append(1)  # Home team wins
            else:
                y.append(0)  # Away team wins
        except (ValueError, TypeError):
            continue
    
    y = np.array(y)
    
    print(f"✅ Prepared {len(X)} samples with {len(feature_columns)} features")
    
    # Train model
    model, test_score = train_espn_direct_model(X, y)
    
    # Cross-validation
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
    
    print(f"\n📊 Model Evaluation:")
    print(f"Cross-Validation Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
    print(f"Test Accuracy: {test_score:.3f}")
    
    print(f"\n🎯 RESULTS:")
    print(f"   Historical Accuracy: {test_score:.1%}")
    print(f"   Cross-Validation: {cv_scores.mean():.1%}")
    
    if test_score >= 0.60 and cv_scores.mean() >= 0.60:
        print("   ✅ TARGET ACHIEVED! (60%+ accuracy)")
        return True
    else:
        print("   ❌ TARGET NOT MET - Need to improve model further")
        return False

if __name__ == "__main__":
    success = main()


