#!/usr/bin/env node

/**
 * Complete Firebase Sync & Migration
 * 
 * 1. Pushes all predictions from Google Sheets to Firebase
 * 2. Migrates picks between collections based on game status
 */

const { execSync } = require('child_process');
const path = require('path');

console.log('\n🏈 COMPLETE FIREBASE SYNC & MIGRATION\n');
console.log('=' .repeat(70));
console.log(`📅 ${new Date().toLocaleString()}\n`);

try {
  // Step 1: Push predictions to Firebase
  console.log('📤 STEP 1: Pushing predictions to Firebase...\n');
  execSync('node push-nfl-picks-to-firebase.js', { 
    stdio: 'inherit',
    cwd: __dirname 
  });
  
  console.log('\n' + '='.repeat(70));
  
  // Step 2: Migrate picks between collections
  console.log('\n🔄 STEP 2: Migrating picks between collections...\n');
  execSync('node migrate-picks-between-collections.js', { 
    stdio: 'inherit',
    cwd: __dirname 
  });
  
  console.log('\n' + '='.repeat(70));
  console.log('✅ COMPLETE SYNC & MIGRATION FINISHED!');
  console.log('='.repeat(70) + '\n');
  
} catch (error) {
  console.error('\n❌ Error during sync/migration:', error.message);
  process.exit(1);
}


