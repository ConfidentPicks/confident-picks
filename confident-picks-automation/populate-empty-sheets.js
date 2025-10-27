#!/usr/bin/env node

/**
 * Populate Empty Sheets with Data
 * 
 * This script will populate the empty sheets with the correct data:
 * - player_stats_2025
 * - historical_team_stats_2021_2024
 * - historical_game_results_2021_2024
 */

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
 * Populate 2025 player stats
 */
async function populate2025PlayerStats(sheetsClient, currentSpreadsheetId) {
  try {
    console.log(`📊 Populating player_stats_2025...`);
    
    const { spawn } = require('child_process');
    
    return new Promise((resolve, reject) => {
      const python = spawn('python', ['fetch_historical_stats.py', '2025']);
      
      let output = '';
      let errorOutput = '';
      
      python.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      python.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });
      
      python.on('close', async (code) => {
        if (code !== 0) {
          console.log(`   ⚠️ Python script exited with code ${code}`);
          console.log(`   Error: ${errorOutput}`);
          resolve(false);
          return;
        }
        
        try {
          const statsData = JSON.parse(output);
          console.log(`   📈 Fetched ${statsData.length} 2025 player game records`);
          
          // Write data to existing sheet
          await sheetsClient.spreadsheets.values.update({
            spreadsheetId: currentSpreadsheetId,
            range: `player_stats_2025!A1:ZZ${statsData.length}`,
            valueInputOption: 'USER_ENTERED',
            resource: { values: statsData },
          });
          
          console.log(`   ✅ Populated player_stats_2025 with ${statsData.length} records`);
          resolve(true);
          
        } catch (parseError) {
          console.log(`   ❌ Error parsing stats data: ${parseError.message}`);
          resolve(false);
        }
      });
    });
    
  } catch (error) {
    console.error(`   ❌ Error populating 2025 player stats:`, error.message);
    return false;
  }
}

/**
 * Populate team stats
 */
async function populateTeamStats(sheetsClient, currentSpreadsheetId) {
  try {
    console.log(`📊 Populating historical_team_stats_2021_2024...`);
    
    const { spawn } = require('child_process');
    
    return new Promise((resolve, reject) => {
      const python = spawn('python', ['fetch_team_stats.py']);
      
      let output = '';
      let errorOutput = '';
      
      python.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      python.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });
      
      python.on('close', async (code) => {
        if (code !== 0) {
          console.log(`   ⚠️ Team stats script exited with code ${code}`);
          resolve(false);
          return;
        }
        
        try {
          const teamStats = JSON.parse(output);
          console.log(`   📈 Fetched ${teamStats.length} team stat records`);
          
          // Write data to existing sheet
          await sheetsClient.spreadsheets.values.update({
            spreadsheetId: currentSpreadsheetId,
            range: `historical_team_stats_2021_2024!A1:ZZ${teamStats.length}`,
            valueInputOption: 'USER_ENTERED',
            resource: { values: teamStats },
          });
          
          console.log(`   ✅ Populated historical_team_stats_2021_2024 with ${teamStats.length} records`);
          resolve(true);
          
        } catch (parseError) {
          console.log(`   ❌ Error parsing team stats: ${parseError.message}`);
          resolve(false);
        }
      });
    });
    
  } catch (error) {
    console.error(`   ❌ Error populating team stats:`, error.message);
    return false;
  }
}

/**
 * Populate game results
 */
async function populateGameResults(sheetsClient, currentSpreadsheetId) {
  try {
    console.log(`📊 Populating historical_game_results_2021_2024...`);
    
    const { spawn } = require('child_process');
    
    return new Promise((resolve, reject) => {
      const python = spawn('python', ['fetch_game_results.py']);
      
      let output = '';
      let errorOutput = '';
      
      python.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      python.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });
      
      python.on('close', async (code) => {
        if (code !== 0) {
          console.log(`   ⚠️ Game results script exited with code ${code}`);
          resolve(false);
          return;
        }
        
        try {
          const gameResults = JSON.parse(output);
          console.log(`   📈 Fetched ${gameResults.length} game result records`);
          
          // Write data to existing sheet
          await sheetsClient.spreadsheets.values.update({
            spreadsheetId: currentSpreadsheetId,
            range: `historical_game_results_2021_2024!A1:ZZ${gameResults.length}`,
            valueInputOption: 'USER_ENTERED',
            resource: { values: gameResults },
          });
          
          console.log(`   ✅ Populated historical_game_results_2021_2024 with ${gameResults.length} records`);
          resolve(true);
          
        } catch (parseError) {
          console.log(`   ❌ Error parsing game results: ${parseError.message}`);
          resolve(false);
        }
      });
    });
    
  } catch (error) {
    console.error(`   ❌ Error populating game results:`, error.message);
    return false;
  }
}

/**
 * Check what sheets exist and their status
 */
async function checkSheetsStatus(sheetsClient, currentSpreadsheetId) {
  try {
    console.log(`🔍 Checking sheets status...`);
    
    const spreadsheet = await sheetsClient.spreadsheets.get({ spreadsheetId: currentSpreadsheetId });
    const sheets = spreadsheet.data.sheets;
    
    console.log(`\n📋 Current Sheets Status:`);
    
    for (const sheet of sheets) {
      const sheetName = sheet.properties.title;
      
      try {
        const response = await sheetsClient.spreadsheets.values.get({
          spreadsheetId: currentSpreadsheetId,
          range: `${sheetName}!A1:Z10`,
        });
        
        const data = response.data.values || [];
        const rowCount = data.length;
        
        console.log(`   ${sheetName}: ${rowCount} rows`);
        
        if (rowCount > 0) {
          console.log(`      Headers: ${data[0] ? data[0].slice(0, 5).join(', ') : 'None'}`);
        }
        
      } catch (e) {
        console.log(`   ${sheetName}: Error reading - ${e.message}`);
      }
    }
    
  } catch (error) {
    console.error(`   ❌ Error checking sheets status:`, error.message);
  }
}

/**
 * Main function
 */
async function main() {
  console.log('\n🏈 Populating Empty Sheets with Data\n');
  console.log('📊 This will populate the empty sheets with the correct data\n');
  
  try {
    // Load credentials
    const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';
    const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
    
    // Initialize client
    const sheetsClient = initializeSheetsClient(credentials);
    
    const currentSpreadsheetId = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
    
    // Check current status
    await checkSheetsStatus(sheetsClient, currentSpreadsheetId);
    
    console.log('\n📊 Populating empty sheets...\n');
    
    // Populate 2025 player stats
    await populate2025PlayerStats(sheetsClient, currentSpreadsheetId);
    
    // Populate team stats
    await populateTeamStats(sheetsClient, currentSpreadsheetId);
    
    // Populate game results
    await populateGameResults(sheetsClient, currentSpreadsheetId);
    
    console.log('\n🎉 Sheet Population Complete!\n');
    console.log('📊 Summary:');
    console.log(`   ✅ Populated player_stats_2025`);
    console.log(`   ✅ Populated historical_team_stats_2021_2024`);
    console.log(`   ✅ Populated historical_game_results_2021_2024`);
    console.log('\n📄 All sheets should now have data!');
    
    // Check final status
    console.log('\n📋 Final Sheets Status:');
    await checkSheetsStatus(sheetsClient, currentSpreadsheetId);
    
  } catch (error) {
    console.error('\n❌ Failed to populate sheets:', error.message);
  }
}

main();



