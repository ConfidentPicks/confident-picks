#!/usr/bin/env node

const fs = require('fs');
const { google } = require('googleapis');

const SPREADSHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
const SHEET_NAME = 'upcoming_games';
const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';

async function fixColumnHeaders() {
  const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
  
  const auth = new google.auth.GoogleAuth({
    credentials,
    scopes: ['https://www.googleapis.com/auth/spreadsheets'],
  });
  
  const sheetsClient = google.sheets({ version: 'v4', auth });
  
  console.log('\n🔧 FIXING COLUMN HEADERS\n');
  console.log('=' .repeat(70));
  
  // Fix the 3 column headers
  const updates = [
    {
      range: `${SHEET_NAME}!AY1`,
      values: [['predicted_home_cover']]
    },
    {
      range: `${SHEET_NAME}!BB1`,
      values: [['predicted_away_cover']]
    },
    {
      range: `${SHEET_NAME}!BE1`,
      values: [['predicted_total']]
    }
  ];
  
  try {
    const response = await sheetsClient.spreadsheets.values.batchUpdate({
      spreadsheetId: SPREADSHEET_ID,
      resource: {
        valueInputOption: 'RAW',
        data: updates
      }
    });
    
    console.log('✅ Column headers updated successfully!');
    console.log('   AY: predicted_home_cover');
    console.log('   BB: predicted_away_cover');
    console.log('   BE: predicted_total');
    
  } catch (error) {
    console.error('❌ Error updating headers:', error.message);
    throw error;
  }
  
  console.log('\n' + '=' .repeat(70) + '\n');
}

fixColumnHeaders()
  .then(() => process.exit(0))
  .catch(err => {
    console.error('Error:', err);
    process.exit(1);
  });

