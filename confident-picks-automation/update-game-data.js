#!/usr/bin/env node

/**
 * Selective Game Data Updater
 * 
 * Updates only dynamic columns that change frequently:
 * - Betting odds (spreads, totals, moneylines)
 * - Game results (scores, outcomes)
 * - Weather conditions
 * - Roster changes (QBs)
 * 
 * Preserves all custom columns you add!
 */

const { spawn } = require('child_process');
const fs = require('fs');
const { google } = require('googleapis');

/**
 * Columns to update (by index and name)
 */
const COLUMNS_TO_UPDATE = {
  // Betting Odds
  'away_moneyline': 24,
  'home_moneyline': 25,
  'spread_line': 26,
  'away_spread_odds': 27,
  'home_spread_odds': 28,
  'total_line': 29,
  'under_odds': 30,
  'over_odds': 31,
  // Game Results
  'away_score': 8,
  'home_score': 10,
  'result': 12,
  'total': 13,
  'overtime': 14,
  // Weather
  'temp': 35,
  'wind': 36,
  // Roster
  'away_qb_id': 37,
  'home_qb_id': 38,
  'away_qb_name': 39,
  'home_qb_name': 40,
};

/**
 * Initialize Google Sheets client
 */
function initializeSheetsClient(credentials) {
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
    scopes: ['https://www.googleapis.com/auth/spreadsheets'],
  });

  return google.sheets({ version: 'v4', auth });
}

/**
 * Run Python script to fetch full season data
 */
async function runPythonScript(scriptName, args = []) {
  return new Promise((resolve, reject) => {
    const python = spawn('python', [scriptName, ...args]);
    
    let output = '';
    let error = '';
    
    python.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    python.stderr.on('data', (data) => {
      error += data.toString();
    });
    
    python.on('close', (code) => {
      if (code === 0) {
        resolve(output);
      } else {
        reject(new Error(`Python script failed with code ${code}: ${error}`));
      }
    });
  });
}

/**
 * Fetch full 2025 season data
 */
async function fetchFullSeason() {
  try {
    console.log('🔄 Fetching latest NFL data...');
    
    const result = await runPythonScript('fetch_full_season.py');
    const seasonData = JSON.parse(result);
    
    if (seasonData.error) {
      throw new Error(seasonData.error);
    }
    
    console.log(`✅ Fetched ${seasonData.length} games`);
    return seasonData;
    
  } catch (error) {
    console.error('Error fetching season data:', error.message);
    throw error;
  }
}

/**
 * Get column letter from index (0=A, 1=B, etc.)
 */
function getColumnLetter(index) {
  let letter = '';
  while (index >= 0) {
    letter = String.fromCharCode((index % 26) + 65) + letter;
    index = Math.floor(index / 26) - 1;
  }
  return letter;
}

/**
 * Read existing sheet data
 */
async function readExistingSheet(sheetsClient, spreadsheetId, sheetName) {
  try {
    console.log('📖 Reading existing sheet data...');
    
    const response = await sheetsClient.spreadsheets.values.get({
      spreadsheetId,
      range: `${sheetName}!A1:ZZ10000`,
    });
    
    const existingData = response.data.values || [];
    console.log(`   Found ${existingData.length} existing rows`);
    
    return existingData;
    
  } catch (error) {
    console.log('   No existing data found');
    return [];
  }
}

/**
 * Update only specific columns while preserving others
 */
async function updateSelectiveColumns(sheetsClient, spreadsheetId, sheetName, newData, existingData) {
  try {
    console.log(`📊 Updating dynamic columns in ${sheetName}...`);
    
    // If no existing data, do full write
    if (existingData.length === 0) {
      console.log('   No existing data - performing full write');
      return await performFullWrite(sheetsClient, spreadsheetId, sheetName, newData);
    }
    
    // Get headers from new data
    const headers = Object.keys(newData[0]);
    
    // Create a map of game_id to row index in existing data
    const existingGameMap = new Map();
    for (let i = 1; i < existingData.length; i++) {
      const gameId = existingData[i][0]; // game_id is first column
      if (gameId) {
        existingGameMap.set(gameId, i);
      }
    }
    
    // Prepare batch update requests
    const updateRequests = [];
    let updatedCount = 0;
    
    for (const game of newData) {
      const gameId = game.game_id;
      const existingRowIndex = existingGameMap.get(gameId);
      
      if (existingRowIndex === undefined) {
        console.log(`   New game found: ${gameId}`);
        continue; // Skip new games for now (they'll be added in full update)
      }
      
      // Update only the dynamic columns
      for (const [columnName, columnIndex] of Object.entries(COLUMNS_TO_UPDATE)) {
        const newValue = game[columnName];
        const columnLetter = getColumnLetter(columnIndex);
        const cellRange = `${sheetName}!${columnLetter}${existingRowIndex + 1}`;
        
        updateRequests.push({
          range: cellRange,
          values: [[newValue !== null && newValue !== undefined ? String(newValue) : '']],
        });
      }
      
      updatedCount++;
    }
    
    // Execute batch update
    if (updateRequests.length > 0) {
      console.log(`   Updating ${updateRequests.length} cells across ${updatedCount} games...`);
      
      await sheetsClient.spreadsheets.values.batchUpdate({
        spreadsheetId,
        resource: {
          valueInputOption: 'USER_ENTERED',
          data: updateRequests,
        },
      });
      
      console.log(`✅ Updated ${updatedCount} games successfully`);
    } else {
      console.log('   No updates needed');
    }
    
    return { success: true, updatedCount, cellsUpdated: updateRequests.length };
    
  } catch (error) {
    console.error(`Error updating columns:`, error.message);
    throw error;
  }
}

