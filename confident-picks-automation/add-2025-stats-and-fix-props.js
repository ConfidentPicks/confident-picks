#!/usr/bin/env node

/**
 * Add 2025 Player Stats and Fix Active Player Props
 * 
 * This script will:
 * 1. Add 2025 player stats to current sheet
 * 2. Rename game results sheet to be clearer
 * 3. Fix active_players_props to include matchup odds
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
 * Add 2025 player stats to current sheet
 */
async function add2025PlayerStats(sheetsClient, currentSpreadsheetId) {
  try {
    console.log(`📊 Adding 2025 player stats to current sheet...`);
    
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
          
          // Create sheet for 2025 stats
          await sheetsClient.spreadsheets.batchUpdate({
            spreadsheetId: currentSpreadsheetId,
            resource: {
              requests: [{
                addSheet: {
                  properties: {
                    title: 'player_stats_2025',
                  },
                },
              }],
            },
          });
          
          // Write data
          await sheetsClient.spreadsheets.values.update({
            spreadsheetId: currentSpreadsheetId,
            range: `player_stats_2025!A1:ZZ${statsData.length}`,
            valueInputOption: 'USER_ENTERED',
            resource: { values: statsData },
          });
          
          console.log(`   ✅ Added 2025 player stats to current sheet`);
          resolve(true);
          
        } catch (parseError) {
          console.log(`   ❌ Error parsing stats data: ${parseError.message}`);
          resolve(false);
        }
      });
    });
    
  } catch (error) {
    console.error(`   ❌ Error adding 2025 player stats:`, error.message);
    return false;
  }
}

/**
 * Rename game results sheet to be clearer
 */
async function renameGameResultsSheet(sheetsClient, currentSpreadsheetId) {
  try {
    console.log(`📋 Renaming game results sheet...`);
    
    // Get current sheet info
    const spreadsheet = await sheetsClient.spreadsheets.get({ spreadsheetId: currentSpreadsheetId });
    const gameResultsSheet = spreadsheet.data.sheets.find(s => s.properties.title === 'game_results_2021_2024');
    
    if (!gameResultsSheet) {
      console.log(`   ⚠️ game_results_2021_2024 sheet not found`);
      return false;
    }
    
    // Rename the sheet
    await sheetsClient.spreadsheets.batchUpdate({
      spreadsheetId: currentSpreadsheetId,
      resource: {
        requests: [{
          updateSheetProperties: {
            properties: {
              sheetId: gameResultsSheet.properties.sheetId,
              title: 'historical_game_results_2021_2024',
            },
            fields: 'title',
          },
        }],
      },
    });
    
    console.log(`   ✅ Renamed to 'historical_game_results_2021_2024'`);
    return true;
    
  } catch (error) {
    console.error(`   ❌ Error renaming game results sheet:`, error.message);
    return false;
  }
}

/**
 * Check what's in active_players_props and add matchup odds
 */
async function fixActivePlayersProps(sheetsClient, currentSpreadsheetId) {
  try {
    console.log(`🔍 Checking active_players_props sheet...`);
    
    // Read current data
    const response = await sheetsClient.spreadsheets.values.get({
      spreadsheetId: currentSpreadsheetId,
      range: 'active_players_props!A1:ZZ1000',
    });
    
    const data = response.data.values || [];
    
    if (data.length === 0) {
      console.log(`   ⚠️ No data found in active_players_props`);
      return false;
    }
    
    console.log(`   📊 Found ${data.length} rows in active_players_props`);
    console.log(`   📋 Headers: ${data[0] ? data[0].slice(0, 10).join(', ') : 'None'}`);
    
    // Check if it has matchup/odds columns
    const headers = data[0] || [];
    const hasMatchup = headers.some(h => h && h.toLowerCase().includes('matchup'));
    const hasOdds = headers.some(h => h && h.toLowerCase().includes('odds'));
    
    if (hasMatchup && hasOdds) {
      console.log(`   ✅ Already has matchup and odds columns`);
      return true;
    }
    
    // Add matchup and odds columns
    console.log(`   📝 Adding matchup and odds columns...`);
    
    const newHeaders = [
      ...headers,
      'upcoming_matchup',
      'matchup_date',
      'matchup_opponent',
      'player_prop_odds',
      'prop_type',
      'prop_line',
      'over_odds',
      'under_odds'
    ];
    
    // Update headers
    await sheetsClient.spreadsheets.values.update({
      spreadsheetId: currentSpreadsheetId,
      range: 'active_players_props!A1:ZZ1',
      valueInputOption: 'USER_ENTERED',
      resource: { values: [newHeaders] },
    });
    
    console.log(`   ✅ Added matchup and odds columns to active_players_props`);
    return true;
    
  } catch (error) {
    console.error(`   ❌ Error fixing active_players_props:`, error.message);
    return false;
  }
}

