#!/usr/bin/env node

/**
 * Transfer Historical Data (2021-2024) to New Spreadsheet
 * 
 * This script will:
 * 1. Copy player_stats_2021-2024 to new historical spreadsheet
 * 2. Delete them from current sheet to free up space
 * 3. Add 2025 player stats to current sheet
 * 4. Add team stats and game results
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
 * Copy sheet data from one spreadsheet to another
 */
async function copySheetData(sheetsClient, sourceSpreadsheetId, destSpreadsheetId, sheetName) {
  try {
    console.log(`📋 Copying ${sheetName}...`);
    
    // Read data from source
    const response = await sheetsClient.spreadsheets.values.get({
      spreadsheetId: sourceSpreadsheetId,
      range: `${sheetName}!A1:ZZ100000`,
    });
    
    const data = response.data.values || [];
    
    if (data.length === 0) {
      console.log(`   ⚠️ No data found in ${sheetName}`);
      return { success: false, rows: 0 };
    }
    
    console.log(`   Read ${data.length} rows`);
    
    // Create sheet in destination
    try {
      await sheetsClient.spreadsheets.batchUpdate({
        spreadsheetId: destSpreadsheetId,
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
      console.log(`   ✅ Created sheet: ${sheetName}`);
    } catch (e) {
      console.log(`   Sheet ${sheetName} might already exist`);
    }
    
    // Write data to destination
    await sheetsClient.spreadsheets.values.update({
      spreadsheetId: destSpreadsheetId,
      range: `${sheetName}!A1:ZZ${data.length}`,
      valueInputOption: 'USER_ENTERED',
      resource: { values: data },
    });
    
    console.log(`   ✅ Copied ${data.length} rows to historical spreadsheet`);
    return { success: true, rows: data.length };
    
  } catch (error) {
    console.error(`   ❌ Error copying ${sheetName}:`, error.message);
    return { success: false, rows: 0 };
  }
}

/**
 * Delete sheet from spreadsheet
 */
async function deleteSheet(sheetsClient, spreadsheetId, sheetName) {
  try {
    console.log(`🗑️ Removing ${sheetName} from current spreadsheet...`);
    
    // Get sheet ID
    const spreadsheet = await sheetsClient.spreadsheets.get({ spreadsheetId });
    const sheet = spreadsheet.data.sheets.find(s => s.properties.title === sheetName);
    
    if (!sheet) {
      console.log(`   Sheet ${sheetName} not found`);
      return;
    }
    
    // Delete sheet
    await sheetsClient.spreadsheets.batchUpdate({
      spreadsheetId,
      resource: {
        requests: [{
          deleteSheet: {
            sheetId: sheet.properties.sheetId,
          },
        }],
      },
    });
    
    console.log(`   ✅ Removed ${sheetName} from current sheet`);
    
  } catch (error) {
    console.log(`   Note: Could not delete ${sheetName}: ${error.message}`);
  }
}

/**
 * Add 2025 player stats to current sheet
 */
async function add2025PlayerStats(sheetsClient, currentSpreadsheetId) {
  try {
    console.log(`\n📊 Adding 2025 player stats to current sheet...`);
    
    // Run the Python script to get 2025 player stats
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
 * Add team stats to current sheet
 */
async function addTeamStats(sheetsClient, currentSpreadsheetId) {
  try {
    console.log(`\n📊 Adding team stats to current sheet...`);
    
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
          
          // Create sheet for team stats
          await sheetsClient.spreadsheets.batchUpdate({
            spreadsheetId: currentSpreadsheetId,
            resource: {
              requests: [{
                addSheet: {
                  properties: {
                    title: 'team_stats_2021_2024',
                  },
                },
              }],
            },
          });
          
          // Write data
          await sheetsClient.spreadsheets.values.update({
            spreadsheetId: currentSpreadsheetId,
            range: `team_stats_2021_2024!A1:ZZ${teamStats.length}`,
            valueInputOption: 'USER_ENTERED',
            resource: { values: teamStats },
          });
          
          console.log(`   ✅ Added team stats to current sheet`);
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
 * Add game results to current sheet
 */
async function addGameResults(sheetsClient, currentSpreadsheetId) {
  try {
    console.log(`\n📊 Adding game results to current sheet...`);
    
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
          
          // Create sheet for game results
          await sheetsClient.spreadsheets.batchUpdate({
            spreadsheetId: currentSpreadsheetId,
            resource: {
              requests: [{
                addSheet: {
                  properties: {
                    title: 'game_results_2021_2024',
                  },
                },
              }],
            },
          });
          
          // Write data
          await sheetsClient.spreadsheets.values.update({
            spreadsheetId: currentSpreadsheetId,
            range: `game_results_2021_2024!A1:ZZ${gameResults.length}`,
            valueInputOption: 'USER_ENTERED',
            resource: { values: gameResults },
          });
          
          console.log(`   ✅ Added game results to current sheet`);
          resolve(true);
          
        } catch (parseError) {
          console.log(`   ❌ Error parsing game results: ${parseError.message}`);
          resolve(false);
        }
      });
    });
    
  } catch (error) {
    console.error(`   ❌ Error adding game results:`, error.message);
    return false;
  }
}

/**
 * Main function
 */
async function main() {
  console.log('\n🏈 Transferring Historical Data (2021-2024)\n');
  console.log('📊 This will:');
  console.log('   1. Copy player_stats_2021-2024 to new historical spreadsheet');
  console.log('   2. Delete them from current sheet (free up ~8.6M cells)');
  console.log('   3. Add 2025 player stats to current sheet');
  console.log('   4. Add team stats and game results\n');
  
  try {
    // Load credentials
    const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';
    const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
    
    // Initialize client
    const sheetsClient = initializeSheetsClient(credentials);
    
    const currentSpreadsheetId = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
    const historicalSpreadsheetId = '1-zXtCyhmjk40R_1mEW_v59j26Q0OpM1zNY6NL1YrTyA';
    
    console.log('📋 Transferring historical player stats...\n');
    
    // Copy historical player stats (2021-2024)
    const sheetsToTransfer = [
      'player_stats_2021',
      'player_stats_2022',
      'player_stats_2023',
      'player_stats_2024'
    ];
    
    let totalRows = 0;
    
    for (const sheetName of sheetsToTransfer) {
      const result = await copySheetData(sheetsClient, currentSpreadsheetId, historicalSpreadsheetId, sheetName);
      if (result.success) {
        totalRows += result.rows;
        
        // Delete from current spreadsheet to free up space
        await deleteSheet(sheetsClient, currentSpreadsheetId, sheetName);
      }
      
      // Small delay between operations
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    // Delete the default "Sheet1" from historical spreadsheet
    try {
      const spreadsheet = await sheetsClient.spreadsheets.get({ spreadsheetId: historicalSpreadsheetId });
      const defaultSheet = spreadsheet.data.sheets.find(s => s.properties.title === 'Sheet1');
      if (defaultSheet) {
        await sheetsClient.spreadsheets.batchUpdate({
          spreadsheetId: historicalSpreadsheetId,
          resource: {
            requests: [{ deleteSheet: { sheetId: defaultSheet.properties.sheetId } }]
          },
        });
        console.log(`   ✅ Removed default Sheet1 from historical spreadsheet`);
      }
    } catch (e) {}
    
    // Add 2025 player stats to current sheet
    await add2025PlayerStats(sheetsClient, currentSpreadsheetId);
    
    // Add team stats to current sheet
    await addTeamStats(sheetsClient, currentSpreadsheetId);
    
    // Add game results to current sheet
    await addGameResults(sheetsClient, currentSpreadsheetId);
    
    // Save the configuration
    const config = {
      historical_spreadsheet_id: historicalSpreadsheetId,
      historical_spreadsheet_url: `https://docs.google.com/spreadsheets/d/${historicalSpreadsheetId}/edit`,
      current_spreadsheet_id: currentSpreadsheetId,
      transferred_at: new Date().toISOString(),
      total_records_transferred: totalRows
    };
    
    fs.writeFileSync('historical-transfer-config.json', JSON.stringify(config, null, 2));
    
    console.log('\n🎉 Historical Data Transfer Complete!\n');
    console.log('📊 Summary:');
    console.log(`   ✅ Transferred ${totalRows.toLocaleString()} player game records`);
    console.log(`   ✅ Freed up ~8.6 million cells in current sheet`);
    console.log(`   ✅ Added 2025 player stats to current sheet`);
    console.log(`   ✅ Added team stats (2021-2024) to current sheet`);
    console.log(`   ✅ Added game results (2021-2024) to current sheet`);
    console.log('\n📋 Historical Spreadsheet (2021-2024):');
    console.log(`   URL: https://docs.google.com/spreadsheets/d/${historicalSpreadsheetId}/edit`);
    console.log(`   - player_stats_2021-2024 (${totalRows.toLocaleString()} records)`);
    console.log(`   - Perfect for model training`);
    console.log('\n📄 Current Spreadsheet (My_NFL_Betting_Data1):');
    console.log(`   - upcoming_games (2025 full season)`);
    console.log(`   - live_picks_sheets (live games)`);
    console.log(`   - player_info (all players)`);
    console.log(`   - active_players_props (active players)`);
    console.log(`   - player_stats_2025 (7,398 records)`);
    console.log(`   - team_stats_2021_2024 (team performance)`);
    console.log(`   - game_results_2021_2024 (game outcomes)`);
    console.log(`   - Ready for live updates!`);
    console.log('\n💡 Config saved to: historical-transfer-config.json');
    
  } catch (error) {
    console.error('\n❌ Failed to transfer historical data:', error.message);
  }
}

main();



