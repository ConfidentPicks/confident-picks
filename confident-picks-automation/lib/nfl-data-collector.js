/**
 * NFL Data Collector - Downloads historical NFL data for model building
 * 
 * This script fetches 3-5 years of NFL data (2021-2024) for analysis and model training
 */

const fs = require('fs');
const path = require('path');
const axios = require('axios');
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
 * Fetch NFL schedule data for a given year
 */
async function fetchNFLSchedule(year) {
  try {
    console.log(`📅 Fetching NFL schedule for ${year}...`);
    
    const response = await axios.get(`https://api.sportsdata.io/v3/nfl/scores/json/Schedules/${year}`, {
      headers: {
        'Ocp-Apim-Subscription-Key': process.env.SPORTSDATA_API_KEY || 'your-sportsdata-api-key'
      }
    });
    
    return response.data;
  } catch (error) {
    console.error(`Error fetching schedule for ${year}:`, error.message);
    return [];
  }
}

/**
 * Fetch NFL game stats for a given year
 */
async function fetchNFLGameStats(year) {
  try {
    console.log(`📊 Fetching NFL game stats for ${year}...`);
    
    const response = await axios.get(`https://api.sportsdata.io/v3/nfl/scores/json/GameStats/${year}`, {
      headers: {
        'Ocp-Apim-Subscription-Key': process.env.SPORTSDATA_API_KEY || 'your-sportsdata-api-key'
      }
    });
    
    return response.data;
  } catch (error) {
    console.error(`Error fetching game stats for ${year}:`, error.message);
    return [];
  }
}

/**
 * Fetch NFL team stats for a given year
 */
async function fetchNFLTeamStats(year) {
  try {
    console.log(`🏈 Fetching NFL team stats for ${year}...`);
    
    const response = await axios.get(`https://api.sportsdata.io/v3/nfl/scores/json/TeamSeasonStats/${year}`, {
      headers: {
        'Ocp-Apim-Subscription-Key': process.env.SPORTSDATA_API_KEY || 'your-sportsdata-api-key'
      }
    });
    
    return response.data;
  } catch (error) {
    console.error(`Error fetching team stats for ${year}:`, error.message);
    return [];
  }
}

/**
 * Fetch NFL player stats for a given year
 */
async function fetchNFLPlayerStats(year) {
  try {
    console.log(`👤 Fetching NFL player stats for ${year}...`);
    
    const response = await axios.get(`https://api.sportsdata.io/v3/nfl/scores/json/PlayerSeasonStats/${year}`, {
      headers: {
        'Ocp-Apim-Subscription-Key': process.env.SPORTSDATA_API_KEY || 'your-sportsdata-api-key'
      }
    });
    
    return response.data;
  } catch (error) {
    console.error(`Error fetching player stats for ${year}:`, error.message);
    return [];
  }
}

/**
 * Convert schedule data to Google Sheets format
 */
function scheduleToSheetFormat(scheduleData) {
  const headers = [
    'GameID',
    'Season',
    'Week',
    'SeasonType',
    'Date',
    'HomeTeam',
    'AwayTeam',
    'HomeScore',
    'AwayScore',
    'OverUnder',
    'PointSpread',
    'HomeTeamMoneyLine',
    'AwayTeamMoneyLine',
    'TotalYards',
    'HomeYards',
    'AwayYards',
    'HomeTurnovers',
    'AwayTurnovers',
    'HomeTimeOfPossession',
    'AwayTimeOfPossession'
  ];

  const rows = [headers];

  scheduleData.forEach(game => {
    const row = [
      game.GameID || '',
      game.Season || '',
      game.Week || '',
      game.SeasonType || '',
      game.Date || '',
      game.HomeTeam || '',
      game.AwayTeam || '',
      game.HomeScore || '',
      game.AwayScore || '',
      game.OverUnder || '',
      game.PointSpread || '',
      game.HomeTeamMoneyLine || '',
      game.AwayTeamMoneyLine || '',
      game.TotalYards || '',
      game.HomeYards || '',
      game.AwayYards || '',
      game.HomeTurnovers || '',
      game.AwayTurnovers || '',
      game.HomeTimeOfPossession || '',
      game.AwayTimeOfPossession || ''
    ];
    
    rows.push(row);
  });

  return rows;
}

/**
 * Convert team stats to Google Sheets format
 */
