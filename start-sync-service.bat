@echo off
echo ========================================
echo STARTING SYNC WEB SERVICE
echo ========================================
echo.
echo This web service allows Google Apps Script to sync to Firebase
echo Keep this window open while using the sync button in Google Sheets
echo.
echo Press Ctrl+C to stop the service
echo.

cd /d "C:\Users\durel\Documents\confident-picks-restored"

python sync-web-service.py