/**
 * Perform full write (for initial setup)
 */
async function performFullWrite(sheetsClient, spreadsheetId, sheetName, seasonData) {
  console.log('   Performing full data write...');
  
  // Get all keys from first game as headers
  const headers = Object.keys(seasonData[0]);
  const rows = [headers];
  
  // Add all games
  seasonData.forEach(game => {
    const row = headers.map(header => {
      const value = game[header];
      return value !== null && value !== undefined ? String(value) : '';
    });
    rows.push(row);
  });
  
  const numRows = rows.length;
  const numCols = rows[0].length;
  
  await sheetsClient.spreadsheets.values.update({
    spreadsheetId,
    range: `${sheetName}!A1:ZZ${numRows}`,
    valueInputOption: 'USER_ENTERED',
    resource: { values: rows },
  });
  
  return { success: true, updatedCount: numRows - 1, cellsUpdated: numRows * numCols };
}

/**
 * Expand sheet to accommodate more columns
 */
async function expandSheetColumns(sheetsClient, spreadsheetId, sheetName, targetColumns) {
  try {
    // Get spreadsheet metadata
    const spreadsheet = await sheetsClient.spreadsheets.get({
      spreadsheetId,
    });
    
    // Find the sheet
    const sheet = spreadsheet.data.sheets.find(
      s => s.properties.title === sheetName
    );
    
    if (!sheet) {
      console.log(`   Sheet ${sheetName} not found`);
      return;
    }
    
    const currentColumns = sheet.properties.gridProperties.columnCount;
    
    if (currentColumns < targetColumns) {
      console.log(`   Expanding sheet from ${currentColumns} to ${targetColumns} columns...`);
      
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
      
      console.log(`   ✅ Sheet expanded successfully`);
    }
  } catch (error) {
    console.log(`   Note: Could not expand sheet: ${error.message}`);
  }
}

/**
 * Add custom column headers if they don't exist
 */
async function addCustomColumnHeaders(sheetsClient, spreadsheetId, sheetName) {
  try {
    console.log('📝 Checking for custom column headers...');
    
    // Custom columns to add (starting after column AT = column 46)
    const customColumns = [
      'predicted_winner',
      'confidence_score',
      'predicted_spread',
      'predicted_total',
      'edge_vs_line',
      'line_movement',
      'sharp_money',
      'public_percentage',
      'value_rating'
    ];
    
    const startCol = 46; // Column AU (after AT which is column 45)
    const targetColumns = startCol + customColumns.length + 10; // Add some buffer
    
    // Expand sheet if needed
    await expandSheetColumns(sheetsClient, spreadsheetId, sheetName, targetColumns);
    
    // Read first row (headers)
    const response = await sheetsClient.spreadsheets.values.get({
      spreadsheetId,
      range: `${sheetName}!1:1`,
    });
    
    const existingHeaders = response.data.values ? response.data.values[0] : [];
    
    // Check if custom columns already exist
    let needsUpdate = false;
    const headersToAdd = [];
    
    for (let i = 0; i < customColumns.length; i++) {
      const colIndex = startCol + i;
      if (!existingHeaders[colIndex] || existingHeaders[colIndex] !== customColumns[i]) {
        needsUpdate = true;
        headersToAdd.push(customColumns[i]);
      }
    }
    
    if (needsUpdate && headersToAdd.length > 0) {
      console.log(`   Adding ${headersToAdd.length} custom column headers...`);
      
      const startColLetter = getColumnLetter(startCol);
      const endColLetter = getColumnLetter(startCol + customColumns.length - 1);
      
      await sheetsClient.spreadsheets.values.update({
        spreadsheetId,
        range: `${sheetName}!${startColLetter}1:${endColLetter}1`,
        valueInputOption: 'USER_ENTERED',
        resource: { values: [customColumns] },
      });
      
      console.log(`   ✅ Added custom columns: ${customColumns.join(', ')}`);
    } else {
      console.log('   ✅ Custom columns already exist');
    }
    
  } catch (error) {
    console.log(`   Note: Could not add custom headers: ${error.message}`);
  }
}