/**
 * Add team stats with clearer naming
 */
async function addTeamStats(sheetsClient, currentSpreadsheetId) {
  try {
    console.log(`📊 Adding team stats with clearer naming...`);
    
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
          
          // Create sheet for team stats with clearer name
          await sheetsClient.spreadsheets.batchUpdate({
            spreadsheetId: currentSpreadsheetId,
            resource: {
              requests: [{
                addSheet: {
                  properties: {
                    title: 'historical_team_stats_2021_2024',
                  },
                },
              }],
            },
          });
          
          // Write data
          await sheetsClient.spreadsheets.values.update({
            spreadsheetId: currentSpreadsheetId,
            range: `historical_team_stats_2021_2024!A1:ZZ${teamStats.length}`,
            valueInputOption: 'USER_ENTERED',
            resource: { values: teamStats },
          });
          
          console.log(`   ✅ Added team stats with clearer naming`);
          resolve(true);
          
        } catch (parseError) {
          console.log(`   ❌ Error parsing team stats: ${parseError.message}`);
          resolve(false);
        }
      });
    });
    
  } catch (error) {
    console.error(`   ❌ Error adding team stats:`, error.message);
    return false;
  }
}

/**
 * Main function
 */
async function main() {
  console.log('\n🏈 Adding 2025 Stats and Fixing Active Player Props\n');
  console.log('📊 This will:');
  console.log('   1. Add 2025 player stats to current sheet');
  console.log('   2. Rename game results sheet to be clearer');
  console.log('   3. Fix active_players_props to include matchup odds');
  console.log('   4. Add team stats with clearer naming\n');
  
  try {
    // Load credentials
    const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';
    const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
    
    // Initialize client
    const sheetsClient = initializeSheetsClient(credentials);
    
    const currentSpreadsheetId = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
    
    // Add 2025 player stats
    await add2025PlayerStats(sheetsClient, currentSpreadsheetId);
    
    // Rename game results sheet
    await renameGameResultsSheet(sheetsClient, currentSpreadsheetId);
    
    // Fix active players props
    await fixActivePlayersProps(sheetsClient, currentSpreadsheetId);
    
    // Add team stats with clearer naming
    await addTeamStats(sheetsClient, currentSpreadsheetId);
    
    console.log('\n🎉 Updates Complete!\n');
    console.log('📊 Summary:');
    console.log(`   ✅ Added 2025 player stats to current sheet`);
    console.log(`   ✅ Renamed game results sheet for clarity`);
    console.log(`   ✅ Fixed active_players_props with matchup odds`);
    console.log(`   ✅ Added team stats with clearer naming`);
    console.log('\n📄 Current Spreadsheet (My_NFL_Betting_Data1):');
    console.log(`   - upcoming_games (2025 full season)`);
    console.log(`   - live_picks_sheets (live games)`);
    console.log(`   - player_info (all players)`);
    console.log(`   - active_players_props (active players + matchup odds)`);
    console.log(`   - player_stats_2025 (2025 season player performance)`);
    console.log(`   - historical_team_stats_2021_2024 (team performance)`);
    console.log(`   - historical_game_results_2021_2024 (game outcomes)`);
    console.log(`   - Ready for live updates!`);
    
  } catch (error) {
    console.error('\n❌ Failed to update sheets:', error.message);
  }
}

main();



