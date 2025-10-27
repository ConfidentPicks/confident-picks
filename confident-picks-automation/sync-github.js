#!/usr/bin/env node

/**
 * GitHub Sync Script for Confident Picks
 * 
 * Usage:
 *   node sync-github.js --to-github      # Sync Firebase → GitHub
 *   node sync-github.js --to-firebase    # Sync GitHub → Firebase
 *   node sync-github.js --both           # Sync both directions
 */

const fs = require('fs');
const path = require('path');
const { initializeApp, cert } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');
const {
  initializeGitHubClient,
  syncFirebaseToGitHub,
  importGitHubToFirebase,
} = require('./lib/github');

async function main() {
  console.log('\n🐙 GitHub ↔ Firebase Sync\n');
  
  // Parse command line arguments
  const args = process.argv.slice(2);
  const direction = args.includes('--to-firebase') ? 'to-firebase' 
    : args.includes('--to-github') ? 'to-github'
    : 'both';
  
  // Load configuration
  const configPath = path.join(__dirname, 'config', 'github.json');
  
  if (!fs.existsSync(configPath)) {
    console.error('❌ GitHub configuration not found!');
    console.log('Please run: node setup-github.js');
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
  
  // Initialize GitHub
  console.log('🐙 Initializing GitHub...');
  const githubClient = initializeGitHubClient(config.githubToken);
  console.log('✅ GitHub initialized');
  
  try {
    // Sync Firebase to GitHub
    if (direction === 'to-github' || direction === 'both') {
      console.log('\n📤 Syncing Firebase → GitHub...');
      const result = await syncFirebaseToGitHub(
        githubClient,
        db,
        config.owner,
        config.repo,
        config.filePath,
        config.branch
      );
      console.log(`✅ Synced ${result.pickCount} picks to GitHub`);
      console.log(`   Commit: ${result.commitSha}`);
      console.log(`   Repository: ${config.owner}/${config.repo}`);
    }
    
    // Sync GitHub to Firebase
    if (direction === 'to-firebase' || direction === 'both') {
      console.log('\n📥 Syncing GitHub → Firebase...');
      const result = await importGitHubToFirebase(
        githubClient,
        db,
        config.owner,
        config.repo,
        config.filePath,
        'qa_picks', // Import to QA collection for review
        config.branch
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



