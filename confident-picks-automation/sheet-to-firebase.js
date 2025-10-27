#!/usr/bin/env node

/**
 * Sheet to Firebase Sync - Update Firebase when you edit the Google Sheet
 */

const fs = require('fs');
const path = require('path');
const { initializeApp, cert } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');
const { google } = require('googleapis');

async function main() {
  console.log('\n📥 Google Sheet → Firebase Sync\n');
  
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
    console.log('📖 Reading data from Google Sheet...');
    
    // Read data from Google Sheet
    const response = await sheetsClient.spreadsheets.values.get({
      spreadsheetId: config.spreadsheetId,
      range: 'A1:Z100', // Read up to 100 rows
    });
    
    const rows = response.data.values;
    if (!rows || rows.length < 2) {
      console.log('⚠️ No data found in sheet (need at least headers + 1 row)');
      return;
    }
    
    console.log(`📊 Found ${rows.length} rows in Google Sheet`);
    
    // Get headers from first row
    const headers = rows[0];
    console.log('📋 Headers:', headers.join(' | '));
    
    // Process data rows (skip header row)
    const dataRows = rows.slice(1);
    console.log(`📝 Processing ${dataRows.length} data rows...`);
    
    let successCount = 0;
    let errorCount = 0;
    
    for (let i = 0; i < dataRows.length; i++) {
      const row = dataRows[i];
      const rowNumber = i + 2; // +2 because we skip header and arrays are 0-indexed
      
      try {
        // Create pick object from row data
        const pick = {};
        headers.forEach((header, index) => {
          const value = row[index] || '';
          
          // Map sheet columns to Firebase fields
          switch (header.toLowerCase()) {
            case 'id':
              pick.id = value;
              break;
            case 'league':
              pick.league = value;
              break;
            case 'game':
              pick.game = value;
              // Try to parse home/away teams from game string
              if (value.includes(' vs ')) {
                const [home, away] = value.split(' vs ');
                pick.homeTeam = home.trim();
                pick.awayTeam = away.trim();
              }
              break;
            case 'pick':
              pick.pick = value;
              break;
            case 'market type':
              pick.marketType = value;
              break;
            case 'odds':
              pick.odds = value ? parseFloat(value) || value : '';
              break;
            case 'confidence':
              pick.modelConfidence = value ? parseFloat(value) || 0 : 0;
              break;
            case 'status':
              pick.status = value;
              break;
            case 'result':
              pick.result = value;
              break;
            case 'reasoning':
              pick.reasoning = value;
              break;
            default:
              pick[header] = value;
          }
        });
        
        // Add metadata
        pick.updatedAt = new Date().toISOString();
        pick.source = 'google-sheets-import';
        
        // Update Firebase document
        if (pick.id) {
          await db.collection('live_picks').doc(pick.id).set(pick, { merge: true });
          console.log(`✅ Updated Firebase document: ${pick.id} (Row ${rowNumber})`);
          successCount++;
        } else {
          console.log(`⚠️ Skipping row ${rowNumber}: No ID found`);
          errorCount++;
        }
        
      } catch (error) {
        console.log(`❌ Error processing row ${rowNumber}:`, error.message);
        errorCount++;
      }
    }
    
    console.log('\n🎉 Sync completed!');
    console.log(`✅ Successfully updated: ${successCount} documents`);
    if (errorCount > 0) {
      console.log(`❌ Errors: ${errorCount} rows`);
    }
    
    console.log('\n💡 Tips:');
    console.log('- Edit your Google Sheet');
    console.log('- Run this script again to update Firebase');
    console.log('- Make sure to keep the ID column for each row');
    
  } catch (error) {
    console.error('\n❌ Sync failed:', error.message);
  }
}

main();



