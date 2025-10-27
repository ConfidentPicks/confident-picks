#!/usr/bin/env node

const fs = require('fs');
const { google } = require('googleapis');

const SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
const SHEET_NAME = 'upcoming_games';
const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';

async function debugSaturdayGames() {
  const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
  
  const auth = new google.auth.GoogleAuth({
    credentials,
    scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
  });
  
  const sheetsClient = google.sheets({ version: 'v4', auth });
  
  const response = await sheetsClient.spreadsheets.values.get({
    spreadsheetId: SPREADSHEET_ID,
    range: `${SHEET_NAME}!A111:CZ115`,
  });
  
  const rows = response.data.values;
  const headers = rows[0];
  
  console.log('\n🔍 DEBUGGING SATURDAY GAMES (Rows 111-115)\n');
  console.log('='  .repeat(70));
  
  // Find key columns
  const colMap = {};
  headers.forEach((header, idx) => {
    colMap[header] = idx;
  });
  
  const keyColumns = [
    'away_team', 'home_team', 'gameday',
    'predicted_winner', 'winner_confidence', 'winner_confidence_fpi',
    'Predicted_Cover_Home', 'Home_Cover_Confidence',
    'Predicted_Total', 'total_confidence'
  ];
  
  console.log('Key Columns Found:');
  keyColumns.forEach(col => {
    if (colMap[col] !== undefined) {
      const letter = getColumnLetter(colMap[col]);
      console.log(`   ${col}: Column ${letter} (index ${colMap[col]})`);
    } else {
      console.log(`   ${col}: ❌ NOT FOUND`);
    }
  });
  
  console.log('\n' + '='  .repeat(70));
  
  // Show data for each game
  for (let i = 1; i < Math.min(rows.length, 6); i++) {
    const row = rows[i];
    
    console.log(`\nRow ${110 + i}:`);
    console.log(`   Away: ${row[colMap['away_team']] || 'N/A'}`);
    console.log(`   Home: ${row[colMap['home_team']] || 'N/A'}`);
    console.log(`   Date: ${row[colMap['gameday']] || 'N/A'}`);
    console.log(`\n   PREDICTIONS:`);
    console.log(`   predicted_winner: "${row[colMap['predicted_winner']] || ''}"`);
    console.log(`   winner_confidence: "${row[colMap['winner_confidence']] || ''}"`);
    console.log(`   winner_confidence_fpi: "${row[colMap['winner_confidence_fpi']] || ''}"`);
    console.log(`   Predicted_Total: "${row[colMap['Predicted_Total']] || ''}"`);
    console.log(`   total_confidence: "${row[colMap['total_confidence']] || ''}"`);
    console.log('-'  .repeat(70));
  }
  
  console.log('\n');
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

debugSaturdayGames()
  .then(() => process.exit(0))
  .catch(err => {
    console.error('Error:', err);
    process.exit(1);
  });


