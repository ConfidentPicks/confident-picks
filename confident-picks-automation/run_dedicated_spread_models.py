#!/usr/bin/env python3

"""
Master script to run dedicated home and away spread cover models
- Home spread cover predictions (YA, AB)
- Away spread cover predictions (BB, DB)
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
        # Run the script
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print(f"SUCCESS: {description}")
            if result.stdout:
                print("Output:")
                print(result.stdout)
        else:
            print(f"ERROR: {description}")
            if result.stderr:
                print("Error output:")
                print(result.stderr)
            if result.stdout:
                print("Standard output:")
                print(result.stdout)
                
        return result.returncode == 0
        
    except Exception as e:
        print(f"EXCEPTION: {description}")
        print(f"Error: {e}")
        return False

def main():
    print("=" * 80)
    print("DEDICATED SPREAD COVER PREDICTION MODELS")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run dedicated home spread cover model
    success_home = run_script(
        'home_spread_cover_model.py',
        'Dedicated Home Spread Cover Model'
    )
    
    # Run dedicated away spread cover model
    success_away = run_script(
        'away_spread_cover_model.py',
        'Dedicated Away Spread Cover Model'
    )
    
    print("\n" + "=" * 80)
    print("DEDICATED SPREAD MODELS SUMMARY")
    print("=" * 80)
    print(f"Home Spread Model: {'SUCCESS' if success_home else 'FAILED'}")
    print(f"Away Spread Model: {'SUCCESS' if success_away else 'FAILED'}")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success_home and success_away:
        print("\nAll dedicated spread models completed successfully!")
        print("Updated columns:")
        print("  - YA (predicted_home_cover)")
        print("  - AB (Home_Cover_Confidence)")
        print("  - BB (predicted_away_cover)")
        print("  - DB (Away_Cover_Confidence)")
        return True
    else:
        print("\nSome dedicated spread models failed!")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\nDedicated spread models completed successfully!")
    else:
        print("\nDedicated spread models failed!")
        sys.exit(1)

