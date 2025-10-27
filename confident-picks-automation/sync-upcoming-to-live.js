#!/usr/bin/env node

/**
 * Sync Upcoming Games to Live Picks
 * 
 * Copies uncompleted games from upcoming_games to:
 * 1. live_picks_sheets (Google Sheets)
 * 2. picks collection (Firebase)
 * 
 * Adds matchup column and maps to coordinating columns
 */

const fs = require('fs');
const { google } = require('googleapis');
const admin = require('firebase-admin');

/**
 * Initialize Firebase Admin
 */
function initializeFirebase() {
  const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';
  const serviceAccount = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
  
  if (!admin.apps.length) {
    admin.initializeApp({
      credential: admin.credential.cert(serviceAccount),
    });
  }
  
  return admin.firestore();
}

/**
 * Initialize Google Sheets client
 */
function initializeSheetsClient(credentials) {
  const auth = new google.auth.GoogleAuth({
    credentials,
    scopes: ['https://www.googleapis.com/auth/spreadsheets'],
  });

  return google.sheets({ version: 'v4', auth });
}

/**
 * Read upcoming games from sheet
 */
async function readUpcomingGames(sheetsClient, spreadsheetId) {
  try {
    console.log('📖 Reading upcoming games...');
    
    const response = await sheetsClient.spreadsheets.values.get({
      spreadsheetId,
      range: 'upcoming_games!A1:ZZ10000',
    });
    
    const rows = response.data.values || [];
    if (rows.length === 0) {
      return [];
    }
    
    const headers = rows[0];
    const games = [];
    
    for (let i = 1; i < rows.length; i++) {
      const row = rows[i];
      const game = {};
      
      headers.forEach((header, index) => {
        game[header] = row[index] || '';
      });
      
      games.push(game);
    }
    
    console.log(`   Found ${games.length} total games`);
    return games;
    
  } catch (error) {
    console.error('Error reading upcoming games:', error.message);
    return [];
  }
}

/**
 * Filter for uncompleted games (no score yet or future games)
 */
function filterUncompletedGames(games) {
  const uncompleted = games.filter(game => {
    // Game is uncompleted if:
    // 1. No scores yet (home_score and away_score are empty or null)
    // 2. Game date is in the future
    const hasNoScore = !game.home_score || !game.away_score || 
                       game.home_score === 'None' || game.away_score === 'None' ||
                       game.home_score === '' || game.away_score === '';
    
    const gameDate = new Date(game.gameday);
    const now = new Date();
    const isFuture = gameDate > now;
    
    return hasNoScore || isFuture;
  });
  
  console.log(`   Filtered to ${uncompleted.length} uncompleted games`);
  return uncompleted;
}

/**
 * Transform game data to live picks format
 */
function transformToLivePicksFormat(games) {
  const transformed = games.map(game => {
    // Create matchup string
    const matchup = `${game.away_team} @ ${game.home_team}`;
    
    return {
      game_id: game.game_id || '',
      matchup: matchup,
      week: game.week || '',
      gameday: game.gameday || '',
      gametime: game.gametime || '',
      away_team: game.away_team || '',
      home_team: game.home_team || '',
      spread_line: game.spread_line || '',
      away_spread_odds: game.away_spread_odds || '',
      home_spread_odds: game.home_spread_odds || '',
      total_line: game.total_line || '',
      over_odds: game.over_odds || '',
      under_odds: game.under_odds || '',
      away_moneyline: game.away_moneyline || '',
      home_moneyline: game.home_moneyline || '',
      location: game.location || '',
      stadium: game.stadium || '',
      roof: game.roof || '',
      surface: game.surface || '',
      temp: game.temp || '',
      wind: game.wind || '',
      away_qb_name: game.away_qb_name || '',
      home_qb_name: game.home_qb_name || '',
      away_coach: game.away_coach || '',
      home_coach: game.home_coach || '',
      referee: game.referee || '',
      // Future picks columns (empty for user to fill)
      my_moneyline_pick: '',
      my_spread_pick: '',
      my_total_pick: '',
      pick_confidence: '',
      pick_reasoning: '',
      bet_size: '',
      expected_value: ''
    };
  });
  
  return transformed;
}

