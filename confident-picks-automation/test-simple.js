#!/usr/bin/env node

/**
 * Test Script - Try different approaches to write to Google Sheets
 */

const fs = require('fs');
const path = require('path');
const { initializeApp, cert } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');
const { google } = require('googleapis');

async function main() {
  console.log('\n🧪 Testing Google Sheets Connection\n');
  
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
    // Test 1: Try to read from the sheet first
    console.log('\n🧪 Test 1: Reading from sheet...');
    try {
      const response = await sheetsClient.spreadsheets.values.get({
        spreadsheetId: config.spreadsheetId,
        range: 'A1:Z10', // Try without sheet name first
      });
      console.log('✅ Successfully read from sheet without sheet name');
      if (response.data.values) {
        console.log(`   Found ${response.data.values.length} rows`);
        console.log('   First row:', response.data.values[0] || 'empty');
      }
    } catch (error) {
      console.log('❌ Could not read without sheet name:', error.message);
    }
    
    // Test 2: Try with sheet name
    console.log('\n🧪 Test 2: Reading with sheet name...');
    try {
      const response = await sheetsClient.spreadsheets.values.get({
        spreadsheetId: config.spreadsheetId,
        range: `${config.sheetName}!A1:Z10`,
      });
      console.log('✅ Successfully read with sheet name');
      if (response.data.values) {
        console.log(`   Found ${response.data.values.length} rows`);
        console.log('   First row:', response.data.values[0] || 'empty');
      }
    } catch (error) {
      console.log('❌ Could not read with sheet name:', error.message);
    }
    
    // Test 3: Try writing to default sheet
    console.log('\n🧪 Test 3: Writing to default sheet...');
    try {
      const testData = [
        ['Test', 'Data', 'From', 'Firebase'],
        ['Row 2', 'More', 'Test', 'Data']
      ];
      
      await sheetsClient.spreadsheets.values.update({
        spreadsheetId: config.spreadsheetId,
        range: 'A1:D2', // Write to default sheet
        valueInputOption: 'USER_ENTERED',
        resource: { values: testData },
      });
      
      console.log('✅ Successfully wrote to default sheet!');
      console.log('   Check your Google Sheet - you should see test data in A1:D2');
      
    } catch (error) {
      console.log('❌ Could not write to default sheet:', error.message);
    }
    
    // Test 4: Get sheet names
    console.log('\n🧪 Test 4: Getting sheet names...');
    try {
      const response = await sheetsClient.spreadsheets.get({
        spreadsheetId: config.spreadsheetId,
      });
      
      console.log('✅ Sheet information:');
      console.log(`   Title: ${response.data.properties.title}`);
      console.log('   Sheet tabs:');
      response.data.sheets.forEach((sheet, index) => {
        console.log(`     ${index + 1}. "${sheet.properties.title}" (ID: ${sheet.properties.sheetId})`);
      });
      
    } catch (error) {
      console.log('❌ Could not get sheet info:', error.message);
    }
    
  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
  }
}

main();



