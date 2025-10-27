#!/usr/bin/env node

const fs = require('fs');
const { google } = require('googleapis');

const SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
const SHEET_NAME = 'upcoming_games';
const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';

async function checkWeatherData() {
  const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
  
  const auth = new google.auth.GoogleAuth({
    credentials,
    scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
  });
  
  const sheetsClient = google.sheets({ version: 'v4', auth });
  
  // Get headers
  const headersRes = await sheetsClient.spreadsheets.values.get({
    spreadsheetId: SPREADSHEET_ID,
    range: `${SHEET_NAME}!A1:CZ1`,
  });
  
  const headers = headersRes.data.values[0];
  
  // Find weather columns
  const weatherColumns = [];
  headers.forEach((header, index) => {
    if (header && (header.includes('temp') || header.includes('weather') || header.includes('wind'))) {
      weatherColumns.push({ index, header });
    }
  });
  
  console.log('\n🌤️  WEATHER DATA CHECK\n');
  console.log('='  .repeat(70));
  
  if (weatherColumns.length === 0) {
    console.log('❌ NO WEATHER COLUMNS FOUND!');
    console.log('\nThis explains why weather predictions might not be accurate.');
    console.log('The models expect "temp" and "wind" columns but they don\'t exist.');
    return;
  }
  
  console.log('📊 Weather columns found:');
  weatherColumns.forEach(col => {
    const letter = getColumnLetter(col.index);
    console.log(`   ${col.header} (Column ${letter})`);
  });
  
  // Check a few rows for weather data
  console.log('\n📋 Checking weather data in sample rows...\n');
  
  const sampleRows = [110, 111, 112]; // Tonight's game and next few
  
  for (const rowNum of sampleRows) {
    const rowRes = await sheetsClient.spreadsheets.values.get({
      spreadsheetId: SPREADSHEET_ID,
      range: `${SHEET_NAME}!A${rowNum}:CZ${rowNum}`,
    });
    
    const row = rowRes.data.values ? rowRes.data.values[0] : [];
    
    // Get game info
    const awayTeamIdx = headers.findIndex(h => h === 'away_team');
    const homeTeamIdx = headers.findIndex(h => h === 'home_team');
    const gamedayIdx = headers.findIndex(h => h === 'gameday');
    
    const awayTeam = row[awayTeamIdx] || 'N/A';
    const homeTeam = row[homeTeamIdx] || 'N/A';
    const gameday = row[gamedayIdx] || 'N/A';
    
    console.log(`Row ${rowNum}: ${awayTeam} @ ${homeTeam} (${gameday})`);
    
    // Check weather data
    weatherColumns.forEach(col => {
      const value = row[col.index] || '';
      console.log(`   ${col.header}: "${value}"`);
    });
    
    console.log('');
  }
  
  // Check if weather data exists in any rows
  console.log('📊 Weather data summary:');
  const hasWeatherData = weatherColumns.some(col => {
    const colIndex = col.index;
    // Check first 50 rows for any non-empty weather data
    return checkColumnHasData(sheetsClient, colIndex, 50);
  });
  
  if (hasWeatherData) {
    console.log('   ✅ Some weather data found');
  } else {
    console.log('   ❌ NO weather data found in any rows');
    console.log('\n🔧 SOLUTION NEEDED:');
    console.log('   The models expect weather data but it\'s not being populated.');
    console.log('   This could significantly impact prediction accuracy.');
    console.log('\n   Possible fixes:');
    console.log('   1. Check if the data source provides weather');
    console.log('   2. Add weather API integration');
    console.log('   3. Use default values (temp=70, wind=0)');
  }
  
  console.log('\n' + '='  .repeat(70) + '\n');
}

async function checkColumnHasData(sheetsClient, colIndex, maxRows) {
  try {
    const letter = getColumnLetter(colIndex);
    const response = await sheetsClient.spreadsheets.values.get({
      spreadsheetId: SPREADSHEET_ID,
      range: `upcoming_games!${letter}2:${letter}${maxRows + 1}`,
    });
    
    const values = response.data.values || [];
    return values.some(row => row[0] && row[0].trim() !== '');
  } catch (error) {
    return false;
  }
}

function getColumnLetter(colIndex) {
  let letter = '';
  let index = colIndex;
  while (index >= 0) {
    letter = String.fromCharCode((index % 26) + 65) + letter;
    index = Math.floor(index / 26) - 1;
  }
  return letter;
}

checkWeatherData()
  .then(() => process.exit(0))
  .catch(err => {
    console.error('Error:', err);
    process.exit(1);
  });