/**
 * Update timestamp notification in the sheet
 */
async function updateTimestamp(sheetsClient, spreadsheetId, sheetName) {
  try {
    console.log('🕒 Updating timestamp notification...');
    
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
    
    // Add timestamp in safe area: Column BX (after all prediction columns)
    // Moved from BD/BE to avoid overwriting prediction columns
    const timestampLabel = 'Last Updated:';
    const timestampValue = timestamp;
    const nextUpdate = new Date(now.getTime() + 60 * 60 * 1000); // +1 hour
    const nextUpdateStr = nextUpdate.toLocaleString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
    
    // Write timestamp notification in safe area (BX-BZ)
    await sheetsClient.spreadsheets.values.update({
      spreadsheetId,
      range: `${sheetName}!BX1:BZ1`,
      valueInputOption: 'USER_ENTERED',
      resource: {
        values: [[timestampLabel, timestampValue, `(Next: ${nextUpdateStr})`]]
      },
    });
    
    // Also update a status message in BX2
    await sheetsClient.spreadsheets.values.update({
      spreadsheetId,
      range: `${sheetName}!BX2:BY2`,
      valueInputOption: 'USER_ENTERED',
      resource: {
        values: [['Auto-Update Status:', '✅ Active (Hourly)']]
      },
    });
    
    console.log(`   ✅ Timestamp updated: ${timestamp}`);
    console.log(`   📅 Next update: ${nextUpdateStr}`);
    
  } catch (error) {
    console.log(`   Note: Could not update timestamp: ${error.message}`);
  }
}

/**
 * Sync uncompleted games to live picks
 */
async function syncUncompletedGames(sheetsClient, spreadsheetId) {
  try {
    console.log('\n🔄 Syncing uncompleted games to live picks...');
    
    // Run the sync script
    const { spawn } = require('child_process');
    return new Promise((resolve, reject) => {
      const sync = spawn('node', ['sync-upcoming-to-live.js']);
      
      let output = '';
      
      sync.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      sync.on('close', (code) => {
        if (code === 0) {
          console.log('   ✅ Live picks sync completed');
          resolve();
        } else {
          console.log('   ⚠️ Live picks sync had issues');
          resolve(); // Don't fail the whole update
        }
      });
    });
  } catch (error) {
    console.log(`   Note: Could not sync live picks: ${error.message}`);
  }
}

/**
 * Main function
 */
async function main() {
  console.log('\n🏈 Hourly NFL Data Update (Selective Columns)\n');
  console.log('⏰ Updating only dynamic data (odds, scores, weather, rosters)');
  console.log('✅ Preserving all your custom columns\n');
  
  try {
    // Load credentials
    const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';
    const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
    
    // Initialize Google Sheets
    const sheetsClient = initializeSheetsClient(credentials);
    
    // Your spreadsheet ID
    const spreadsheetId = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
    const sheetName = 'upcoming_games';
    
    // Fetch latest NFL data
    const seasonData = await fetchFullSeason();
    
    if (seasonData.length === 0) {
      console.log('⚠️ No season data found');
      return;
    }
    
    // Read existing sheet data
    const existingData = await readExistingSheet(sheetsClient, spreadsheetId, sheetName);
    
    // Update only dynamic columns
    const result = await updateSelectiveColumns(sheetsClient, spreadsheetId, sheetName, seasonData, existingData);
    
    // DO NOT update column headers - user manages these manually
    // await addCustomColumnHeaders(sheetsClient, spreadsheetId, sheetName);
    
    // Update timestamp notification
    await updateTimestamp(sheetsClient, spreadsheetId, sheetName);
    
    // Sync uncompleted games to live_picks_sheets and Firebase
    await syncUncompletedGames(sheetsClient, spreadsheetId);
    
    console.log('\n🎉 Hourly update completed successfully!');
    console.log(`📊 Updated ${result.updatedCount} games (${result.cellsUpdated} cells)`);
    console.log(`⏰ Next update in 1 hour`);
    console.log('\n💡 Updated columns:');
    console.log('   - Betting odds (spreads, totals, moneylines)');
    console.log('   - Game results (scores, outcomes)');
    console.log('   - Weather conditions (temp, wind)');
    console.log('   - Roster changes (QBs)');
    console.log('\n✅ Your custom columns are preserved!');
    
  } catch (error) {
    console.error('\n❌ Hourly update failed:', error.message);
  }
}

main();