/**
 * Convert to sheet format
 */
function toSheetFormat(games) {
  if (games.length === 0) return [];
  
  const headers = Object.keys(games[0]);
  const rows = [headers];
  
  games.forEach(game => {
    const row = headers.map(header => game[header] || '');
    rows.push(row);
  });
  
  return rows;
}

/**
 * Update live_picks_sheets in Google Sheets
 */
async function updateLivePicksSheet(sheetsClient, spreadsheetId, games) {
  try {
    console.log('📊 Updating live_picks_sheets...');
    
    const sheetData = toSheetFormat(games);
    const numRows = sheetData.length;
    
    // Clear existing data
    try {
      await sheetsClient.spreadsheets.values.clear({
        spreadsheetId,
        range: 'live_picks_sheets!A1:ZZ10000',
      });
    } catch (clearError) {
      console.log('   Note: Could not clear existing data');
    }
    
    // Write new data
    await sheetsClient.spreadsheets.values.update({
      spreadsheetId,
      range: `live_picks_sheets!A1:ZZ${numRows}`,
      valueInputOption: 'USER_ENTERED',
      resource: { values: sheetData },
    });
    
    console.log(`   ✅ Updated live_picks_sheets with ${numRows - 1} games`);
    return { success: true, count: numRows - 1 };
    
  } catch (error) {
    console.error(`Error updating live_picks_sheets:`, error.message);
    throw error;
  }
}

/**
 * Transform game data to Firebase picks format
 */
function transformToFirebaseFormat(game) {
  const commenceTime = new Date(game.gameday);
  
  return {
    id: game.game_id,
    league: 'NFL',
    matchup: game.matchup,
    week: parseInt(game.week) || 0,
    marketType: 'spread',  // Default, can be customized
    pickDesc: `${game.matchup} - Week ${game.week}`,
    oddsAmerican: parseInt(game.home_spread_odds) || -110,
    modelConfidence: 0,  // To be filled by model
    commenceTime: admin.firestore.Timestamp.fromDate(commenceTime),
    tier: 'public',
    riskTag: 'safe',
    reasoning: 'Upcoming NFL game',
    status: 'pending',
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
    updatedAt: admin.firestore.FieldValue.serverTimestamp(),
    gameData: {
      away_team: game.away_team,
      home_team: game.home_team,
      spread_line: parseFloat(game.spread_line) || 0,
      total_line: parseFloat(game.total_line) || 0,
      away_moneyline: parseInt(game.away_moneyline) || 0,
      home_moneyline: parseInt(game.home_moneyline) || 0,
      location: game.location,
      stadium: game.stadium,
      roof: game.roof,
      surface: game.surface,
      temp: game.temp,
      wind: game.wind,
      away_qb: game.away_qb_name,
      home_qb: game.home_qb_name,
      away_coach: game.away_coach,
      home_coach: game.home_coach,
      referee: game.referee
    },
    metadata: {
      source: 'nflreadpy',
      synced_from: 'upcoming_games',
      last_synced: new Date().toISOString()
    }
  };
}

/**
 * Update Firebase picks collection
 */
async function updateFirebasePicks(db, games) {
  try {
    console.log('🔥 Updating Firebase picks collection...');
    
    const batch = db.batch();
    const picksRef = db.collection('picks');
    let count = 0;
    
    for (const game of games) {
      const pickData = transformToFirebaseFormat(game);
      const docRef = picksRef.doc(pickData.id);
      batch.set(docRef, pickData, { merge: true });
      count++;
    }
    
    await batch.commit();
    console.log(`   ✅ Updated ${count} picks in Firebase`);
    return { success: true, count };
    
  } catch (error) {
    console.error('Error updating Firebase:', error.message);
    throw error;
  }
}

/**
 * Expand sheet columns if needed
 */
