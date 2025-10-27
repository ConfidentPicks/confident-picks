#!/usr/bin/env node

/**
 * Automatic Pick Migration - Move picks between collections as game status changes
 * 
 * This script:
 * 1. Checks upcoming_picks - if odds are added, move to live_picks
 * 2. Checks live_picks - if results are added, calculate W/L and move to completed_picks
 * 3. Runs automatically to keep collections organized
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
  UPCOMING: 'upcoming_picks',
  LIVE: 'live_picks',
  COMPLETED: 'completed_picks'
};

async function main() {
  console.log('\n🔄 AUTOMATIC PICK MIGRATION\n');
  console.log('=' .repeat(70));
  console.log(`📅 ${new Date().toLocaleString()}\n`);
  
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
  console.log('✅ Google Sheets connected\n');
  
  try {
    // Read current game data from sheet
    console.log('📖 Reading current game data from sheet...');
    const response = await sheetsClient.spreadsheets.values.get({
      spreadsheetId: SPREADSHEET_ID,
      range: `${SHEET_NAME}!A1:CZ500`,
    });
    
    const rows = response.data.values;
    if (!rows || rows.length < 2) {
      console.log('⚠️ No data found in sheet');
      return;
    }
    
    const headers = rows[0];
    const colMap = {};
    headers.forEach((header, idx) => {
      colMap[header] = idx;
    });
    
    // Build game status map from sheet
    const gameStatusMap = new Map();
    
    for (let i = 1; i < rows.length; i++) {
      const row = rows[i];
      if (!row || row.length === 0) continue;
      
      const gameId = row[colMap['game_id']] || '';
      if (!gameId) continue;
      
      const awayScore = row[colMap['away_score']] || '';
      const homeScore = row[colMap['home_score']] || '';
      const spreadLine = row[colMap['spread_line']] || '';
      const totalLine = row[colMap['total_line']] || '';
      const awayTeam = row[colMap['away_team']] || '';
      const homeTeam = row[colMap['home_team']] || '';
      const gameday = row[colMap['gameday']] || '';
      
      // Parse game date
      const gameDate = new Date(gameday);
      const now = new Date();
      const isInFuture = gameDate > now;
      
      let status = 'upcoming';
      if (awayScore !== '' && homeScore !== '') {
        status = 'completed';
      } else if (spreadLine !== '' && totalLine !== '' && isInFuture) {
        status = 'live';
      } else if (spreadLine !== '' && totalLine !== '' && !isInFuture) {
        // Old game with odds but date passed - treat as completed
        status = 'completed';
      }
      
      gameStatusMap.set(gameId, {
        status,
        awayTeam,
        homeTeam,
        awayScore,
        homeScore,
        spreadLine,
        totalLine
      });
    }
    
    console.log(`✅ Loaded status for ${gameStatusMap.size} games\n`);
    
    // Migration counters
    let upcomingToLive = 0;
    let liveToCompleted = 0;
    let alreadyCorrect = 0;
    let errors = 0;
    
    const batch = db.batch();
    const picksToDelete = [];
    
    // Check UPCOMING picks - should they move to LIVE?
    console.log('🔍 Checking upcoming_picks for games that now have odds...');
    const upcomingSnapshot = await db.collection(COLLECTIONS.UPCOMING).get();
    
    for (const doc of upcomingSnapshot.docs) {
      const pick = doc.data();
      const gameStatus = gameStatusMap.get(pick.gameId);
      
      if (!gameStatus) continue;
      
      if (gameStatus.status === 'live') {
        // Game now has odds - move to live_picks
        const newPickRef = db.collection(COLLECTIONS.LIVE).doc(doc.id);
        const updatedPick = {
          ...pick,
          status: 'live',
          updatedAt: new Date().toISOString()
        };
        
        batch.set(newPickRef, updatedPick);
        picksToDelete.push({ collection: COLLECTIONS.UPCOMING, id: doc.id });
        
        upcomingToLive++;
        console.log(`   ↗️  ${pick.gameId} (${pick.marketType}) → live_picks`);
        
      } else if (gameStatus.status === 'completed') {
        // Game already completed - move directly to completed_picks
        const actualResult = calculateResult(pick, gameStatus);
        const newPickRef = db.collection(COLLECTIONS.COMPLETED).doc(doc.id);
        const updatedPick = {
          ...pick,
          status: 'completed',
          result: actualResult.result,
          actualResult: actualResult.actualResult,
          updatedAt: new Date().toISOString()
        };
        
        if (pick.marketType === 'totals' && actualResult.actualTotal) {
          updatedPick.actualTotal = actualResult.actualTotal;
        }
        
        batch.set(newPickRef, updatedPick);
        picksToDelete.push({ collection: COLLECTIONS.UPCOMING, id: doc.id });
        
        liveToCompleted++;
        console.log(`   ✅ ${pick.gameId} (${pick.marketType}) → completed_picks [${actualResult.result}]`);
        
      } else {
        alreadyCorrect++;
      }
    }
    
    // Check LIVE picks - should they move to COMPLETED?
    console.log('\n🔍 Checking live_picks for games with results...');
    const liveSnapshot = await db.collection(COLLECTIONS.LIVE).get();
    
    for (const doc of liveSnapshot.docs) {
      const pick = doc.data();
      const gameStatus = gameStatusMap.get(pick.gameId);
      
      if (!gameStatus) continue;
      
      if (gameStatus.status === 'completed') {
        // Game has results - calculate W/L and move to completed_picks
        const actualResult = calculateResult(pick, gameStatus);
        const newPickRef = db.collection(COLLECTIONS.COMPLETED).doc(doc.id);
        const updatedPick = {
          ...pick,
          status: 'completed',
          result: actualResult.result,
          actualResult: actualResult.actualResult,
          updatedAt: new Date().toISOString()
        };
        
        if (pick.marketType === 'totals' && actualResult.actualTotal) {
          updatedPick.actualTotal = actualResult.actualTotal;
        }
        
        batch.set(newPickRef, updatedPick);
        picksToDelete.push({ collection: COLLECTIONS.LIVE, id: doc.id });
        
        liveToCompleted++;
        console.log(`   ✅ ${pick.gameId} (${pick.marketType}) → completed_picks [${actualResult.result}]`);
        
      } else {
        alreadyCorrect++;
      }
    }
    
    // Commit all updates
    if (upcomingToLive > 0 || liveToCompleted > 0) {
      console.log('\n💾 Applying migrations...');
      await batch.commit();
      console.log('✅ Batch updates committed');
      
      // Delete old documents
      console.log('🗑️  Cleaning up old documents...');
      for (const pick of picksToDelete) {
        await db.collection(pick.collection).doc(pick.id).delete();
      }
      console.log('✅ Cleanup complete');
    }
    
    // Summary
    console.log('\n' + '='.repeat(70));
    console.log('🎉 MIGRATION COMPLETE!\n');
    console.log('📊 Summary:');
    console.log(`   📅 → 🔴 Upcoming to Live: ${upcomingToLive} picks`);
    console.log(`   🔴 → ✅ Live to Completed: ${liveToCompleted} picks`);
    console.log(`   ✓ Already correct: ${alreadyCorrect} picks`);
    
    if (errors > 0) {
      console.log(`   ❌ Errors: ${errors}`);
    }
    
    if (upcomingToLive === 0 && liveToCompleted === 0) {
      console.log('\n✨ All picks are in the correct collections!');
    }
    
    console.log('='.repeat(70) + '\n');
    
  } catch (error) {
    console.error('\n❌ MIGRATION FAILED:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

/**
 * Calculate pick result based on actual game outcome
 */
