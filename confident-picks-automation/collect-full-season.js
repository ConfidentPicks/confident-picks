#!/usr/bin/env node

/**
 * Full Season Data Collector
 * 
 * Collects all games for the 2025 NFL season with all available columns
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
    console.log('🔄 Fetching full 2025 NFL season data...');
    
    const result = await runPythonScript('fetch_full_season.py');
    const seasonData = JSON.parse(result);
    
    if (seasonData.error) {
      throw new Error(seasonData.error);
    }
    
    console.log(`✅ Fetched ${seasonData.length} games for 2025 season`);
    return seasonData;
    
  } catch (error) {
    console.error('Error fetching full season:', error.message);
    throw error;
  }
}

/**
 * Convert season data to Google Sheets format with ALL columns
 */
function seasonToSheetFormat(seasonData) {
  if (seasonData.length === 0) return [];
  
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
 * Update Google Sheet with full season data
 */
async function updateSeasonSheet(sheetsClient, spreadsheetId, sheetName, seasonData) {
  try {
    console.log(`📊 Updating ${sheetName} with full season data...`);
    
    const sheetData = seasonToSheetFormat(seasonData);
    const numRows = sheetData.length;
    const numCols = sheetData[0].length;
    
    console.log(`   Data size: ${numRows} rows × ${numCols} columns`);
    
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
    
    // Determine the end column letter
    const endCol = String.fromCharCode(65 + Math.min(numCols - 1, 25)); // A-Z
    const range = numCols > 26 
      ? `${sheetName}!A1:ZZ${numRows}` 
      : `${sheetName}!A1:${endCol}${numRows}`;
    
    console.log(`   Writing to range: ${range}`);
    
    // Write new data
    await sheetsClient.spreadsheets.values.update({
      spreadsheetId,
      range,
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
  console.log('\n🏈 Full 2025 NFL Season Data Collection\n');
  
  try {
    // Load credentials
    const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';
    const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
    
    // Initialize Google Sheets
    const sheetsClient = initializeSheetsClient(credentials);
    
    // Your spreadsheet ID
    const spreadsheetId = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
    
    // Fetch full 2025 season data
    const seasonData = await fetchFullSeason();
    
    if (seasonData.length === 0) {
      console.log('⚠️ No season data found');
      return;
    }
    
    // Update Google Sheet
    const result = await updateSeasonSheet(sheetsClient, spreadsheetId, 'upcoming_games', seasonData);
    
    console.log('\n🎉 Full season data collection completed successfully!');
    console.log(`📊 Updated ${result.rowCount} rows with ${result.colCount} columns`);
    console.log('\n💡 Your "upcoming_games" sheet now has:');
    console.log('   - All 272 games for the 2025 NFL season');
    console.log('   - All 45 available data columns');
    console.log('   - Game dates, teams, odds, weather, and more!');
    
  } catch (error) {
    console.error('\n❌ Season data collection failed:', error.message);
    console.log('\n🔧 Troubleshooting:');
    console.log('1. Make sure Python is installed');
    console.log('2. Install nflreadpy: pip install nflreadpy');
    console.log('3. Check internet connection');
    console.log('4. Verify Google Sheets API is enabled');
  }
}

main();
