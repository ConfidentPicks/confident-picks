#!/usr/bin/env node

/**
 * Player Data Collector
 * 
 * Collects comprehensive NFL player information including:
 * - Player names, positions, teams
 * - Physical attributes (height, weight)
 * - Draft information
 * - College information
 * - Career stats
 * - Status (active, inactive, etc.)
 */

const { spawn } = require('child_process');
const fs = require('fs');
const { google } = require('googleapis');

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
 * Run Python script to fetch player data
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
 * Fetch player data
 */
async function fetchPlayerData() {
  try {
    console.log('🔄 Fetching NFL player data...');
    
    const result = await runPythonScript('fetch_player_data.py');
    const playerData = JSON.parse(result);
    
    if (playerData.error) {
      throw new Error(playerData.error);
    }
    
    console.log(`✅ Fetched ${playerData.length} players`);
    return playerData;
    
  } catch (error) {
    console.error('Error fetching player data:', error.message);
    throw error;
  }
}

/**
 * Convert player data to Google Sheets format
 */
function playersToSheetFormat(playerData) {
  if (playerData.length === 0) return [];
  
  // Get all keys from first player as headers
  const headers = Object.keys(playerData[0]);
  const rows = [headers];
  
  // Add all players
  playerData.forEach(player => {
    const row = headers.map(header => {
      const value = player[header];
      return value !== null && value !== undefined ? String(value) : '';
    });
    rows.push(row);
  });
  
  return rows;
}

/**
 * Create sheet tab if it doesn't exist
 */
async function ensureSheetExists(sheetsClient, spreadsheetId, sheetName) {
  try {
    // Get spreadsheet metadata
    const spreadsheet = await sheetsClient.spreadsheets.get({
      spreadsheetId,
    });
    
    // Check if sheet exists
    const sheetExists = spreadsheet.data.sheets.some(
      sheet => sheet.properties.title === sheetName
    );
    
    if (!sheetExists) {
      console.log(`   Creating new sheet: ${sheetName}`);
      await sheetsClient.spreadsheets.batchUpdate({
        spreadsheetId,
        resource: {
          requests: [{
            addSheet: {
              properties: {
                title: sheetName,
              },
            },
          }],
        },
      });
      console.log(`   ✅ Sheet created successfully`);
    }
  } catch (error) {
    console.log(`   Note: Could not verify/create sheet: ${error.message}`);
  }
}

/**
 * Update Google Sheet with player data
 */
async function updatePlayerSheet(sheetsClient, spreadsheetId, sheetName, playerData) {
  try {
    console.log(`📊 Updating ${sheetName} with player data...`);
    
    const sheetData = playersToSheetFormat(playerData);
    const numRows = sheetData.length;
    const numCols = sheetData[0].length;
    
    console.log(`   Data size: ${numRows} rows × ${numCols} columns`);
    
    // Ensure sheet exists
    await ensureSheetExists(sheetsClient, spreadsheetId, sheetName);
    
    // Try to clear existing data
    try {
      await sheetsClient.spreadsheets.values.clear({
        spreadsheetId,
        range: `${sheetName}!A1:ZZ100000`,
      });
    } catch (clearError) {
      console.log(`   Note: Could not clear existing data`);
    }
    
    console.log(`   Writing to range: ${sheetName}!A1:ZZ${numRows}`);
    
    // Write new data
    await sheetsClient.spreadsheets.values.update({
      spreadsheetId,
      range: `${sheetName}!A1:ZZ${numRows}`,
      valueInputOption: 'USER_ENTERED',
      resource: { values: sheetData },
    });
    
    console.log(`✅ Updated ${sheetName} with ${numRows} rows and ${numCols} columns`);
    return { success: true, rowCount: numRows, colCount: numCols };
    
  } catch (error) {
    console.error(`Error updating ${sheetName}:`, error.message);
    throw error;
  }
}

/**
 * Main function
 */
async function main() {
  console.log('\n🏈 NFL Player Data Collection\n');
  
  try {
    // Load credentials
    const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';
    const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
    
    // Initialize Google Sheets
    const sheetsClient = initializeSheetsClient(credentials);
    
    // Your spreadsheet ID
    const spreadsheetId = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
    
    // Fetch player data
    const playerData = await fetchPlayerData();
    
    if (playerData.length === 0) {
      console.log('⚠️ No player data found');
      return;
    }
    
    // Update Google Sheet
    const result = await updatePlayerSheet(sheetsClient, spreadsheetId, 'player_info', playerData);
    
    console.log('\n🎉 Player data collection completed successfully!');
    console.log(`📊 Updated ${result.rowCount} rows with ${result.colCount} columns`);
    console.log('\n💡 Your "player_info" sheet now has:');
    console.log('   - All NFL players (active and historical)');
    console.log('   - Names, positions, teams');
    console.log('   - Physical attributes (height, weight)');
    console.log('   - Draft information');
    console.log('   - College information');
    console.log('   - Career status and experience');
    
  } catch (error) {
    console.error('\n❌ Player data collection failed:', error.message);
    console.log('\n🔧 Troubleshooting:');
    console.log('1. Make sure Python is installed');
    console.log('2. Install nflreadpy: pip install nflreadpy');
    console.log('3. Check internet connection');
    console.log('4. Verify Google Sheets API is enabled');
  }
}

main();



