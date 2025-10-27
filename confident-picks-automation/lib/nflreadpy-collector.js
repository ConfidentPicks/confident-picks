/**
 * NFLReadPy Data Collector - Uses Python nflreadpy for NFL data
 * 
 * This script uses nflreadpy to fetch live odds and historical NFL data
 * Much better than external APIs since it's specifically designed for NFL
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
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
 * Run Python script to fetch data using nflreadpy
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
 * Fetch live odds using nflreadpy
 */
async function fetchLiveOdds() {
  try {
    console.log('🔄 Fetching live odds using nflreadpy...');
    
    const result = await runPythonScript('fetch_live_odds_simple.py');
    const oddsData = JSON.parse(result);
    
    // Check if the response contains an error
    if (oddsData.error) {
      throw new Error(oddsData.error);
    }
    
    console.log(`✅ Fetched odds for ${oddsData.length} games`);
    return oddsData;
    
  } catch (error) {
    console.error('Error fetching live odds:', error.message);
    return [];
  }
}

/**
 * Fetch historical NFL data using nflreadpy
 */
async function fetchHistoricalData(years = [2021, 2022, 2023, 2024]) {
  try {
    console.log(`🔄 Fetching historical NFL data for years: ${years.join(', ')}...`);
    
    const result = await runPythonScript('fetch_historical_data.py', years.map(String));
    const historicalData = JSON.parse(result);
    
    console.log(`✅ Fetched historical data for ${historicalData.length} years`);
    return historicalData;
    
  } catch (error) {
    console.error('Error fetching historical data:', error.message);
    return [];
  }
}

/**
 * Convert odds data to Google Sheets format
 */
function oddsToSheetFormat(oddsData) {
  const headers = [
    'Game ID',
    'Home Team',
    'Away Team',
    'Game Date',
    'Home Score',
    'Away Score',
    'Spread',
    'Spread Odds',
    'Total',
    'Total Odds',
    'Home Moneyline',
    'Away Moneyline',
    'Last Updated'
  ];

  const rows = [headers];

  oddsData.forEach(game => {
    const row = [
      game.game_id || '',
      game.home_team || '',
      game.away_team || '',
      game.game_date || '',
      game.home_score || '',
      game.away_score || '',
      game.spread || '',
      game.spread_odds || '',
      game.total || '',
      game.total_odds || '',
      game.home_moneyline || '',
      game.away_moneyline || '',
      new Date().toISOString()
    ];
    
    rows.push(row);
  });

  return rows;
}

/**
 * Convert historical data to Google Sheets format
 */
function historicalDataToSheetFormat(historicalData, dataType) {
  if (dataType === 'games') {
    const headers = [
      'Game ID',
      'Season',
      'Week',
      'Game Date',
      'Home Team',
      'Away Team',
      'Home Score',
      'Away Score',
      'Spread',
      'Total',
      'Home Moneyline',
      'Away Moneyline',
      'Home Yards',
      'Away Yards',
      'Home Turnovers',
      'Away Turnovers'
    ];

    const rows = [headers];

    historicalData.forEach(game => {
      const row = [
        game.game_id || '',
        game.season || '',
        game.week || '',
        game.game_date || '',
        game.home_team || '',
        game.away_team || '',
        game.home_score || '',
        game.away_score || '',
        game.spread || '',
        game.total || '',
        game.home_moneyline || '',
        game.away_moneyline || '',
        game.home_yards || '',
        game.away_yards || '',
        game.home_turnovers || '',
        game.away_turnovers || ''
      ];
      
      rows.push(row);
    });

    return rows;
  } else if (dataType === 'team_stats') {
    const headers = [
      'Team',
      'Season',
      'Games',
      'Wins',
      'Losses',
      'Ties',
      'Points For',
      'Points Against',
      'Passing Yards',
      'Rushing Yards',
      'Total Yards',
      'Passing Touchdowns',
      'Rushing Touchdowns',
      'Total Touchdowns',
      'Interceptions',
      'Fumbles',
      'Sacks',
      'Turnovers'
    ];

    const rows = [headers];

    historicalData.forEach(team => {
      const row = [
        team.team || '',
        team.season || '',
        team.games || '',
        team.wins || '',
        team.losses || '',
        team.ties || '',
        team.points_for || '',
        team.points_against || '',
        team.passing_yards || '',
        team.rushing_yards || '',
        team.total_yards || '',
        team.passing_touchdowns || '',
        team.rushing_touchdowns || '',
        team.total_touchdowns || '',
        team.interceptions || '',
        team.fumbles || '',
        team.sacks || '',
        team.turnovers || ''
      ];
      
      rows.push(row);
    });

    return rows;
  }

  return [];
}

