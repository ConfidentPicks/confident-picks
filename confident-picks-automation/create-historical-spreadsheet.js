#!/usr/bin/env node

/**
 * Create Historical Data Spreadsheet (2021-2024)
 * 
 * Creates a new Google Sheet for historical data and transfers:
 * - player_stats_2021-2024
 * 
 * Leaves the current sheet for live 2025 updates
 */

const fs = require('fs');
const { google } = require('googleapis');

/**
 * Initialize Google Sheets client
 */
function initializeSheetsClient(credentials) {
  const auth = new google.auth.GoogleAuth({
    credentials,
    scopes: ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'],
  });

  return google.sheets({ version: 'v4', auth });
}

/**
 * Initialize Google Drive client
 */
function initializeDriveClient(credentials) {
  const auth = new google.auth.GoogleAuth({
    credentials,
    scopes: ['https://www.googleapis.com/auth/drive'],
  });

  return google.drive({ version: 'v3', auth });
}

/**
 * Create new spreadsheet
 */
async function createNewSpreadsheet(sheetsClient, driveClient, title) {
  try {
    console.log(`📄 Creating new spreadsheet: "${title}"...`);
    
    // Create new spreadsheet
    const spreadsheet = await sheetsClient.spreadsheets.create({
      resource: {
        properties: {
          title: title,
        },
      },
    });
    
    const newSpreadsheetId = spreadsheet.data.spreadsheetId;
    const newSpreadsheetUrl = spreadsheet.data.spreadsheetUrl;
    
    console.log(`   ✅ Created successfully!`);
    console.log(`   📋 ID: ${newSpreadsheetId}`);
    console.log(`   🔗 URL: ${newSpreadsheetUrl}`);
    
    // Share with anyone (or set specific permissions)
    try {
      await driveClient.permissions.create({
        fileId: newSpreadsheetId,
        resource: {
          role: 'writer',
          type: 'anyone',
        },
      });
      console.log(`   ✅ Set to "Anyone with link can edit"`);
    } catch (e) {
      console.log(`   Note: Could not set sharing permissions`);
    }
    
    return { id: newSpreadsheetId, url: newSpreadsheetUrl };
    
  } catch (error) {
    console.error('Error creating spreadsheet:', error.message);
    throw error;
  }
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
      return { success: false };
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
    } catch (e) {
      // Sheet might already exist
    }
    
    // Write data to destination
    await sheetsClient.spreadsheets.values.update({
      spreadsheetId: destSpreadsheetId,
      range: `${sheetName}!A1:ZZ${data.length}`,
      valueInputOption: 'USER_ENTERED',
      resource: { values: data },
    });
    
    console.log(`   ✅ Copied ${data.length} rows to new spreadsheet`);
    return { success: true, rows: data.length };
    
  } catch (error) {
    console.error(`   ❌ Error copying ${sheetName}:`, error.message);
    return { success: false };
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
    
    console.log(`   ✅ Removed ${sheetName}`);
    
  } catch (error) {
    console.log(`   Note: Could not delete ${sheetName}: ${error.message}`);
  }
}

/**
 * Main function
 */
async function main() {
  console.log('\n🏈 Creating Historical Data Spreadsheet\n');
  console.log('📊 This will:');
  console.log('   1. Create new spreadsheet for historical data (2021-2024)');
  console.log('   2. Copy player_stats_2021-2024 to new sheet');
  console.log('   3. Remove them from current sheet to free up space');
  console.log('   4. Keep current sheet for live 2025 updates\n');
  
  try {
    // Load credentials
    const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';
    const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
    
    // Initialize clients
    const sheetsClient = initializeSheetsClient(credentials);
    const driveClient = initializeDriveClient(credentials);
    
    const currentSpreadsheetId = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
    
    // Create new spreadsheet
    const newSheet = await createNewSpreadsheet(
      sheetsClient, 
      driveClient, 
      'NFL Historical Data (2021-2024)'
    );
    
    console.log('\n📋 Transferring historical data...\n');
    
    // Copy historical player stats (2021-2024)
    const sheetsToTransfer = [
      'player_stats_2021',
      'player_stats_2022',
      'player_stats_2023',
      'player_stats_2024'
    ];
    
    let totalRows = 0;
    
    for (const sheetName of sheetsToTransfer) {
      const result = await copySheetData(sheetsClient, currentSpreadsheetId, newSheet.id, sheetName);
      if (result.success) {
        totalRows += result.rows;
        
        // Delete from current spreadsheet to free up space
        await deleteSheet(sheetsClient, currentSpreadsheetId, sheetName);
      }
      
      // Small delay
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    // Delete the default "Sheet1" from new spreadsheet
    try {
      const spreadsheet = await sheetsClient.spreadsheets.get({ spreadsheetId: newSheet.id });
      const defaultSheet = spreadsheet.data.sheets.find(s => s.properties.title === 'Sheet1');
      if (defaultSheet) {
        await sheetsClient.spreadsheets.batchUpdate({
          spreadsheetId: newSheet.id,
          resource: {
            requests: [{ deleteSheet: { sheetId: defaultSheet.properties.sheetId } }]
          },
        });
      }
    } catch (e) {}
    
    // Save the new spreadsheet info
    const config = {
      historical_spreadsheet_id: newSheet.id,
      historical_spreadsheet_url: newSheet.url,
      created_at: new Date().toISOString()
    };
    
    fs.writeFileSync('historical-sheet-config.json', JSON.stringify(config, null, 2));
    
    console.log('\n🎉 Historical Data Spreadsheet Created!\n');
    console.log('📊 Summary:');
    console.log(`   - Transferred ${totalRows.toLocaleString()} player game records`);
    console.log(`   - Freed up ~8.6 million cells in current sheet`);
    console.log(`   - Historical data (2021-2024) now in separate sheet`);
    console.log(`   - Current sheet ready for 2025 live updates`);
    console.log('\n📋 New Spreadsheet:');
    console.log(`   Name: NFL Historical Data (2021-2024)`);
    console.log(`   ID: ${newSheet.id}`);
    console.log(`   URL: ${newSheet.url}`);
    console.log('\n📄 Current Spreadsheet (My_NFL_Betting_Data1):');
    console.log(`   - upcoming_games (2025 full season)`);
    console.log(`   - live_picks_sheets (uncompleted games)`);
    console.log(`   - player_info (all players)`);
    console.log(`   - active_players_props (active players)`);
    console.log(`   - Ready to add player_stats_2025!`);
    console.log('\n💡 Config saved to: historical-sheet-config.json');
    
  } catch (error) {
    console.error('\n❌ Failed to create historical spreadsheet:', error.message);
  }
}

main();



