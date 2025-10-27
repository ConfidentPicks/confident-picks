#!/usr/bin/env node

/**
 * Quick Connection Test
 * 
 * Run this to verify your Google Sheets connection is working
 * 
 * Usage: node test-sheets-connection.js <spreadsheet-id>
 */

const fs = require('fs');
const path = require('path');

async function testConnection(serviceAccountPath, spreadsheetId) {
  console.log('\n🔍 Testing Google Sheets Connection...\n');
  
  // Step 1: Check service account file
  console.log('Step 1: Loading service account...');
  if (!fs.existsSync(serviceAccountPath)) {
    console.error('❌ Service account file not found!');
    console.log('   Path:', serviceAccountPath);
    return false;
  }
  
  let credentials;
  try {
    credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
    console.log('✅ Service account loaded');
    console.log(`   Project: ${credentials.project_id}`);
    console.log(`   Email: ${credentials.client_email}\n`);
  } catch (error) {
    console.error('❌ Error reading service account:', error.message);
    return false;
  }
  
  // Step 2: Check googleapis module
  console.log('Step 2: Checking googleapis module...');
  try {
    require('googleapis');
    console.log('✅ googleapis module installed\n');
  } catch (error) {
    console.error('❌ googleapis module not found!');
    console.log('   Run: npm install googleapis');
    return false;
  }
  
  // Step 3: Initialize client
  console.log('Step 3: Initializing Google Sheets client...');
  try {
    const { initializeSheetsClient } = require('./lib/google-sheets');
    const sheetsClient = initializeSheetsClient(credentials);
    console.log('✅ Client initialized\n');
    
    // Step 4: Test connection
    console.log('Step 4: Testing connection to spreadsheet...');
    console.log(`   Spreadsheet ID: ${spreadsheetId}`);
    
    const { readSheet } = require('./lib/google-sheets');
    const rows = await readSheet(sheetsClient, spreadsheetId, 'A1:Z1');
    
    console.log('✅ Connection successful!\n');
    
    if (rows && rows.length > 0) {
      console.log('📊 First row data:');
      console.log('   Columns:', rows[0].length);
      console.log('   Headers:', rows[0].join(', '));
    } else {
      console.log('📊 Spreadsheet is empty (this is OK)');
    }
    
    console.log('\n🎉 Everything is working!\n');
    console.log('Next steps:');
    console.log('  1. Run: node sync-sheets.js --to-sheets');
    console.log('  2. Check your Google Sheet for data');
    console.log('  3. Review: docs/GOOGLE_SHEETS.md for more options\n');
    
    return true;
    
  } catch (error) {
    console.error('❌ Connection failed!\n');
    console.error('Error:', error.message);
    
    console.log('\n🔧 Troubleshooting:\n');
    
    if (error.message.includes('permission')) {
      console.log('Issue: Permission denied');
      console.log('Fix: Share the Google Sheet with:');
      console.log(`     ${credentials.client_email}`);
      console.log('');
      console.log('Steps:');
      console.log('  1. Open your Google Sheet');
      console.log('  2. Click "Share" button');
      console.log('  3. Add the email above as "Editor"');
      console.log('  4. Click "Send"');
    } else if (error.message.includes('API has not been used')) {
      console.log('Issue: Google Sheets API not enabled');
      console.log('Fix: Enable the API here:');
      console.log(`     https://console.cloud.google.com/apis/library/sheets.googleapis.com?project=${credentials.project_id}`);
      console.log('');
      console.log('Steps:');
      console.log('  1. Click the link above');
      console.log('  2. Click "ENABLE" button');
      console.log('  3. Wait a few seconds');
      console.log('  4. Run this test again');
    } else if (error.message.includes('Unable to parse range')) {
      console.log('Issue: Invalid spreadsheet ID or sheet name');
      console.log('Fix: Check your spreadsheet URL:');
      console.log('     https://docs.google.com/spreadsheets/d/YOUR_ID_HERE/edit');
      console.log('');
      console.log('The ID is the long string between /d/ and /edit');
    } else {
      console.log('Issue: Unknown error');
      console.log('');
      console.log('Common fixes:');
      console.log('  1. Check internet connection');
      console.log('  2. Verify spreadsheet ID is correct');
      console.log('  3. Ensure sheet exists and isn\'t deleted');
      console.log('  4. Try running: npm install googleapis');
    }
    
    console.log('');
    return false;
  }
}

// Main
async function main() {
  const args = process.argv.slice(2);
  
  // Get service account path
  let serviceAccountPath = args[0];
  if (!serviceAccountPath) {
    // Try to find it in common locations
    const commonPaths = [
      'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json',
      path.join(__dirname, 'service-account.json'),
      path.join(__dirname, 'config', 'service-account.json'),
    ];
    
    for (const p of commonPaths) {
      if (fs.existsSync(p)) {
        serviceAccountPath = p;
        break;
      }
    }
    
    if (!serviceAccountPath) {
      console.log('Usage: node test-sheets-connection.js <service-account-path> <spreadsheet-id>');
      console.log('');
      console.log('Example:');
      console.log('  node test-sheets-connection.js');
      console.log('    C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json');
      console.log('    1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms');
      process.exit(1);
    }
  }
  
  // Get spreadsheet ID
  let spreadsheetId = args[1];
  if (!spreadsheetId) {
    // Try to load from config
    const configPath = path.join(__dirname, 'config', 'google-sheets.json');
    if (fs.existsSync(configPath)) {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      spreadsheetId = config.spreadsheetId;
      console.log('📋 Loaded spreadsheet ID from config');
    } else {
      console.log('❌ Spreadsheet ID required!');
      console.log('');
      console.log('Usage: node test-sheets-connection.js <service-account-path> <spreadsheet-id>');
      console.log('');
      console.log('Get your spreadsheet ID from the URL:');
      console.log('https://docs.google.com/spreadsheets/d/YOUR_ID_HERE/edit');
      console.log('');
      console.log('Or run the setup wizard first:');
      console.log('  node setup-google-sheets.js');
      process.exit(1);
    }
  }
  
  const success = await testConnection(serviceAccountPath, spreadsheetId);
  process.exit(success ? 0 : 1);
}

main().catch(error => {
  console.error('Unexpected error:', error);
  process.exit(1);
});




