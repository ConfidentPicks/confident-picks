#!/usr/bin/env node

const fs = require('fs');
const { google } = require('googleapis');

const SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
const SHEET_NAME = 'upcoming_games';
const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';

async function checkHeadersAroundAV() {
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
  
  console.log('\nHEADERS AROUND AV-AW-AX:\n');
  console.log('=' .repeat(70));
  
  // Check columns around AV (index 47), AW (index 48), AX (index 49)
  for(let i = 45; i < 55; i++) {
    const letter = getColumnLetter(i);
    const header = headers[i] || '';
    console.log(`${letter.padEnd(3)} (${i}): "${header}"`);
  }
  
  // Check for actual winner column
  console.log('\nLOOKING FOR ACTUAL WINNER COLUMN:\n');
  console.log('=' .repeat(70));
  
  headers.forEach((header, index) => {
    if (header && (header.includes('actual') || header.includes('winner') || header.includes('result'))) {
      const letter = getColumnLetter(index);
      console.log(`${letter.padEnd(3)} (${index}): "${header}"`);
    }
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

checkHeadersAroundAV()
  .then(() => process.exit(0))
  .catch(err => {
    console.error('Error:', err);
    process.exit(1);
  });

