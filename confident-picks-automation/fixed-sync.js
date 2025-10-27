#!/usr/bin/env node

/**
 * Fixed Sync Script - Uses correct sheet name and simple range
 */

const fs = require('fs');
const path = require('path');
const { initializeApp, cert } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');
const { google } = require('googleapis');

async function main() {
  console.log('\n🚀 Fixed Google Sheets Sync\n');
  
  // Load configuration
  const configPath = path.join(__dirname, 'config', 'google-sheets.json');
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  
  // Load service account credentials
  const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';
  const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
  
  // Initialize Firebase
  console.log('🔥 Initializing Firebase...');
  const app = initializeApp({ credential: cert(credentials) });
  const db = getFirestore(app);
  console.log('✅ Firebase initialized');
  
  // Initialize Google Sheets
  console.log('📊 Initializing Google Sheets...');
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
  
  const sheetsClient = google.sheets({ version: 'v4', auth });
  console.log('✅ Google Sheets initialized');
  
  try {
    console.log('🔄 Getting picks from Firebase...');
    
    // Get picks from Firebase
    const picksSnapshot = await db.collection('live_picks').get();
    const picks = [];
    picksSnapshot.forEach(doc => {
      picks.push({ id: doc.id, ...doc.data() });
    });
    
    console.log(`📊 Found ${picks.length} picks in Firebase`);
    
    if (picks.length === 0) {
      console.log('⚠️ No picks found in Firebase');
      return;
    }
    
    // Convert to simple format
    const headers = [
      'ID',
      'League', 
      'Game',
      'Pick',
      'Market Type',
      'Odds',
      'Confidence',
      'Status',
      'Result',
      'Reasoning'
    ];
    
    const rows = [headers]; // Start with headers
    
    picks.forEach(pick => {
      const row = [
        pick.id || '',
        pick.league || '',
        `${pick.homeTeam || ''} vs ${pick.awayTeam || ''}`,
        pick.pick || '',
        pick.marketType || '',
        pick.odds || '',
        pick.modelConfidence || '',
        pick.status || '',
        pick.result || '',
        pick.reasoning || ''
      ];
      rows.push(row);
    });
    
    console.log(`📝 Writing ${rows.length} rows to Google Sheets...`);
    console.log('   Sheet: live_picks_sheets (correct sheet name)');
    console.log(`   Range: A1:Z${rows.length} (${rows.length} rows)`);
    
    // Write data to the correct sheet
    await sheetsClient.spreadsheets.values.update({
      spreadsheetId: config.spreadsheetId,
      range: `A1:Z${rows.length}`, // Dynamic range based on number of rows
      valueInputOption: 'USER_ENTERED',
      resource: { values: rows },
    });
    
    console.log('✅ Successfully synced picks to Google Sheets!');
    console.log('\n🎉 Check your Google Sheet - you should see your Firebase data!');
    console.log('   Headers in row 1, data starting from row 2');
    
  } catch (error) {
    console.error('\n❌ Sync failed:', error.message);
  }
}

main();
