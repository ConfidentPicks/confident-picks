#!/usr/bin/env node

/**
 * GitHub Setup Script for Confident Picks
 * 
 * This script helps you set up GitHub integration for your picks data.
 * It will create a repository and configure the integration.
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
  console.log('\n🐙 GitHub Integration Setup for Confident Picks\n');
  console.log('This will create a GitHub repository for your picks data.\n');
  
  // Step 1: Check for GitHub token
  console.log('📋 Step 1: GitHub Authentication');
  console.log('─────────────────────────────────────');
  
  let githubToken = await question('Enter your GitHub Personal Access Token: ');
  
  if (!githubToken) {
    console.log('\n❌ GitHub token required!');
    console.log('\nTo get a token:');
    console.log('1. Go to: https://github.com/settings/tokens');
    console.log('2. Click "Generate new token" → "Generate new token (classic)"');
    console.log('3. Give it a name like "Confident Picks"');
    console.log('4. Select scopes: repo (full control)');
    console.log('5. Click "Generate token"');
    console.log('6. Copy the token and run this script again\n');
    rl.close();
    return;
  }
  
  // Step 2: Initialize GitHub client
  console.log('\n🔄 Initializing GitHub client...');
  
  try {
    const { initializeGitHubClient } = require('./lib/github');
    const githubClient = initializeGitHubClient(githubToken);
    
    // Test the token
    const { data: user } = await githubClient.rest.users.getAuthenticated();
    console.log(`✅ Authenticated as: ${user.login}`);
    console.log(`   Name: ${user.name || 'Not set'}`);
    console.log(`   Email: ${user.email || 'Not set'}`);
  } catch (error) {
    console.error('❌ GitHub authentication failed:', error.message);
    console.log('\nPlease check your token and try again.');
    rl.close();
    return;
  }
  
  // Step 3: Repository details
  console.log('\n\n📋 Step 2: Repository Configuration');
  console.log('─────────────────────────────────────');
  
  const repoName = await question('Repository name (e.g., confident-picks-data): ') || 'confident-picks-data';
  const description = await question('Description (optional): ') || 'Confident Picks betting data repository';
  
  const isPrivateChoice = await question('Make repository private? (yes/no): ');
  const isPrivate = isPrivateChoice.toLowerCase() === 'yes';
  
  console.log(`\n📊 Repository Details:`);
  console.log(`   Name: ${repoName}`);
  console.log(`   Description: ${description}`);
  console.log(`   Private: ${isPrivate ? 'Yes' : 'No'}`);
  
  const confirm = await question('\nCreate this repository? (yes/no): ');
  
  if (confirm.toLowerCase() !== 'yes') {
    console.log('\n❌ Repository creation cancelled.');
    rl.close();
    return;
  }
  
  // Step 4: Create repository
  console.log('\n🔄 Creating repository...');
  
  try {
    const { createPicksRepository } = require('./lib/github');
    const repo = await createPicksRepository(githubClient, repoName, description, isPrivate);
    
    console.log(`\n✅ Repository created successfully!`);
    console.log(`   URL: ${repo.html_url}`);
    console.log(`   Clone URL: ${repo.clone_url}`);
    
    // Step 5: Create configuration
    console.log('\n📋 Step 3: Creating Configuration');
    console.log('─────────────────────────────────────');
    
    const config = {
      githubToken,
      owner: repo.owner.login,
      repo: repo.name,
      filePath: 'data/picks.csv',
      branch: 'main',
      isPrivate,
      repositoryUrl: repo.html_url,
      createdAt: new Date().toISOString(),
    };
    
    const configDir = path.join(__dirname, 'config');
    if (!fs.existsSync(configDir)) {
      fs.mkdirSync(configDir, { recursive: true });
    }
    
    const configPath = path.join(configDir, 'github.json');
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
    console.log(`✅ Configuration saved to: ${configPath}`);
    
    // Step 6: Test connection
    console.log('\n📋 Step 4: Testing Connection');
    console.log('─────────────────────────────────────');
    
    const testConnection = await question('Would you like to test the connection now? (yes/no): ');
    
    if (testConnection.toLowerCase() === 'yes') {
      console.log('\n🔄 Testing connection...\n');
      
      try {
        const { getRepositoryInfo } = require('./lib/github');
        const repoInfo = await getRepositoryInfo(githubClient, repo.owner.login, repo.name);
        
        console.log('✅ Connection successful!');
        console.log(`   Repository: ${repoInfo.fullName}`);
        console.log(`   Description: ${repoInfo.description}`);
        console.log(`   Private: ${repoInfo.isPrivate ? 'Yes' : 'No'}`);
        console.log(`   Created: ${new Date(repoInfo.createdAt).toLocaleString()}`);
      } catch (error) {
        console.error('❌ Connection test failed:', error.message);
        rl.close();
        return;
      }
    }
    
    // Summary
    console.log('\n\n🎉 GitHub Integration Setup Complete!');
    console.log('═══════════════════════════════════════');
    console.log('\nYour GitHub repository is ready!');
    console.log(`\nRepository: ${repo.html_url}`);
    console.log('\nNext steps:');
    console.log('1. Run the sync script to upload your picks:');
    console.log('   node sync-github.js --to-github');
    console.log('\n2. Or use the API endpoints:');
    console.log('   /api/sync-to-github');
    console.log('   /api/import-from-github');
    console.log('\n3. Set up automated syncing in Vercel');
    console.log('\n4. Share the repository with your team');
    
    console.log('\n📚 Documentation:');
    console.log('   docs/GITHUB_INTEGRATION.md');
    
  } catch (error) {
    console.error('\n❌ Repository creation failed:', error.message);
    
    if (error.message.includes('already exists')) {
      console.log('\n🔧 Fix: Repository name already exists');
      console.log('Try a different name or delete the existing repository.');
    } else if (error.message.includes('token')) {
      console.log('\n🔧 Fix: Invalid GitHub token');
      console.log('Please check your token permissions and try again.');
    } else {
      console.log('\n🔧 Unknown error. Please check:');
      console.log('1. Internet connection');
      console.log('2. GitHub token permissions');
      console.log('3. Repository name availability');
    }
  }
  
  rl.close();
}

main().catch(error => {
  console.error('Error:', error);
  rl.close();
  process.exit(1);
});