function teamStatsToSheetFormat(teamStatsData) {
  const headers = [
    'Team',
    'Season',
    'Games',
    'PassingYards',
    'PassingTouchdowns',
    'RushingYards',
    'RushingTouchdowns',
    'ReceivingYards',
    'ReceivingTouchdowns',
    'Interceptions',
    'Fumbles',
    'Sacks',
    'TacklesForLoss',
    'QuarterbackHits',
    'PassesDefended',
    'FumblesRecovered',
    'FumblesForced',
    'InterceptionsReturnedForTouchdowns',
    'FumblesReturnedForTouchdowns',
    'Safeties',
    'Punts',
    'PuntYards',
    'PuntAverage',
    'FieldGoalsAttempted',
    'FieldGoalsMade',
    'ExtraPointsAttempted',
    'ExtraPointsMade',
    'Penalties',
    'PenaltyYards',
    'TimeOfPossessionMinutes',
    'TimeOfPossessionSeconds',
    'TimeOfPossession'
  ];

  const rows = [headers];

  teamStatsData.forEach(team => {
    const row = [
      team.Team || '',
      team.Season || '',
      team.Games || '',
      team.PassingYards || '',
      team.PassingTouchdowns || '',
      team.RushingYards || '',
      team.RushingTouchdowns || '',
      team.ReceivingYards || '',
      team.ReceivingTouchdowns || '',
      team.Interceptions || '',
      team.Fumbles || '',
      team.Sacks || '',
      team.TacklesForLoss || '',
      team.QuarterbackHits || '',
      team.PassesDefended || '',
      team.FumblesRecovered || '',
      team.FumblesForced || '',
      team.InterceptionsReturnedForTouchdowns || '',
      team.FumblesReturnedForTouchdowns || '',
      team.Safeties || '',
      team.Punts || '',
      team.PuntYards || '',
      team.PuntAverage || '',
      team.FieldGoalsAttempted || '',
      team.FieldGoalsMade || '',
      team.ExtraPointsAttempted || '',
      team.ExtraPointsMade || '',
      team.Penalties || '',
      team.PenaltyYards || '',
      team.TimeOfPossessionMinutes || '',
      team.TimeOfPossessionSeconds || '',
      team.TimeOfPossession || ''
    ];
    
    rows.push(row);
  });

  return rows;
}

/**
 * Update Google Sheet with historical data
 */
async function updateHistoricalSheet(sheetsClient, spreadsheetId, sheetName, data, dataType) {
  try {
    console.log(`📊 Updating ${sheetName} with ${dataType} data...`);
    
    let sheetData;
    if (dataType === 'schedule') {
      sheetData = scheduleToSheetFormat(data);
    } else if (dataType === 'teamStats') {
      sheetData = teamStatsToSheetFormat(data);
    } else {
      throw new Error(`Unknown data type: ${dataType}`);
    }
    
    const numRows = sheetData.length;
    
    // Clear existing data and write new data
    await sheetsClient.spreadsheets.values.clear({
      spreadsheetId,
      range: `${sheetName}!A1:Z10000`,
    });
    
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
 * Download historical NFL data for multiple years
 */
async function downloadHistoricalData(years = [2021, 2022, 2023, 2024]) {
  try {
    console.log('🚀 Starting historical NFL data download...');
    
    // Load credentials
    const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';
    const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
    
    // Initialize Google Sheets
    const sheetsClient = initializeSheetsClient(credentials);
    
    const spreadsheetId = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU'; // Your sheet ID
    
    for (const year of years) {
      console.log(`\n📅 Processing year ${year}...`);
      
      // Fetch schedule data
      const scheduleData = await fetchNFLSchedule(year);
      if (scheduleData.length > 0) {
        await updateHistoricalSheet(sheetsClient, spreadsheetId, `NFL_Schedule_${year}`, scheduleData, 'schedule');
      }
      
      // Fetch team stats
      const teamStatsData = await fetchNFLTeamStats(year);
      if (teamStatsData.length > 0) {
        await updateHistoricalSheet(sheetsClient, spreadsheetId, `NFL_TeamStats_${year}`, teamStatsData, 'teamStats');
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
  downloadHistoricalData,
  fetchNFLSchedule,
  fetchNFLTeamStats,
  fetchNFLPlayerStats,
  scheduleToSheetFormat,
  teamStatsToSheetFormat,
};



