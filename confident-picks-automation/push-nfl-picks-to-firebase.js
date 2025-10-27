#!/usr/bin/env node

/**
 * NFL Predictions → Firebase Sync
 * Pushes upcoming_games sheet with all predictions to Firebase
 */

const fs = require('fs');
const path = require('path');
const { initializeApp, cert } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');
const { google } = require('googleapis');

// Configuration
const SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
const SHEET_NAME = 'upcoming_games';

// Firebase Collections
const COLLECTIONS = {
  UPCOMING: 'upcoming_picks',     // No odds yet
  LIVE: 'live_picks',             // Has odds, no results
  COMPLETED: 'completed_picks'    // Has results
};

async function main() {
  console.log('\n🏈 NFL PICKS → FIREBASE SYNC\n');
  console.log('=' .repeat(70));
  
  // Load service account credentials
  const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';
  
  if (!fs.existsSync(serviceAccountPath)) {
    console.error('❌ Service account file not found:', serviceAccountPath);
    process.exit(1);
  }
  
  const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
  
  // Initialize Firebase
  console.log('🔥 Initializing Firebase...');
  const app = initializeApp({ credential: cert(credentials) });
  const db = getFirestore(app);
  console.log('✅ Firebase connected');
  
  // Initialize Google Sheets
  console.log('📊 Connecting to Google Sheets...');
  const auth = new google.auth.GoogleAuth({
    credentials: {
      type: credentials.type,
      project_id: credentials.project_id,
      private_key_id: credentials.private_key_id,
      private_key: credentials.private_key,
      client_email: credentials.client_email,
      client_id: credentials.client_id,
      auth_uri: credentials.auth_uri,
      token_uri: credentials.token_uri,
      auth_provider_x509_cert_url: credentials.auth_provider_x509_cert_url,
      client_x509_cert_url: credentials.client_x509_cert_url,
    },
    scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
  });
  
  const sheetsClient = google.sheets({ version: 'v4', auth });
  console.log('✅ Google Sheets connected');
  
  try {
    console.log('\n📖 Reading NFL predictions from sheet...');
    console.log(`   Sheet: ${SHEET_NAME}`);
    console.log(`   Spreadsheet ID: ${SPREADSHEET_ID}`);
    
    // Read all data from upcoming_games sheet
    const response = await sheetsClient.spreadsheets.values.get({
      spreadsheetId: SPREADSHEET_ID,
      range: `${SHEET_NAME}!A1:CZ500`, // Read all columns up to row 500
    });
    
    const rows = response.data.values;
    
    if (!rows || rows.length < 2) {
      console.log('⚠️ No data found in sheet');
      return;
    }
    
    console.log(`✅ Found ${rows.length - 1} games in sheet\n`);
    
    // Get headers from first row
    const headers = rows[0];
    
    // Map column letters to indices for our prediction columns
    const colMap = {};
    headers.forEach((header, idx) => {
      colMap[header] = idx;
    });
    
    console.log('📋 Prediction Columns Found:');
    const predictionCols = ['predicted_winner', 'winner_confidence', 'winner_confidence_fpi', 
                            'Predicted_Cover_Home', 'Home_Cover_Confidence', 
                            'Predicted_Cover_Away', 'Away_Cover_Confidence',
                            'Predicted_Total', 'total_confidence'];
    
    predictionCols.forEach(col => {
      if (colMap[col] !== undefined) {
        const colLetter = getColumnLetter(colMap[col]);
        console.log(`   ✓ ${col} (Column ${colLetter})`);
      }
    });
    
    // Process data rows (skip header)
    const dataRows = rows.slice(1);
    console.log(`\n📝 Processing ${dataRows.length} games...`);
    console.log('=' .repeat(70));
    
    let successCount = 0;
    let skipCount = 0;
    let errorCount = 0;
    let upcomingCount = 0;
    let liveCount = 0;
    let completedCount = 0;
    
    const batch = db.batch();
    
    for (let i = 0; i < dataRows.length; i++) {
      const row = dataRows[i];
      const rowNumber = i + 2;
      
      try {
        // Skip empty rows
        if (!row || row.length === 0 || !row[0]) {
          skipCount++;
          continue;
        }
        
        // Extract basic game info
        const awayTeam = row[colMap['away_team']] || '';
        const homeTeam = row[colMap['home_team']] || '';
        const gameday = row[colMap['gameday']] || '';
        const gameId = row[colMap['game_id']] || '';
        const awayScore = row[colMap['away_score']] || '';
        const homeScore = row[colMap['home_score']] || '';
        const spreadLine = row[colMap['spread_line']] || '';
        const totalLine = row[colMap['total_line']] || '';
        
        if (!awayTeam || !homeTeam) {
          console.log(`⚠️ Row ${rowNumber}: Missing team names, skipping`);
          skipCount++;
          continue;
        }
        
        // Determine game status and which collection to use
        let targetCollection;
        let gameStatus;
        
        // Parse game date
        const gameDate = new Date(gameday);
        const now = new Date();
        const isInFuture = gameDate > now;
        
        if (awayScore !== '' && homeScore !== '') {
          // Game has results - completed
          targetCollection = COLLECTIONS.COMPLETED;
          gameStatus = 'completed';
        } else if (spreadLine !== '' && totalLine !== '' && isInFuture) {
          // Game has odds AND is in the future - live
          targetCollection = COLLECTIONS.LIVE;
          gameStatus = 'live';
        } else if (spreadLine !== '' && totalLine !== '' && !isInFuture) {
          // Game has odds but date passed (old game without scores yet) - treat as completed
          targetCollection = COLLECTIONS.COMPLETED;
          gameStatus = 'completed';
        } else {
          // No odds yet OR game is too far in future - upcoming
          targetCollection = COLLECTIONS.UPCOMING;
          gameStatus = 'upcoming';
        }
        
        // Extract prediction data
        const predictedWinner = row[colMap['predicted_winner']] || '';
        const winnerConfidence = parseFloat(row[colMap['winner_confidence']]) || 0;
        const winnerConfidenceFpi = parseFloat(row[colMap['winner_confidence_fpi']]) || 0;
        const predictedCoverHome = row[colMap['Predicted_Cover_Home']] || '';
        const homeCoverConfidence = parseFloat(row[colMap['Home_Cover_Confidence']]) || 0;
        const predictedCoverAway = row[colMap['Predicted_Cover_Away']] || '';
        const awayCoverConfidence = parseFloat(row[colMap['Away_Cover_Confidence']]) || 0;
        const predictedTotal = row[colMap['Predicted_Total']] || '';
        const totalConfidence = parseFloat(row[colMap['total_confidence']]) || 0;
        
        // Skip if no predictions available
        if (!predictedWinner && !predictedTotal && !predictedCoverHome) {
          console.log(`⚠️ Row ${rowNumber}: No predictions available, skipping`);
          skipCount++;
          continue;
        }
        
        // Create pick documents for each prediction type
        const picks = [];
        
        // Determine if game has results
        let actualResult = null;
        if (awayScore !== '' && homeScore !== '') {
          const awayScoreNum = parseFloat(awayScore);
          const homeScoreNum = parseFloat(homeScore);
          if (!isNaN(awayScoreNum) && !isNaN(homeScoreNum)) {
            actualResult = {
              awayScore: awayScoreNum,
              homeScore: homeScoreNum,
              winner: homeScoreNum > awayScoreNum ? homeTeam : awayTeam
            };
          }
        }
        
        // WINNER PICK (Moneyline)
        if (predictedWinner) {
          const winnerPick = {
            id: `${gameId}_moneyline`,
            sport: 'NFL',
            league: 'NFL',
            gameId: gameId,
            awayTeam: awayTeam,
            homeTeam: homeTeam,
            gameTime: gameday,
            marketType: 'moneyline',
            pick: predictedWinner,
            pickDesc: `${predictedWinner} to win`,
            modelConfidence: winnerConfidenceFpi > 0 ? winnerConfidenceFpi : winnerConfidence,
            odds: -110,
            status: gameStatus,
            tier: 'public',
            riskTag: winnerConfidenceFpi >= 70 ? 'safe' : 'moderate',
            reasoning: `Model prediction with ${winnerConfidenceFpi.toFixed(1)}% confidence (FPI-adjusted)`,
            source: 'nfl-prediction-model',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          };
          
          // Add result if game is completed
          if (actualResult) {
            winnerPick.result = predictedWinner === actualResult.winner ? 'W' : 'L';
            winnerPick.actualResult = actualResult;
          }
          
          picks.push(winnerPick);
        }
        
        // SPREAD PICK
        const spreadLineNum = parseFloat(spreadLine) || 0;
        if (predictedCoverHome === 'YES' || predictedCoverAway === 'YES') {
          const coveringTeam = predictedCoverHome === 'YES' ? homeTeam : awayTeam;
          const confidence = predictedCoverHome === 'YES' ? homeCoverConfidence : awayCoverConfidence;
          
          const spreadPick = {
            id: `${gameId}_spread`,
            sport: 'NFL',
            league: 'NFL',
            gameId: gameId,
            awayTeam: awayTeam,
            homeTeam: homeTeam,
            gameTime: gameday,
            marketType: 'spread',
            pick: coveringTeam,
            pickDesc: `${coveringTeam} ${spreadLineNum > 0 ? '+' : ''}${spreadLineNum}`,
            modelConfidence: confidence,
            odds: -110,
            status: gameStatus,
            tier: 'public',
            riskTag: confidence >= 70 ? 'safe' : 'moderate',
            reasoning: `Model predicts ${coveringTeam} covers with ${confidence.toFixed(1)}% confidence`,
            source: 'nfl-prediction-model',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          };
          
          // Add result if game is completed
          if (actualResult) {
            // Calculate if spread was covered
            const adjustedHomeScore = actualResult.homeScore + spreadLineNum;
            const covered = coveringTeam === homeTeam ? 
              adjustedHomeScore > actualResult.awayScore : 
              actualResult.awayScore > adjustedHomeScore;
            
            spreadPick.result = covered ? 'W' : 'L';
            spreadPick.actualResult = actualResult;
          }
          
          picks.push(spreadPick);
        }
        
        // TOTAL PICK (Over/Under)
        const totalLineNum = parseFloat(totalLine) || 0;
        if (predictedTotal) {
          const totalPick = {
            id: `${gameId}_total`,
            sport: 'NFL',
            league: 'NFL',
            gameId: gameId,
            awayTeam: awayTeam,
            homeTeam: homeTeam,
            gameTime: gameday,
            marketType: 'totals',
            pick: predictedTotal,
            pickDesc: `${predictedTotal} ${totalLineNum}`,
            modelConfidence: totalConfidence,
            odds: -110,
            status: gameStatus,
            tier: 'public',
            riskTag: totalConfidence >= 70 ? 'safe' : 'moderate',
            reasoning: `Model predicts ${predictedTotal} ${totalLineNum} with ${totalConfidence.toFixed(1)}% confidence`,
            source: 'nfl-prediction-model',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          };
          
          // Add result if game is completed
          if (actualResult) {
            const actualTotal = actualResult.awayScore + actualResult.homeScore;
            const wasOver = actualTotal > totalLineNum;
            const predictedOver = predictedTotal === 'OVER';
            
            totalPick.result = (wasOver === predictedOver) ? 'W' : 'L';
            totalPick.actualResult = actualResult;
            totalPick.actualTotal = actualTotal;
          }
          
          picks.push(totalPick);
        }
        
        // Add all picks to batch in the appropriate collection
        for (const pick of picks) {
          const docRef = db.collection(targetCollection).doc(pick.id);
          batch.set(docRef, pick, { merge: true });
        }
        
        // Track counts
        if (gameStatus === 'upcoming') upcomingCount++;
        else if (gameStatus === 'live') liveCount++;
        else if (gameStatus === 'completed') completedCount++;
        
        console.log(`✅ Row ${rowNumber}: ${awayTeam} @ ${homeTeam} - ${picks.length} picks → ${targetCollection} (${gameStatus})`);
        successCount++;
        
      } catch (error) {
        console.log(`❌ Row ${rowNumber}: Error - ${error.message}`);
        errorCount++;
      }
    }
    
    // Commit batch
    console.log('\n' + '='.repeat(70));
    console.log('💾 Pushing to Firebase...');
    await batch.commit();
    console.log('✅ Batch committed successfully!');
    
    console.log('\n🎉 SYNC COMPLETED!\n');
    console.log('📊 Summary:');
    console.log(`   ✅ Successfully synced: ${successCount} games`);
    console.log(`   ⚠️ Skipped: ${skipCount} rows (empty or no predictions)`);
    if (errorCount > 0) {
      console.log(`   ❌ Errors: ${errorCount} rows`);
    }
    console.log('\n📦 Firebase Collections:');
    console.log(`   📅 ${COLLECTIONS.UPCOMING}: ${upcomingCount} games (no odds yet)`);
    console.log(`   🔴 ${COLLECTIONS.LIVE}: ${liveCount} games (active with odds)`);
    console.log(`   ✅ ${COLLECTIONS.COMPLETED}: ${completedCount} games (with results)`);
    console.log('\n💡 Your NFL picks are organized in Firebase!');
    console.log('=' .repeat(70) + '\n');
    
  } catch (error) {
    console.error('\n❌ SYNC FAILED:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

function getColumnLetter(colIndex) {
  let letter = '';
  let index = colIndex;
  while (index >= 0) {
    letter = String.fromCharCode((index % 26) + 65) + letter;
    index = Math.floor(index / 26) - 1;
  }
  return letter;
}

main();

