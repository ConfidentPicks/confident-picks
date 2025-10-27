#!/usr/bin/env node

/**
 * Historical Player Stats Collector (2021-Current)
 * 
 * Collects week-by-week player statistics for model building:
 * - 2021, 2022, 2023, 2024, 2025 seasons
 * - All offensive and defensive stats by game
 * - Updates as new games complete
 */

const { spawn } = require('child_process');
const fs = require('fs');
const { google } = require('googleapis');

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
 * Run Python script to fetch player stats
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
 * Fetch historical player stats
 */
async function fetchHistoricalStats(years) {
  try {
    console.log(`🔄 Fetching player stats for ${years.join(', ')}...`);
    
    const result = await runPythonScript('fetch_historical_stats.py', years.map(String));
    const statsData = JSON.parse(result);
    
    if (statsData.error) {
      throw new Error(statsData.error);
    }
    
    console.log(`✅ Fetched ${statsData.length} player game records`);
    return statsData;
    
  } catch (error) {
    console.error('Error fetching historical stats:', error.message);
    throw error;
  }
}

/**
 * Convert stats data to Google Sheets format
 */
function statsToSheetFormat(statsData) {
  if (statsData.length === 0) return [];
  
  const headers = Object.keys(statsData[0]);
  const rows = [headers];
  
  statsData.forEach(stat => {
    const row = headers.map(header => {
      const value = stat[header];
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
    const spreadsheet = await sheetsClient.spreadsheets.get({
      spreadsheetId,
    });
    
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
 * Update Google Sheet with stats
 */
async function updateStatsSheet(sheetsClient, spreadsheetId, sheetName, statsData) {
  try {
    console.log(`📊 Updating ${sheetName}...`);
    
    const sheetData = statsToSheetFormat(statsData);
    const numRows = sheetData.length;
    const numCols = sheetData[0].length;
    
    console.log(`   Data size: ${numRows} rows × ${numCols} columns`);
    
    // Ensure sheet exists
    await ensureSheetExists(sheetsClient, spreadsheetId, sheetName);
    
    // Clear existing data
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
    
    console.log(`✅ Updated ${sheetName} with ${numRows} rows`);
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
  console.log('\n🏈 Historical Player Stats Collection (2021-Current)\n');
  console.log('📊 Collecting week-by-week player statistics for model building\n');
  
  try {
    // Load credentials
    const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';
    const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
    
    // Initialize Google Sheets
    const sheetsClient = initializeSheetsClient(credentials);
    
    const spreadsheetId = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
    
    // Fetch historical stats for 2021-2025 (one year at a time)
    const years = [2021, 2022, 2023, 2024, 2025];
    let totalRecords = 0;
    
    for (const year of years) {
      console.log(`\n📅 Processing ${year}...`);
      const statsData = await fetchHistoricalStats([year]);
      
      if (statsData.length === 0) {
        console.log(`   ⚠️ No stats found for ${year}`);
        continue;
      }
      
      // Update Google Sheet (one sheet per year)
      const sheetName = `player_stats_${year}`;
      const result = await updateStatsSheet(sheetsClient, spreadsheetId, sheetName, statsData);
      totalRecords += (result.rowCount - 1);
      
      // Small delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    console.log('\n🎉 Historical stats collection completed!');
    console.log(`📊 Collected ${totalRecords} player game records across ${years.length} years`);
    console.log('\n💡 Your sheets (player_stats_2021 through player_stats_2025) include:');
    console.log('   - Player stats by game (2021-2025)');
    console.log('   - Passing, rushing, receiving stats');
    console.log('   - Week-by-week performance');
    console.log('   - Team and opponent info');
    console.log('   - EPA and advanced metrics');
    console.log('\n🎯 Perfect for:');
    console.log('   - Building prediction models');
    console.log('   - Player performance analysis');
    console.log('   - Matchup analysis');
    console.log('   - Prop betting models');
    
  } catch (error) {
    console.error('\n❌ Historical stats collection failed:', error.message);
    console.log('\n🔧 Troubleshooting:');
    console.log('1. Make sure Python is installed');
    console.log('2. Install nflreadpy: pip install nflreadpy');
    console.log('3. Check internet connection');
  }
}

main();