async function expandSheetColumns(sheetsClient, spreadsheetId, sheetName, targetColumns) {
  try {
    const spreadsheet = await sheetsClient.spreadsheets.get({
      spreadsheetId,
    });
    
    const sheet = spreadsheet.data.sheets.find(
      s => s.properties.title === sheetName
    );
    
    if (!sheet) return;
    
    const currentColumns = sheet.properties.gridProperties.columnCount;
    
    if (currentColumns < targetColumns) {
      console.log(`   Expanding ${sheetName} from ${currentColumns} to ${targetColumns} columns...`);
      
      await sheetsClient.spreadsheets.batchUpdate({
        spreadsheetId,
        resource: {
          requests: [{
            updateSheetProperties: {
              properties: {
                sheetId: sheet.properties.sheetId,
                gridProperties: {
                  columnCount: targetColumns,
                },
              },
              fields: 'gridProperties.columnCount',
            },
          }],
        },
      });
    }
  } catch (error) {
    console.log(`   Note: Could not expand sheet: ${error.message}`);
  }
}

/**
 * Update timestamp notification
 */
async function updateTimestamp(sheetsClient, spreadsheetId) {
  try {
    console.log('🕒 Updating timestamp...');
    
    // Expand sheet to accommodate timestamp columns
    await expandSheetColumns(sheetsClient, spreadsheetId, 'live_picks_sheets', 40);
    
    const now = new Date();
    const timestamp = now.toLocaleString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
    
    const nextUpdate = new Date(now.getTime() + 60 * 60 * 1000); // +1 hour
    const nextUpdateStr = nextUpdate.toLocaleString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
    
    // Write timestamp notification in columns AH, AI, AJ (34, 35, 36)
    await sheetsClient.spreadsheets.values.update({
      spreadsheetId,
      range: `live_picks_sheets!AH1:AJ1`,
      valueInputOption: 'USER_ENTERED',
      resource: {
        values: [['Last Synced:', timestamp, `(Next: ${nextUpdateStr})`]]
      },
    });
    
    // Add status in row 2
    await sheetsClient.spreadsheets.values.update({
      spreadsheetId,
      range: `live_picks_sheets!AH2:AI2`,
      valueInputOption: 'USER_ENTERED',
      resource: {
        values: [['Sync Status:', '✅ Active (Hourly)']]
      },
    });
    
    console.log(`   ✅ Timestamp updated: ${timestamp}`);
    
  } catch (error) {
    console.log(`   Note: Could not update timestamp: ${error.message}`);
  }
}

/**
 * Main function
 */
async function main() {
  console.log('\n🔄 Syncing Upcoming Games to Live Picks\n');
  
  try {
    // Load credentials
    const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';
    const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
    
    // Initialize clients
    const sheetsClient = initializeSheetsClient(credentials);
    const db = initializeFirebase();
    
    const spreadsheetId = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
    
    // Read upcoming games
    const allGames = await readUpcomingGames(sheetsClient, spreadsheetId);
    
    if (allGames.length === 0) {
      console.log('⚠️ No games found in upcoming_games');
      return;
    }
    
    // Filter for uncompleted games
    const uncompletedGames = filterUncompletedGames(allGames);
    
    if (uncompletedGames.length === 0) {
      console.log('✅ All games are completed - nothing to sync');
      return;
    }
    
    // Transform to live picks format
    const livePicksData = transformToLivePicksFormat(uncompletedGames);
    
    // Update Google Sheets
    const sheetsResult = await updateLivePicksSheet(sheetsClient, spreadsheetId, livePicksData);
    
    // Update Firebase
    const firebaseResult = await updateFirebasePicks(db, livePicksData);
    
    // Update timestamp
    await updateTimestamp(sheetsClient, spreadsheetId);
    
    console.log('\n🎉 Sync completed successfully!');
    console.log(`📊 Synced ${sheetsResult.count} games to live_picks_sheets`);
    console.log(`🔥 Synced ${firebaseResult.count} picks to Firebase`);
    console.log('\n💡 Added columns:');
    console.log('   - matchup: "AWAY @ HOME" format');
    console.log('   - All coordinating betting odds columns');
    console.log('   - Stadium and weather information');
    console.log('   - QB and coaching information');
    
  } catch (error) {
    console.error('\n❌ Sync failed:', error.message);
  }
}

main();
