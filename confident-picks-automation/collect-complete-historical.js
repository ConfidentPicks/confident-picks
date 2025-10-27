#!/usr/bin/env node

/**
 * Complete Historical Data Collection (2021-Current)
 * 
 * Collects ALL data needed for model building:
 * 1. Player stats by game (2025 + any missing)
 * 2. Team stats by game  
 * 3. Play-by-play data (if needed)
 * 4. Game results and outcomes
 */

const { spawn } = require('child_process');
const fs = require('fs');
const { google } = require('googleapis');

function initializeSheetsClient(credentials) {
  const auth = new google.auth.GoogleAuth({
    credentials,
    scopes: ['https://www.googleapis.com/auth/spreadsheets'],
  });
  return google.sheets({ version: 'v4', auth });
}

async function runPythonScript(scriptName, args = []) {
  return new Promise((resolve, reject) => {
    const python = spawn('python', [scriptName, ...args]);
    let output = '';
    let error = '';
    
    python.stdout.on('data', (data) => output += data.toString());
    python.stderr.on('data', (data) => error += data.toString());
    python.on('close', (code) => {
      if (code === 0) resolve(output);
      else reject(new Error(`Python script failed: ${error}`));
    });
  });
}

async function ensureSheetExists(sheetsClient, spreadsheetId, sheetName) {
  try {
    const spreadsheet = await sheetsClient.spreadsheets.get({ spreadsheetId });
    const sheetExists = spreadsheet.data.sheets.some(s => s.properties.title === sheetName);
    
    if (!sheetExists) {
      console.log(`   Creating sheet: ${sheetName}`);
      await sheetsClient.spreadsheets.batchUpdate({
        spreadsheetId,
        resource: {
          requests: [{ addSheet: { properties: { title: sheetName } } }]
        },
      });
    }
  } catch (error) {
    console.log(`   Note: ${error.message}`);
  }
}

async function updateSheet(sheetsClient, spreadsheetId, sheetName, data) {
  if (data.length === 0) return { success: false };
  
  const headers = Object.keys(data[0]);
  const rows = [headers];
  data.forEach(item => {
    rows.push(headers.map(h => String(item[h] || '')));
  });
  
  console.log(`📊 Updating ${sheetName}... (${rows.length} rows)`);
  
  await ensureSheetExists(sheetsClient, spreadsheetId, sheetName);
  
  try {
    await sheetsClient.spreadsheets.values.clear({
      spreadsheetId,
      range: `${sheetName}!A1:ZZ100000`,
    });
  } catch (e) {}
  
  await sheetsClient.spreadsheets.values.update({
    spreadsheetId,
    range: `${sheetName}!A1:ZZ${rows.length}`,
    valueInputOption: 'USER_ENTERED',
    resource: { values: rows },
  });
  
  console.log(`   ✅ Updated ${sheetName} with ${rows.length - 1} records`);
  return { success: true, count: rows.length - 1 };
}

async function main() {
  console.log('\n🏈 Complete Historical Data Collection\n');
  console.log('📊 Collecting ALL data from 2021-current for model building\n');
  
  try {
    const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';
    const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
    const sheetsClient = initializeSheetsClient(credentials);
    const spreadsheetId = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
    
    const summary = {
      player_stats_2025: 0,
      team_stats: 0,
      game_results: 0
    };
    
    // 1. Add 2025 Player Stats (completed games so far)
    console.log('\n📅 1. Collecting 2025 Player Stats (completed games)...');
    const stats2025 = await runPythonScript('fetch_historical_stats.py', ['2025']);
    const statsData = JSON.parse(stats2025);
    if (!statsData.error && statsData.length > 0) {
      const result = await updateSheet(sheetsClient, spreadsheetId, 'player_stats_2025', statsData);
      summary.player_stats_2025 = result.count;
    }
    
    // 2. Collect Team Stats by Game (2021-2025)
    console.log('\n📅 2. Collecting Team Stats by Game (2021-2025)...');
    const years = [2021, 2022, 2023, 2024, 2025];
    for (const year of years) {
      const teamStats = await runPythonScript('fetch_team_stats.py', [String(year)]);
      const teamData = JSON.parse(teamStats);
      if (!teamData.error && teamData.length > 0) {
        const result = await updateSheet(sheetsClient, spreadsheetId, `team_stats_${year}`, teamData);
        summary.team_stats += result.count;
      }
      await new Promise(r => setTimeout(r, 1000));
    }
    
    // 3. Collect Game Results (completed games with scores)
    console.log('\n📅 3. Collecting Game Results (completed games 2021-2025)...');
    for (const year of years) {
      const games = await runPythonScript('fetch_game_results.py', [String(year)]);
      const gamesData = JSON.parse(games);
      if (!gamesData.error && gamesData.length > 0) {
        const result = await updateSheet(sheetsClient, spreadsheetId, `game_results_${year}`, gamesData);
        summary.game_results += result.count;
      }
      await new Promise(r => setTimeout(r, 1000));
    }
    
    console.log('\n🎉 Complete Historical Data Collection Finished!\n');
    console.log('📊 Summary:');
    console.log(`   - 2025 Player Stats: ${summary.player_stats_2025} records`);
    console.log(`   - Team Stats (2021-2025): ${summary.team_stats} records`);
    console.log(`   - Game Results (2021-2025): ${summary.game_results} games`);
    console.log('\n💡 You now have EVERYTHING for model building!');
    
  } catch (error) {
    console.error('\n❌ Collection failed:', error.message);
  }
}

main();



