#!/usr/bin/env node

const fs = require('fs');
const { google } = require('googleapis');

const SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
const SHEET_NAME = 'upcoming_games';
const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';

async function checkColumnHeaders() {
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
  
  console.log('\n📊 CURRENT COLUMN HEADERS\n');
  console.log('=' .repeat(70));
  
  headers.forEach((header, index) => {
    if (header && header.trim() !== '') {
      const letter = getColumnLetter(index);
      console.log(`${letter.padEnd(3)}: ${header}`);
    }
  });
  
  // Check specific prediction columns around AZ and BA
  console.log('\n🎯 PREDICTION COLUMNS CHECK\n');
  console.log('=' .repeat(70));
  
  const predictionColumns = ['AU', 'AV', 'AW', 'AX', 'AY', 'AZ', 'BA', 'BB', 'BC', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BK', 'BL', 'BM', 'BN'];
  
  predictionColumns.forEach(colLetter => {
    const index = getColumnIndex(colLetter);
    const header = headers[index] || '';
    const letter = getColumnLetter(index);
    console.log(`${letter.padEnd(3)}: "${header}"`);
  });
  
  // Check a sample row to see what data is in these columns
  console.log('\n📋 SAMPLE DATA (Row 110)\n');
  console.log('=' .repeat(70));
  
  const rowRes = await sheetsClient.spreadsheets.values.get({
    spreadsheetId: SPREADSHEET_ID,
    range: `${SHEET_NAME}!A110:CZ110`,
  });
  
  const row = rowRes.data.values ? rowRes.data.values[0] : [];
  
  predictionColumns.forEach(colLetter => {
    const index = getColumnIndex(colLetter);
    const value = row[index] || '';
    const header = headers[index] || '';
    console.log(`${colLetter.padEnd(3)}: "${header}" = "${value}"`);
  });
  
  console.log('\n' + '=' .repeat(70) + '\n');
}

function getColumnLetter(index) {
  let letter = '';
  let num = index;
  while (num >= 0) {
    letter = String.fromCharCode((num % 26) + 65) + letter;
    num = Math.floor(num / 26) - 1;
  }
  return letter;
}

function getColumnIndex(letter) {
  let index = 0;
  for (let i = 0; i < letter.length; i++) {
    index = index * 26 + (letter.charCodeAt(i) - 64);
  }
  return index - 1;
}

checkColumnHeaders()
  .then(() => process.exit(0))
  .catch(err => {
    console.error('Error:', err);
    process.exit(1);
  });

