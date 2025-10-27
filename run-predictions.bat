@echo off
echo.
echo ========================================
echo   NFL Prediction System - Auto-Update
echo ========================================
echo.
echo This will update predictions for all upcoming games
echo using your trained models based on historical data.
echo.
echo Model Accuracy: 63.6%%
echo Games to Predict: All upcoming games in your sheet
echo.
pause

cd /d "C:\Users\durel\Documents\confident-picks-restored\confident-picks-automation"

echo.
echo Running prediction system...
echo.

python batch_predictions.py

echo.
echo ========================================
echo   Predictions Complete!
echo ========================================
echo.
echo Check your Google Sheet 'upcoming_games' tab for:
echo   - Predicted winner
echo   - Win probabilities  
echo   - Confidence scores
echo   - Betting recommendations
echo.
echo Run this script anytime to update predictions!
echo.
pause