/**
 * Update Google Sheet with data
 */
async function updateSheet(sheetsClient, spreadsheetId, sheetName, data, dataType) {
  try {
    console.log(`📊 Updating ${sheetName} with ${dataType} data...`);
    
    let sheetData;
    if (dataType === 'odds') {
      sheetData = oddsToSheetFormat(data);
    } else if (dataType === 'games') {
      sheetData = historicalDataToSheetFormat(data, 'games');
    } else if (dataType === 'team_stats') {
      sheetData = historicalDataToSheetFormat(data, 'team_stats');
    } else {
      throw new Error(`Unknown data type: ${dataType}`);
    }
    
    const numRows = sheetData.length;
    
    // Try to clear existing data (skip if sheet doesn't exist)
    try {
      await sheetsClient.spreadsheets.values.clear({
        spreadsheetId,
        range: `${sheetName}!A1:Z10000`,
      });
    } catch (clearError) {
      console.log(`   Note: Could not clear sheet (might not exist yet)`);
    }
    
    // Write new data
    await sheetsClient.spreadsheets.values.update({
      spreadsheetId,
      range: `${sheetName}!A1:Z${numRows}`,
      valueInputOption: 'USER_ENTERED',
      resource: { values: sheetData },
    });
    
    console.log(`✅ Updated ${sheetName} with ${numRows} rows of ${dataType} data`);
    return { success: true, rowCount: numRows };
    
  } catch (error) {
    console.error(`Error updating ${sheetName}:`, error.message);
    throw error;
  }
}

/**
 * Main function to collect live odds using nflreadpy
 */
async function collectLiveOdds(spreadsheetId, sheetName = 'Live_Odds') {
  try {
    console.log('🚀 Starting live odds collection with nflreadpy...');
    
    // Load credentials
    const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';
    const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
    
    // Initialize Google Sheets
    const sheetsClient = initializeSheetsClient(credentials);
    
    // Fetch live odds using nflreadpy
    const oddsData = await fetchLiveOdds();
    
    if (oddsData.length === 0) {
      console.log('⚠️ No odds data found');
      return { success: false, message: 'No odds data available' };
    }
    
    // Update Google Sheet
    const result = await updateSheet(sheetsClient, spreadsheetId, sheetName, oddsData, 'odds');
    
    console.log('🎉 Live odds collection completed successfully!');
    return result;
    
  } catch (error) {
    console.error('❌ Live odds collection failed:', error.message);
    throw error;
  }
}

/**
 * Main function to download historical data using nflreadpy
 */
async function downloadHistoricalData(years = [2021, 2022, 2023, 2024]) {
  try {
    console.log('🚀 Starting historical NFL data download with nflreadpy...');
    
    // Load credentials
    const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';
    const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
    
    // Initialize Google Sheets
    const sheetsClient = initializeSheetsClient(credentials);
    
    const spreadsheetId = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU'; // Your sheet ID
    
    for (const year of years) {
      console.log(`\n📅 Processing year ${year}...`);
      
      // Fetch games data
      const gamesData = await fetchHistoricalData([year]);
      if (gamesData.length > 0) {
        await updateSheet(sheetsClient, spreadsheetId, `NFL_Games_${year}`, gamesData, 'games');
      }
      
      // Fetch team stats data
      const teamStatsData = await fetchHistoricalData([year, 'team_stats']);
      if (teamStatsData.length > 0) {
        await updateSheet(sheetsClient, spreadsheetId, `NFL_TeamStats_${year}`, teamStatsData, 'team_stats');
      }
      
      // Small delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    console.log('🎉 Historical data download completed!');
    return { success: true, yearsProcessed: years.length };
    
  } catch (error) {
    console.error('❌ Historical data download failed:', error.message);
    throw error;
  }
}

module.exports = {
  collectLiveOdds,
  downloadHistoricalData,
  fetchLiveOdds,
  fetchHistoricalData,
};
