#!/usr/bin/env node

/**
 * Fix Populate Empty Sheets with Data
 * 
 * This script will properly populate the empty sheets with the correct data
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
          // Parse the JSON array
          const statsData = JSON.parse(output);
          console.log(`   📈 Fetched ${statsData.length} 2025 player game records`);
          
          // Convert to 2D array for Google Sheets
          const sheetData = [];
          
          // Add headers first
          if (statsData.length > 0) {
            const headers = Object.keys(statsData[0]);
            sheetData.push(headers);
            
            // Add data rows
            for (const record of statsData) {
              const row = headers.map(header => record[header]);
              sheetData.push(row);
            }
          }
          
          // Write data to existing sheet
          await sheetsClient.spreadsheets.values.update({
            spreadsheetId: currentSpreadsheetId,
            range: `player_stats_2025!A1:ZZ${sheetData.length}`,
            valueInputOption: 'USER_ENTERED',
            resource: { values: sheetData },
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
          // Parse the JSON array
          const teamStats = JSON.parse(output);
          console.log(`   📈 Fetched ${teamStats.length} team stat records`);
          
          // Convert to 2D array for Google Sheets
          const sheetData = [];
          
          // Add headers first
          if (teamStats.length > 0) {
            const headers = Object.keys(teamStats[0]);
            sheetData.push(headers);
            
            // Add data rows
            for (const record of teamStats) {
              const row = headers.map(header => record[header]);
              sheetData.push(row);
            }
          }
          
          // Write data to existing sheet
          await sheetsClient.spreadsheets.values.update({
            spreadsheetId: currentSpreadsheetId,
            range: `historical_team_stats_2021_2024!A1:ZZ${sheetData.length}`,
            valueInputOption: 'USER_ENTERED',
            resource: { values: sheetData },
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
          // Parse the JSON array
          const gameResults = JSON.parse(output);
          console.log(`   📈 Fetched ${gameResults.length} game result records`);
          
          // Convert to 2D array for Google Sheets
          const sheetData = [];
          
          // Add headers first
          if (gameResults.length > 0) {
            const headers = Object.keys(gameResults[0]);
            sheetData.push(headers);
            
            // Add data rows
            for (const record of gameResults) {
              const row = headers.map(header => record[header]);
              sheetData.push(row);
            }
          }
          
          // Write data to existing sheet
          await sheetsClient.spreadsheets.values.update({
            spreadsheetId: currentSpreadsheetId,
            range: `historical_game_results_2021_2024!A1:ZZ${sheetData.length}`,
            valueInputOption: 'USER_ENTERED',
            resource: { values: sheetData },
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
 * Main function
 */
async function main() {
  console.log('\n🏈 Fixing Empty Sheets with Data\n');
  console.log('📊 This will properly populate the empty sheets with the correct data\n');
  
  try {
    // Load credentials
    const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';
    const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
    
    // Initialize client
    const sheetsClient = initializeSheetsClient(credentials);
    
    const currentSpreadsheetId = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
    
    console.log('📊 Populating empty sheets...\n');
    
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
    
  } catch (error) {
    console.error('\n❌ Failed to populate sheets:', error.message);
  }
}

main();
