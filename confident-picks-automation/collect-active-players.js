#!/usr/bin/env node

/**
 * Active Players Collector - For Prop Picks
 * 
 * Collects only active NFL players with relevant information for prop betting:
 * - Current team and position
 * - Recent stats and performance
 * - Player attributes
 * - Custom columns for prop picks
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
 * Run Python script to fetch active player data
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
 * Fetch active player data
 */
async function fetchActivePlayers() {
  try {
    console.log('🔄 Fetching active NFL players...');
    
    const result = await runPythonScript('fetch_active_players.py');
    const playerData = JSON.parse(result);
    
    if (playerData.error) {
      throw new Error(playerData.error);
    }
    
    console.log(`✅ Fetched ${playerData.length} active players`);
    return playerData;
    
  } catch (error) {
    console.error('Error fetching active players:', error.message);
    throw error;
  }
}

/**
 * Convert player data to Google Sheets format with prop betting columns
 */
function playersToSheetFormat(playerData) {
  if (playerData.length === 0) return [];
  
  // Define the columns we want for prop betting (most relevant first)
  const relevantColumns = [
    'display_name',
    'latest_team',
    'position',
    'position_group',
    'jersey_number',
    'height',
    'weight',
    'years_of_experience',
    'college_name',
    'draft_year',
    'draft_round',
    'birth_date',
    'gsis_id',
    'pfr_id',
    'espn_id',
    'headshot'
  ];
  
  // Add custom columns for prop picks
  const propColumns = [
    'week',
    'opponent',
    'home_away',
    'prop_type',
    'prop_line',
    'over_odds',
    'under_odds',
    'predicted_value',
    'bet_recommendation',
    'confidence',
    'recent_avg',
    'vs_opponent_avg',
    'matchup_rating',
    'weather_impact',
    'injury_status',
    'notes'
  ];
  
  const headers = [...relevantColumns, ...propColumns];
  const rows = [headers];
  
  // Add all active players
  playerData.forEach(player => {
    const row = relevantColumns.map(col => {
      const value = player[col];
      return value !== null && value !== undefined ? String(value) : '';
    });
    
    // Add empty cells for custom prop columns (user will fill these)
    propColumns.forEach(() => row.push(''));
    
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
 * Update Google Sheet with active player data
 */
async function updateActivePlayersSheet(sheetsClient, spreadsheetId, sheetName, playerData) {
  try {
    console.log(`📊 Updating ${sheetName} with active player data...`);
    
    const sheetData = playersToSheetFormat(playerData);
    const numRows = sheetData.length;
    const numCols = sheetData[0].length;
    
    console.log(`   Data size: ${numRows} rows × ${numCols} columns`);
    console.log(`   Player data: 16 columns`);
    console.log(`   Prop pick columns: 16 columns`);
    
    // Ensure sheet exists
    await ensureSheetExists(sheetsClient, spreadsheetId, sheetName);
    
    // Try to clear existing data
    try {
      await sheetsClient.spreadsheets.values.clear({
        spreadsheetId,
        range: `${sheetName}!A1:ZZ10000`,
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
  console.log('\n🏈 Active NFL Players for Prop Picks\n');
  
  try {
    // Load credentials
    const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';
    const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
    
    // Initialize Google Sheets
    const sheetsClient = initializeSheetsClient(credentials);
    
    // Your spreadsheet ID
    const spreadsheetId = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
    
    // Fetch active player data
    const playerData = await fetchActivePlayers();
    
    if (playerData.length === 0) {
      console.log('⚠️ No active player data found');
      return;
    }
    
    // Update Google Sheet
    const result = await updateActivePlayersSheet(sheetsClient, spreadsheetId, 'active_players_props', playerData);
    
    console.log('\n🎉 Active players sheet created successfully!');
    console.log(`📊 Added ${result.rowCount - 1} active players`);
    console.log('\n💡 Your "active_players_props" sheet includes:');
    console.log('\n📋 Player Information (Columns A-P):');
    console.log('   - Name, Team, Position');
    console.log('   - Physical attributes');
    console.log('   - Experience & draft info');
    console.log('   - College & IDs');
    console.log('\n🎯 Prop Pick Columns (Columns Q-AF):');
    console.log('   - week: Week number');
    console.log('   - opponent: Opponent team');
    console.log('   - home_away: H or A');
    console.log('   - prop_type: Pass Yds, Rush Yds, Rec Yds, TDs, etc.');
    console.log('   - prop_line: Betting line');
    console.log('   - over_odds: Over odds');
    console.log('   - under_odds: Under odds');
    console.log('   - predicted_value: Your prediction');
    console.log('   - bet_recommendation: OVER/UNDER/PASS');
    console.log('   - confidence: 0-100%');
    console.log('   - recent_avg: Recent game average');
    console.log('   - vs_opponent_avg: Avg vs this opponent');
    console.log('   - matchup_rating: 1-5 stars');
    console.log('   - weather_impact: Weather notes');
    console.log('   - injury_status: Injury info');
    console.log('   - notes: Additional notes');
    
  } catch (error) {
    console.error('\n❌ Active players collection failed:', error.message);
    console.log('\n🔧 Troubleshooting:');
    console.log('1. Make sure Python is installed');
    console.log('2. Install nflreadpy: pip install nflreadpy');
    console.log('3. Check internet connection');
  }
}

main();



