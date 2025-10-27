#!/usr/bin/env node

/**
 * Simple Sync Script - Just write data without clearing
 * 
 * This script writes Firebase picks to Google Sheets without trying to clear first
 */

const fs = require('fs');
const path = require('path');
const { initializeApp, cert } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');
const {
  initializeSheetsClient,
  writeSheet,
  picksToSheetFormat,
} = require('./lib/google-sheets');

async function main() {
  console.log('\n🚀 Simple Google Sheets Sync\n');
  
  // Load configuration
  const configPath = path.join(__dirname, 'config', 'google-sheets.json');
  
  if (!fs.existsSync(configPath)) {
    console.error('❌ Configuration not found!');
    console.log('Please run: node setup-my-sheet.js');
    process.exit(1);
  }
  
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  
  // Load service account credentials
  const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';
  
  if (!fs.existsSync(serviceAccountPath)) {
    console.error('❌ Service account file not found!');
    console.log(`Expected at: ${serviceAccountPath}`);
    process.exit(1);
  }
  
  const credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
  
  // Initialize Firebase
  console.log('🔥 Initializing Firebase...');
  const app = initializeApp({
    credential: cert(credentials),
  });
  const db = getFirestore(app);
  console.log('✅ Firebase initialized');
  
  // Initialize Google Sheets
  console.log('📊 Initializing Google Sheets...');
  const sheetsClient = initializeSheetsClient(credentials);
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
    
    // Convert to sheet format
    const sheetData = picksToSheetFormat(picks);
    
    console.log(`📝 Writing ${sheetData.length} rows to Google Sheets...`);
    console.log(`   Sheet: ${config.sheetName}`);
    console.log(`   Range: A1`);
    
    // Write data directly without clearing
    await writeSheet(sheetsClient, config.spreadsheetId, `${config.sheetName}!A1`, sheetData);
    
    console.log('✅ Successfully synced picks to Google Sheets!');
    console.log('\n🎉 Check your Google Sheet to see the data!');
    
  } catch (error) {
    console.error('\n❌ Sync failed:', error.message);
    
    if (error.message.includes('permission')) {
      console.log('\n🔧 Fix: Make sure your sheet is shared with:');
      console.log(`     ${credentials.client_email}`);
    } else if (error.message.includes('API has not been used')) {
      console.log('\n🔧 Fix: Enable Google Sheets API');
      console.log('     https://console.cloud.google.com/apis/library/sheets.googleapis.com');
    } else {
      console.log('\n🔧 Unknown error. Please check:');
      console.log('1. Sheet is shared with service account');
      console.log('2. Google Sheets API is enabled');
      console.log('3. Sheet name is correct');
    }
  }
}

main();



