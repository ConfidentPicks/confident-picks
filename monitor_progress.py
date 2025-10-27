#!/usr/bin/env python3
"""
Monitor Progress - Check running scripts and send notifications
Runs every 15 minutes and notifies on completion or failure
"""

import json
import time
import os
import subprocess
from datetime import datetime
from pathlib import Path

# Progress files to monitor
PROGRESS_FILES = [
    'confident-picks-automation/nhl_moneyline_progress.json',
    'confident-picks-automation/nhl_puckline_progress.json',
    'confident-picks-automation/nfl_moneyline_progress.json',
    'confident-picks-automation/nfl_spread_progress.json',
    'confident-picks-automation/nfl_total_progress.json',
    'confident-picks-automation/nba_fetch_progress.json'
]

def check_progress_files():
    """Check all progress files and return status"""
    results = {}
    
    for progress_file in PROGRESS_FILES:
        file_path = Path(progress_file)
        
        if not file_path.exists():
            results[progress_file] = {
                'exists': False,
                'status': 'not_started'
            }
            continue
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            results[progress_file] = {
                'exists': True,
                'status': data.get('status', 'unknown'),
                'message': data.get('message', ''),
                'progress_percent': data.get('progress_percent', 0),
                'last_updated': data.get('last_updated', '')
            }
        except Exception as e:
            results[progress_file] = {
                'exists': True,
                'status': 'error',
                'error': str(e)
            }
    
    return results

def check_python_processes():
    """Check if Python processes are still running"""
    try:
        result = subprocess.run(
            ['powershell', '-Command', 'Get-Process python -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count'],
            capture_output=True,
            text=True
        )
        
        count = int(result.stdout.strip()) if result.stdout.strip() else 0
        return count
    except:
        return 0

def send_notification(title, message):
    """Send Windows notification"""
    try:
        # Use PowerShell to show toast notification
        ps_script = f'''
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
        $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
        $textNodes = $template.GetElementsByTagName("text")
        $textNodes.Item(0).AppendChild($template.CreateTextNode("{title}"))
        $textNodes.Item(1).AppendChild($template.CreateTextNode("{message}"))
        $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
        $toast.ExpirationTime = [DateTimeOffset]::Now.AddMinutes(1)
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Confident Picks Monitor").Show($toast)
        '''
        
        subprocess.run(['powershell', '-Command', ps_script], capture_output=True)
        print(f"✓ Notification sent: {title}")
    except Exception as e:
        print(f"⚠ Could not send notification: {e}")
        print(f"  {title}: {message}")

def main():
    """Main monitoring loop"""
    print("=" * 60)
    print("CONFIDENT PICKS - PROGRESS MONITOR")
    print("=" * 60)
    print("Monitoring scripts every 15 minutes...")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    # Track previous states
    previous_status = {}
    
    try:
        while True:
            # Check progress files
            results = check_progress_files()
            
            # Check if processes are still running
            process_count = check_python_processes()
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking progress...")
            print(f"  Python processes: {process_count}")
            
            # Check each progress file for changes
            for file_path, data in results.items():
                script_name = file_path.split('/')[-1].replace('.json', '')
                
                if file_path in previous_status:
                    prev = previous_status[file_path]
                    
                    # Check for status changes
                    if data.get('status') != prev.get('status'):
                        new_status = data.get('status', 'unknown')
                        
                        if new_status == 'complete':
                            send_notification(
                                "✓ Script Completed!",
                                f"{script_name} has finished successfully"
                            )
                        elif new_status == 'failed':
                            send_notification(
                                "❌ Script Failed!",
                                f"{script_name} encountered an error"
                            )
                        elif new_status == 'running':
                            send_notification(
                                "▶️ Script Started",
                                f"{script_name} has started running"
                            )
                    
                    # Check for progress updates
                    if data.get('progress_percent') and prev.get('progress_percent'):
                        progress = data.get('progress_percent', 0)
                        prev_progress = prev.get('progress_percent', 0)
                        
                        if progress != prev_progress:
                            print(f"  {script_name}: {progress}%")
                
                previous_status[file_path] = data
            
            # Check if all processes stopped unexpectedly
            if process_count == 0 and any(r.get('status') not in ['complete', 'failed', 'not_started'] for r in results.values()):
                send_notification(
                    "⚠️ All Scripts Stopped",
                    "All Python processes have stopped. Check for errors."
                )
            
            print()
            
            # Wait 15 minutes before next check
            print("Waiting 15 minutes until next check...")
            time.sleep(15 * 60)  # 15 minutes
            
    except KeyboardInterrupt:
        print("\n\nMonitor stopped by user")
        send_notification(
            "Monitor Stopped",
            "Progress monitoring has been stopped"
        )

if __name__ == '__main__':
    main()
