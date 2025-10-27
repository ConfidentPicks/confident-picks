#!/usr/bin/env node

const fs = require('fs');
const { google } = require('googleapis');

const SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
const SHEET_NAME = 'upcoming_games';
const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';

async function checkRow110() {
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
  
  // Get row 110
  const rowRes = await sheetsClient.spreadsheets.values.get({
    spreadsheetId: SPREADSHEET_ID,
    range: `${SHEET_NAME}!A110:CZ110`,
  });
  
  const row = rowRes.data.values ? rowRes.data.values[0] : [];
  
  console.log('\n🏈 ROW 110 - TONIGHT\'S GAME\n');
  console.log('='  .repeat(70));
  
  // Find key columns
  const findCol = (name) => headers.findIndex(h => h === name);
  
  const awayTeamIdx = findCol('away_team');
  const homeTeamIdx = findCol('home_team');
  const gamedayIdx = findCol('gameday');
  const awayScoreIdx = findCol('away_score');
  const homeScoreIdx = findCol('home_score');
  const spreadLineIdx = findCol('spread_line');
  const totalLineIdx = findCol('total_line');
  
  console.log('GAME INFO:');
  console.log(`   Away Team: ${row[awayTeamIdx] || 'N/A'}`);
  console.log(`   Home Team: ${row[homeTeamIdx] || 'N/A'}`);
  console.log(`   Gameday: ${row[gamedayIdx] || 'N/A'}`);
  console.log(`   Away Score: ${row[awayScoreIdx] || 'N/A'}`);
  console.log(`   Home Score: ${row[homeScoreIdx] || 'N/A'}`);
  console.log(`   Spread Line: ${row[spreadLineIdx] || 'N/A'}`);
  console.log(`   Total Line: ${row[totalLineIdx] || 'N/A'}`);
  
  console.log('\n' + '-' .repeat(70));
  console.log('PREDICTIONS:\n');
  
  // Winner predictions
  const predictedWinnerIdx = findCol('predicted_winner');
  const winnerConfidenceIdx = findCol('winner_confidence');
  const winnerConfidenceFpiIdx = findCol('winner_confidence_fpi');
  
  if (predictedWinnerIdx >= 0) {
    const col = getColumnLetter(predictedWinnerIdx);
    console.log(`   predicted_winner (${col}): "${row[predictedWinnerIdx] || ''}"`);
  }
  
  if (winnerConfidenceIdx >= 0) {
    const col = getColumnLetter(winnerConfidenceIdx);
    console.log(`   winner_confidence (${col}): "${row[winnerConfidenceIdx] || ''}"`);
  }
  
  if (winnerConfidenceFpiIdx >= 0) {
    const col = getColumnLetter(winnerConfidenceFpiIdx);
    console.log(`   winner_confidence_fpi (${col}): "${row[winnerConfidenceFpiIdx] || ''}"`);
  }
  
  // Spread predictions
  console.log('\n   SPREAD:');
  const predictedCoverHomeIdx = findCol('Predicted_Cover_Home');
  const homeCoverConfidenceIdx = findCol('Home_Cover_Confidence');
  const predictedCoverAwayIdx = findCol('Predicted_Cover_Away');
  const awayCoverConfidenceIdx = findCol('Away_Cover_Confidence');
  
  if (predictedCoverHomeIdx >= 0) {
    const col = getColumnLetter(predictedCoverHomeIdx);
    console.log(`   Predicted_Cover_Home (${col}): "${row[predictedCoverHomeIdx] || ''}"`);
  }
  
  if (homeCoverConfidenceIdx >= 0) {
    const col = getColumnLetter(homeCoverConfidenceIdx);
    console.log(`   Home_Cover_Confidence (${col}): "${row[homeCoverConfidenceIdx] || ''}"`);
  }
  
  if (predictedCoverAwayIdx >= 0) {
    const col = getColumnLetter(predictedCoverAwayIdx);
    console.log(`   Predicted_Cover_Away (${col}): "${row[predictedCoverAwayIdx] || ''}"`);
  }
  
  if (awayCoverConfidenceIdx >= 0) {
    const col = getColumnLetter(awayCoverConfidenceIdx);
    console.log(`   Away_Cover_Confidence (${col}): "${row[awayCoverConfidenceIdx] || ''}"`);
  }
  
  // Total predictions
  console.log('\n   TOTAL:');
  const predictedTotalIdx = findCol('Predicted_Total');
  const totalConfidenceIdx = findCol('total_confidence');
  
  if (predictedTotalIdx >= 0) {
    const col = getColumnLetter(predictedTotalIdx);
    console.log(`   Predicted_Total (${col}): "${row[predictedTotalIdx] || ''}"`);
  }
  
  if (totalConfidenceIdx >= 0) {
    const col = getColumnLetter(totalConfidenceIdx);
    console.log(`   total_confidence (${col}): "${row[totalConfidenceIdx] || ''}"`);
  }
  
  console.log('\n' + '='  .repeat(70) + '\n');
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

checkRow110()
  .then(() => process.exit(0))
  .catch(err => {
    console.error('Error:', err);
    process.exit(1);
  });


