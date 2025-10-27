#!/usr/bin/env node

const fs = require('fs');
const { google } = require('googleapis');

const SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
const SHEET_NAME = 'upcoming_games';
const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';

async function checkSpecificColumns() {
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
  
  // Get sample data (row 110)
  const rowRes = await sheetsClient.spreadsheets.values.get({
    spreadsheetId: SPREADSHEET_ID,
    range: `${SHEET_NAME}!A110:CZ110`,
  });
  
  const row = rowRes.data.values ? rowRes.data.values[0] : [];
  
  console.log('\n🎯 YOUR TOUCH-ONLY COLUMNS\n');
  console.log('=' .repeat(70));
  
  const touchColumns = ['AU', 'AV', 'AX', 'AY', 'BA', 'BB', 'BD', 'BE', 'BG', 'BH', 'BK'];
  
  touchColumns.forEach(colLetter => {
    const index = getColumnIndex(colLetter);
    const header = headers[index] || '';
    const value = row[index] || '';
    console.log(`${colLetter.padEnd(3)}: "${header}" = "${value}"`);
  });
  
  console.log('\n📋 ANALYSIS\n');
  console.log('=' .repeat(70));
  
  // Check for missing columns based on the prediction models
  console.log('Expected columns for complete prediction system:');
  console.log('');
  console.log('WINNER PREDICTIONS:');
  console.log('  - predicted_winner (team name)');
  console.log('  - winner_confidence (percentage)');
  console.log('  - winner_confidence_fpi (FPI adjustment)');
  console.log('');
  console.log('SPREAD COVER PREDICTIONS:');
  console.log('  - predicted_home_cover (YES/NO)');
  console.log('  - home_cover_confidence (percentage)');
  console.log('  - predicted_away_cover (YES/NO)');
  console.log('  - away_cover_confidence (percentage)');
  console.log('');
  console.log('TOTAL PREDICTIONS:');
  console.log('  - predicted_total (OVER/UNDER)');
  console.log('  - total_confidence (percentage)');
  console.log('');
  console.log('SCORE PREDICTIONS:');
  console.log('  - predicted_home_score (number)');
  console.log('  - predicted_away_score (number)');
  
  console.log('\n' + '=' .repeat(70) + '\n');
}

function getColumnIndex(letter) {
  let index = 0;
  for (let i = 0; i < letter.length; i++) {
    index = index * 26 + (letter.charCodeAt(i) - 64);
  }
  return index - 1;
}

checkSpecificColumns()
  .then(() => process.exit(0))
  .catch(err => {
    console.error('Error:', err);
    process.exit(1);
  });

