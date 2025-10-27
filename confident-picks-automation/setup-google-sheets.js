#!/usr/bin/env node

/**
 * Google Sheets Setup Script
 * 
 * This script helps you set up Google Sheets integration with your Firebase project.
 * It will guide you through the setup process and test the connection.
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function question(query) {
  return new Promise(resolve => rl.question(query, resolve));
}

async function main() {
  console.log('\n🚀 Google Sheets Integration Setup\n');
  console.log('This script will help you connect Google Sheets to your Firebase project.\n');
  
  // Step 1: Check for service account file
  console.log('📋 Step 1: Service Account Credentials');
  console.log('─────────────────────────────────────');
  
  const serviceAccountPath = await question('Enter the path to your Firebase service account JSON file: ');
  
  if (!fs.existsSync(serviceAccountPath)) {
    console.error('❌ Service account file not found!');
    console.log('\nPlease ensure the file path is correct.');
    rl.close();
    return;
  }
  
  let credentials;
  try {
    credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
    console.log('✅ Service account file loaded successfully!');
    console.log(`   Project ID: ${credentials.project_id}`);
    console.log(`   Service Account Email: ${credentials.client_email}`);
  } catch (error) {
    console.error('❌ Error reading service account file:', error.message);
    rl.close();
    return;
  }
  
  // Step 2: Enable Google Sheets API
  console.log('\n\n📋 Step 2: Enable Google Sheets API');
  console.log('─────────────────────────────────────');
  console.log('You need to enable the Google Sheets API for your project:');
  console.log('\n1. Go to: https://console.cloud.google.com/apis/library/sheets.googleapis.com');
  console.log(`2. Make sure project "${credentials.project_id}" is selected`);
  console.log('3. Click "ENABLE" button');
  console.log('4. Wait for the API to be enabled (takes a few seconds)');
  
  const apiEnabled = await question('\nHave you enabled the Google Sheets API? (yes/no): ');
  
  if (apiEnabled.toLowerCase() !== 'yes') {
    console.log('\n⚠️  Please enable the Google Sheets API and run this script again.');
    rl.close();
    return;
  }
  
  console.log('✅ Google Sheets API enabled!');
  
  // Step 3: Share spreadsheet
  console.log('\n\n📋 Step 3: Share Your Google Sheet');
  console.log('─────────────────────────────────────');
  console.log('To allow your Firebase app to access a Google Sheet, you must share it:');
  console.log('\n1. Open your Google Sheet');
  console.log('2. Click the "Share" button');
  console.log('3. Add this email address as an Editor:');
  console.log(`\n   ${credentials.client_email}\n`);
  console.log('4. Click "Send" or "Done"');
  
  const sheetShared = await question('\nHave you shared the sheet with the service account? (yes/no): ');
  
  if (sheetShared.toLowerCase() !== 'yes') {
    console.log('\n⚠️  Please share the sheet and run this script again.');
    rl.close();
    return;
  }
  
  console.log('✅ Sheet shared with service account!');
  
  // Step 4: Get spreadsheet ID
  console.log('\n\n📋 Step 4: Get Your Spreadsheet ID');
  console.log('─────────────────────────────────────');
  console.log('The spreadsheet ID is in the URL of your Google Sheet:');
  console.log('https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit');
  console.log('\nExample: If your URL is:');
  console.log('https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit');
  console.log('The ID is: 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms');
  
  const spreadsheetId = await question('\nEnter your spreadsheet ID: ');
  
  if (!spreadsheetId || spreadsheetId.length < 20) {
    console.error('❌ Invalid spreadsheet ID');
    rl.close();
    return;
  }
  
  console.log(`✅ Spreadsheet ID: ${spreadsheetId}`);
  
  // Step 5: Create config file
  console.log('\n\n📋 Step 5: Creating Configuration');
  console.log('─────────────────────────────────────');
  
  const config = {
    spreadsheetId,
    serviceAccountPath: path.resolve(serviceAccountPath),
    sheetName: 'Picks',
    syncDirection: 'both', // 'toSheets', 'toFirebase', or 'both'
    autoSync: false,
    syncInterval: 3600000, // 1 hour in milliseconds
  };
  
  const configPath = path.join(__dirname, 'config', 'google-sheets.json');
  const configDir = path.dirname(configPath);
  
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
  }
  
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
  console.log(`✅ Configuration saved to: ${configPath}`);
  
  // Step 6: Test connection
  console.log('\n\n📋 Step 6: Testing Connection');
  console.log('─────────────────────────────────────');
  
  const testConnection = await question('Would you like to test the connection now? (yes/no): ');
  
  if (testConnection.toLowerCase() === 'yes') {
    console.log('\n🔄 Testing connection...\n');
    
    try {
      // Import the library
      const { initializeSheetsClient, readSheet } = require('./lib/google-sheets');
      
      // Initialize client
      const sheetsClient = initializeSheetsClient(credentials);
      
      // Try to read the first row
      const rows = await readSheet(sheetsClient, spreadsheetId, 'A1:Z1');
      
      console.log('✅ Connection successful!');
      if (rows && rows.length > 0) {
        console.log(`✅ Read ${rows[0].length} columns from the sheet`);
        console.log(`   First row: ${rows[0].join(', ')}`);
      }
    } catch (error) {
      console.error('❌ Connection test failed:', error.message);
      console.log('\nPossible issues:');
      console.log('1. Google Sheets API is not enabled');
      console.log('2. Sheet is not shared with service account');
      console.log('3. Spreadsheet ID is incorrect');
      console.log('4. Network connectivity issues');
      rl.close();
      return;
    }
  }
  
  // Summary
  console.log('\n\n🎉 Setup Complete!');
  console.log('═══════════════════════════════════════');
  console.log('\nYou can now use Google Sheets with your Firebase project!');
  console.log('\nNext steps:');
  console.log('1. Run the sync script to sync data:');
  console.log('   node sync-sheets.js');
  console.log('\n2. Or use the API endpoints in your automation:');
  console.log('   /api/sync-to-sheets');
  console.log('   /api/import-from-sheets');
  console.log('\n3. Read the documentation:');
  console.log('   docs/GOOGLE_SHEETS.md');
  
  rl.close();
}

main().catch(error => {
  console.error('Error:', error);
  rl.close();
  process.exit(1);
});




