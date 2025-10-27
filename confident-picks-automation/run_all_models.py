"""
Master script to run all NFL prediction models daily
- Winner predictions (VA, XA)
- Home spread cover predictions (YA, AB)
- Away spread cover predictions (BB, DB)
- Total predictions (EB, GB)
"""

import subprocess
import sys
import os
from datetime import datetime

# Set UTF-8 encoding for subprocess
os.environ['PYTHONIOENCODING'] = 'utf-8'

def run_script(script_name, description):
    """Run a Python script and report status"""
    print(f"\n{'='*70}")
    print(f"Running: {description}")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            cwd='.'
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"{description} completed successfully")
            return True
        else:
            print(f"{description} failed with exit code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"Error running {description}: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("COMPLETE NFL PREDICTION SYSTEM - DAILY UPDATE")
    print("="*70)
    print(f"Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print("="*70)
    
    scripts = [
        ('daily_prediction_update.py', 'Winner Predictions (VA, XA)'),
        ('ultra_minimal_home_spread_model.py', 'Home Spread Cover Predictions (AY)'),
        ('away_spread_cover_model.py', 'Away Spread Cover Predictions (BB, DB)'),
        ('total_prediction_model.py', 'Total Predictions (EB, GB)')
    ]
    
    results = []
    
    for script, description in scripts:
        success = run_script(script, description)
        results.append((description, success))
    
    print("\n" + "="*70)
    print("DAILY UPDATE SUMMARY")
    print("="*70)
    
    for description, success in results:
        status = "SUCCESS" if success else "FAILED"
        print(f"{status}: {description}")
    
    all_success = all(success for _, success in results)
    
    if all_success:
        print("\nALL MODELS UPDATED SUCCESSFULLY!")
        print("\nUpdated Columns:")
        print("   Winner Predictions:")
        print("      - VA (predicted_winner)")
        print("      - XA (winner_confidence)")
        print("   Home Spread Cover Predictions:")
        print("      - YA (predicted_home_cover)")
        print("      - AB (Home_Cover_Confidence)")
        print("   Away Spread Cover Predictions:")
        print("      - BB (predicted_away_cover)")
        print("      - DB (Away_Cover_Confidence)")
        print("   Total Predictions:")
        print("      - EB (predicted_total)")
        print("      - GB (total_confidence)")
    else:
        print("\nWARNING: SOME MODELS FAILED - CHECK ERRORS ABOVE")
    
    print("="*70 + "\n")
    
    return all_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

