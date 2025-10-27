/**
 * Odds Collector - Automatically updates Google Sheets with latest betting odds
 * 
 * This script fetches current odds from various sources and updates your Google Sheet
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
 * Fetch odds from The Odds API (free tier available)
 */
async function fetchOddsFromAPI() {
  try {
    // You'll need to get a free API key from https://the-odds-api.com/
    const apiKey = process.env.ODDS_API_KEY || 'your-odds-api-key-here';
    
    const response = await axios.get('https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/', {
      params: {
        apiKey,
        regions: 'us',
        markets: 'spreads,totals',
        oddsFormat: 'american',
        dateFormat: 'iso',
      },
    });

    return response.data;
  } catch (error) {
    console.error('Error fetching odds from API:', error.message);
    return [];
  }
}

/**
 * Fetch odds from DraftKings (if available)
 */
async function fetchDraftKingsOdds() {
  try {
    // This is a placeholder - you'd need to implement actual DraftKings scraping
    // or use their API if available
    console.log('Fetching DraftKings odds...');
    
    // For now, return mock data structure
    return [
      {
        id: 'dk_001',
        homeTeam: 'Kansas City Chiefs',
        awayTeam: 'Buffalo Bills',
        commenceTime: '2025-10-22T17:00:00Z',
        spreads: [
          { bookmaker: 'DraftKings', point: -3.5, price: -110 }
        ],
        totals: [
          { bookmaker: 'DraftKings', point: 52.5, price: -110 }
        ]
      }
    ];
  } catch (error) {
    console.error('Error fetching DraftKings odds:', error.message);
    return [];
  }
}

/**
 * Fetch odds from FanDuel (if available)
 */
async function fetchFanDuelOdds() {
  try {
    console.log('Fetching FanDuel odds...');
    
    // Placeholder for FanDuel integration
    return [
      {
        id: 'fd_001',
        homeTeam: 'Kansas City Chiefs',
        awayTeam: 'Buffalo Bills',
        commenceTime: '2025-10-22T17:00:00Z',
        spreads: [
          { bookmaker: 'FanDuel', point: -3.5, price: -108 }
        ],
        totals: [
          { bookmaker: 'FanDuel', point: 52.5, price: -108 }
        ]
      }
    ];
  } catch (error) {
    console.error('Error fetching FanDuel odds:', error.message);
    return [];
  }
}

/**
 * Combine odds from multiple sources
 */
async function fetchAllOdds() {
  console.log('🔄 Fetching odds from all sources...');
  
  const [apiOdds, dkOdds, fdOdds] = await Promise.all([
    fetchOddsFromAPI(),
    fetchDraftKingsOdds(),
    fetchFanDuelOdds(),
  ]);

  // Combine and deduplicate odds
  const allOdds = [...apiOdds, ...dkOdds, ...fdOdds];
  
  console.log(`✅ Fetched odds for ${allOdds.length} games`);
  return allOdds;
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
    'DK Spread',
    'DK Spread Odds',
    'FD Spread',
    'FD Spread Odds',
    'DK Total',
    'DK Total Odds',
    'FD Total',
    'FD Total Odds',
    'Last Updated'
  ];

  const rows = [headers];

  oddsData.forEach(game => {
    const row = [
      game.id || '',
      game.homeTeam || '',
      game.awayTeam || '',
      game.commenceTime ? new Date(game.commenceTime).toLocaleString() : '',
      // DraftKings data
      game.spreads?.find(s => s.bookmaker === 'DraftKings')?.point || '',
      game.spreads?.find(s => s.bookmaker === 'DraftKings')?.price || '',
      // FanDuel data
      game.spreads?.find(s => s.bookmaker === 'FanDuel')?.point || '',
      game.spreads?.find(s => s.bookmaker === 'FanDuel')?.price || '',
      // Totals
      game.totals?.find(t => t.bookmaker === 'DraftKings')?.point || '',
      game.totals?.find(t => t.bookmaker === 'DraftKings')?.price || '',
      game.totals?.find(t => t.bookmaker === 'FanDuel')?.point || '',
      game.totals?.find(t => t.bookmaker === 'FanDuel')?.price || '',
      new Date().toISOString()
    ];
    
    rows.push(row);
  });

  return rows;
}

/**
 * Update Google Sheet with latest odds
 */
async function updateOddsSheet(sheetsClient, spreadsheetId, sheetName, oddsData) {
  try {
    console.log(`📊 Updating ${sheetName} with latest odds...`);
    
    const sheetData = oddsToSheetFormat(oddsData);
    const numRows = sheetData.length;
    const numCols = sheetData[0].length;
    
    // Clear existing data and write new data
    await sheetsClient.spreadsheets.values.clear({
      spreadsheetId,
      range: `${sheetName}!A1:Z1000`,
    });
    
    await sheetsClient.spreadsheets.values.update({
      spreadsheetId,
      range: `${sheetName}!A1:Z${numRows}`,
      valueInputOption: 'USER_ENTERED',
      resource: { values: sheetData },
    });
    
    console.log(`✅ Updated ${sheetName} with ${numRows} rows of odds data`);
    return { success: true, rowCount: numRows };
    
  } catch (error) {
    console.error('Error updating odds sheet:', error.message);
    throw error;
  }
}

/**
 * Main function to collect and update odds
 */
async function collectAndUpdateOdds(spreadsheetId, sheetName = 'Live_Odds') {
  try {
    console.log('🚀 Starting odds collection...');
    
    // Load credentials
    const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';
    const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
    
    // Initialize Google Sheets
    const sheetsClient = initializeSheetsClient(credentials);
    
    // Fetch odds from all sources
    const oddsData = await fetchAllOdds();
    
    if (oddsData.length === 0) {
      console.log('⚠️ No odds data found');
      return { success: false, message: 'No odds data available' };
    }
    
    // Update Google Sheet
    const result = await updateOddsSheet(sheetsClient, spreadsheetId, sheetName, oddsData);
    
    console.log('🎉 Odds collection completed successfully!');
    return result;
    
  } catch (error) {
    console.error('❌ Odds collection failed:', error.message);
    throw error;
  }
}

module.exports = {
  collectAndUpdateOdds,
  fetchAllOdds,
  oddsToSheetFormat,
  updateOddsSheet,
};



