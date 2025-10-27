#!/usr/bin/env node

const fs = require('fs');
const { google } = require('googleapis');

const SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
const SHEET_NAME = 'upcoming_games';
const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';

async function checkFullAccuracy() {
  const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
  
  const auth = new google.auth.GoogleAuth({
    credentials,
    scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
  });
  
  const sheetsClient = google.sheets({ version: 'v4', auth });
  
  // Get data from AV (predicted_winner) and AW (actual_winner) columns
  const res = await sheetsClient.spreadsheets.values.get({
    spreadsheetId: SPREADSHEET_ID,
    range: `${SHEET_NAME}!AV2:AW273`,
  });
  
  const rows = res.data.values || [];
  
  console.log('\nCHECKING FULL WINNER PREDICTION ACCURACY\n');
  console.log('=' .repeat(70));
  
  let totalRows = 0;
  let nonBlankRows = 0;
  let matches = 0;
  
  console.log('Analyzing all rows with data...');
  
  for (let i = 0; i < rows.length; i++) {
    const row = rows[i] || [];
    const predicted = row[0] || '';
    const actual = row[1] || '';
    
    totalRows++;
    if (predicted !== '' && actual !== '') {
      nonBlankRows++;
      if (predicted === actual) {
        matches++;
      }
    }
  }
  
  console.log('\n' + '=' .repeat(70));
  console.log('FULL DATASET RESULTS:');
  console.log(`Total rows checked: ${totalRows}`);
  console.log(`Rows with both predicted and actual: ${nonBlankRows}`);
  console.log(`Matches: ${matches}`);
  console.log(`Accuracy: ${nonBlankRows > 0 ? (matches / nonBlankRows * 100).toFixed(1) : 0}%`);
  
  if (nonBlankRows > 0) {
    console.log(`\nFormula result: ${matches}/${nonBlankRows} = ${(matches / nonBlankRows * 100).toFixed(1)}%`);
  }
  
  console.log('\n' + '=' .repeat(70) + '\n');
}

checkFullAccuracy()
  .then(() => process.exit(0))
  .catch(err => {
    console.error('Error:', err);
    process.exit(1);
  });

