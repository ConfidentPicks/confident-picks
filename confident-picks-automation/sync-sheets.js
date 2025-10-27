#!/usr/bin/env node

/**
 * Manual Sync Script for Google Sheets ↔ Firebase
 * 
 * Usage:
 *   node sync-sheets.js --to-sheets      # Sync Firebase → Google Sheets
 *   node sync-sheets.js --to-firebase    # Sync Google Sheets → Firebase
 *   node sync-sheets.js --both           # Sync both directions
 */

const fs = require('fs');
const path = require('path');
const { initializeApp, cert } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');
const {
  initializeSheetsClient,
  syncFirebaseToSheets,
  importSheetsToFirebase,
} = require('./lib/google-sheets');

async function main() {
  console.log('\n🔄 Google Sheets ↔ Firebase Sync\n');
  
  // Parse command line arguments
  const args = process.argv.slice(2);
  const direction = args.includes('--to-firebase') ? 'to-firebase' 
    : args.includes('--to-sheets') ? 'to-sheets'
    : 'both';
  
  // Load configuration
  const configPath = path.join(__dirname, 'config', 'google-sheets.json');
  
  if (!fs.existsSync(configPath)) {
    console.error('❌ Configuration file not found!');
    console.log('Please run: node setup-google-sheets.js');
    process.exit(1);
  }
  
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  
  // Load service account credentials
  if (!fs.existsSync(config.serviceAccountPath)) {
    console.error('❌ Service account file not found!');
    console.log(`Expected at: ${config.serviceAccountPath}`);
    process.exit(1);
  }
  
  const credentials = JSON.parse(fs.readFileSync(config.serviceAccountPath, 'utf8'));
  
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
    // Sync Firebase to Sheets
    if (direction === 'to-sheets' || direction === 'both') {
      console.log('\n📤 Syncing Firebase → Google Sheets...');
      const result = await syncFirebaseToSheets(
        sheetsClient,
        db,
        config.spreadsheetId,
        config.sheetName
      );
      console.log(`✅ Synced ${result.pickCount} picks to Google Sheets`);
    }
    
    // Sync Sheets to Firebase
    if (direction === 'to-firebase' || direction === 'both') {
      console.log('\n📥 Syncing Google Sheets → Firebase...');
      const result = await importSheetsToFirebase(
        sheetsClient,
        db,
        config.spreadsheetId,
        config.sheetName,
        'qa_picks' // Import to QA collection for review
      );
      console.log(`✅ Imported ${result.pickCount} picks to Firebase (qa_picks collection)`);
    }
    
    console.log('\n🎉 Sync completed successfully!');
    
  } catch (error) {
    console.error('\n❌ Sync failed:', error.message);
    console.error(error);
    process.exit(1);
  }
}

main();




