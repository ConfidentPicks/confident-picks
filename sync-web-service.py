#!/usr/bin/env python3

"""
WEB SERVICE FOR GOOGLE APPS SCRIPT SYNC
=======================================

This creates a simple web service that Google Apps Script can call
to trigger the Firebase sync. Run this on your local machine.
"""

from flask import Flask, request, jsonify
import subprocess
import os
import sys

app = Flask(__name__)

@app.route('/sync-to-firebase', methods=['POST'])
def sync_to_firebase():
    """Endpoint that Google Apps Script can call to trigger sync"""
    try:
        # Change to the correct directory
        os.chdir(r'C:\Users\durel\Documents\confident-picks-restored')
        
        # Run the sync script
        result = subprocess.run([
            sys.executable, 
            'confident-picks-automation/sync_sheet_to_firebase.py'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Sync completed successfully',
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Sync failed',
                'error': result.stderr
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    print("Starting sync web service...")
    print("Google Apps Script can now call: http://localhost:5000/sync-to-firebase")
    print("Press Ctrl+C to stop")
    app.run(host='localhost', port=5000, debug=False)