function calculateResult(pick, gameStatus) {
  const awayScore = parseFloat(gameStatus.awayScore);
  const homeScore = parseFloat(gameStatus.homeScore);
  
  const actualResult = {
    awayScore,
    homeScore,
    winner: homeScore > awayScore ? gameStatus.homeTeam : gameStatus.awayTeam
  };
  
  let result = 'L'; // Default to loss
  let actualTotal = null;
  
  switch (pick.marketType) {
    case 'moneyline':
      // Did we pick the winning team?
      result = pick.pick === actualResult.winner ? 'W' : 'L';
      break;
      
    case 'spread':
      // Did our team cover the spread?
      const spreadLine = parseFloat(gameStatus.spreadLine) || 0;
      const pickedHome = pick.pick === gameStatus.homeTeam;
      
      if (pickedHome) {
        const adjustedHomeScore = homeScore + spreadLine;
        result = adjustedHomeScore > awayScore ? 'W' : 'L';
      } else {
        const adjustedHomeScore = homeScore + spreadLine;
        result = awayScore > adjustedHomeScore ? 'W' : 'L';
      }
      break;
      
    case 'totals':
      // Was our over/under correct?
      const totalLine = parseFloat(gameStatus.totalLine) || 0;
      actualTotal = awayScore + homeScore;
      const wasOver = actualTotal > totalLine;
      const predictedOver = pick.pick === 'OVER';
      result = (wasOver === predictedOver) ? 'W' : 'L';
      break;
  }
  
  return {
    result,
    actualResult,
    actualTotal
  };
}

main();

