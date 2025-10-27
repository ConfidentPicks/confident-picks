#!/usr/bin/env node

/**
 * Quick Setup for Your Specific Sheet
 * 
 * This script sets up Google Sheets integration with your specific sheet:
 * Sheet ID: 1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU
 * Sheet Name: My_NFL_Betting_Data1
 */

const fs = require('fs');
const path = require('path');

async function main() {
  console.log('\n🚀 Setting up Google Sheets for YOUR sheet...\n');
  
  // Your specific sheet details
  const YOUR_SHEET_ID = '1ZS01ra-72OA5p3wXyDcZdCHLT-U4_OWASTMR3tRrEmU';
  const YOUR_SHEET_NAME = 'My_NFL_Betting_Data1';
  
  console.log('📋 Your Sheet Details:');
  console.log(`   Name: ${YOUR_SHEET_NAME}`);
  console.log(`   ID: ${YOUR_SHEET_ID}`);
  console.log(`   URL: https://docs.google.com/spreadsheets/d/${YOUR_SHEET_ID}/edit\n`);
  
  // Step 1: Check service account file
  console.log('Step 1: Loading service account...');
  const serviceAccountPath = 'C:\\Users\\durel\\Downloads\\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json';
  
  if (!fs.existsSync(serviceAccountPath)) {
    console.error('❌ Service account file not found!');
    console.log('   Expected at:', serviceAccountPath);
    console.log('\nPlease check the file path and try again.');
    return;
  }
  
  let credentials;
  try {
    credentials = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
    console.log('✅ Service account loaded');
    console.log(`   Project: ${credentials.project_id}`);
    console.log(`   Email: ${credentials.client_email}\n`);
  } catch (error) {
    console.error('❌ Error reading service account:', error.message);
    return;
  }
  
  // Step 2: Check googleapis module
  console.log('Step 2: Checking dependencies...');
  try {
    require('googleapis');
    console.log('✅ googleapis module found\n');
  } catch (error) {
    console.log('❌ Installing googleapis module...');
    const { execSync } = require('child_process');
    try {
      execSync('npm install googleapis', { stdio: 'inherit' });
      console.log('✅ googleapis installed\n');
    } catch (installError) {
      console.error('❌ Failed to install googleapis:', installError.message);
      console.log('\nPlease run: npm install googleapis');
      return;
    }
  }
  
  // Step 3: Create config
  console.log('Step 3: Creating configuration...');
  const config = {
    spreadsheetId: YOUR_SHEET_ID,
    serviceAccountPath: serviceAccountPath,
    sheetName: YOUR_SHEET_NAME,
    syncDirection: 'both',
    autoSync: false,
    syncInterval: 3600000,
  };
  
  const configDir = path.join(__dirname, 'config');
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
  }
  
  const configPath = path.join(configDir, 'google-sheets.json');
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
  console.log(`✅ Configuration saved to: ${configPath}\n`);
  
  // Step 4: Test connection
  console.log('Step 4: Testing connection...');
  try {
    const { initializeSheetsClient, readSheet } = require('./lib/google-sheets');
    
    const sheetsClient = initializeSheetsClient(credentials);
    const rows = await readSheet(sheetsClient, YOUR_SHEET_ID, 'A1:K1');
    
    console.log('✅ Connection successful!\n');
    
    if (rows && rows.length > 0) {
      console.log('📊 Your sheet headers:');
      console.log('   ', rows[0].join(' | '));
    }
    
    console.log('\n🎉 Setup complete!\n');
    console.log('Next steps:');
    console.log('  1. Share your sheet with:');
    console.log(`     ${credentials.client_email}`);
    console.log('  2. Run: node sync-sheets.js --to-sheets');
    console.log('  3. Check your sheet for Firebase data\n');
    
  } catch (error) {
    console.error('❌ Connection test failed:', error.message);
    
    if (error.message.includes('permission')) {
      console.log('\n🔧 Fix: Share your sheet');
      console.log('1. Open your Google Sheet');
      console.log('2. Click "Share" button');
      console.log(`3. Add: ${credentials.client_email}`);
      console.log('4. Set permission to "Editor"');
      console.log('5. Click "Send"');
    } else if (error.message.includes('API has not been used')) {
      console.log('\n🔧 Fix: Enable Google Sheets API');
      console.log('1. Go to: https://console.cloud.google.com/apis/library/sheets.googleapis.com');
      console.log('2. Select project: confident-picks-app-8-25');
      console.log('3. Click "ENABLE"');
    } else {
      console.log('\n🔧 Unknown error. Please check:');
      console.log('1. Internet connection');
      console.log('2. Sheet ID is correct');
      console.log('3. Sheet exists and is accessible');
    }
  }
}

main().catch(error => {
  console.error('Unexpected error:', error);
});



