/**
 * GitHub Integration for Confident Picks
 * 
 * This allows you to sync picks to/from GitHub repositories
 * Perfect for version control, collaboration, and backup
 */

const fs = require('fs');
const path = require('path');
const { Octokit } = require('@octokit/rest');

/**
 * Initialize GitHub client
 * @param {string} token - GitHub personal access token
 * @returns {Object} GitHub client
 */
function initializeGitHubClient(token) {
  return new Octokit({
    auth: token,
  });
}

/**
 * Convert picks to CSV format for GitHub
 * @param {Array} picks - Array of pick objects
 * @returns {string} CSV content
 */
function picksToCSV(picks) {
  const headers = [
    'id',
    'league',
    'homeTeam',
    'awayTeam',
    'pick',
    'marketType',
    'odds',
    'modelConfidence',
    'tier',
    'status',
    'result',
    'commenceTime',
    'reasoning',
    'createdAt',
    'updatedAt'
  ];
  
  const csvRows = [headers.join(',')];
  
  picks.forEach(pick => {
    const row = headers.map(header => {
      let value = pick[header] || '';
      
      // Escape CSV values
      if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
        value = `"${value.replace(/"/g, '""')}"`;
      }
      
      return value;
    });
    
    csvRows.push(row.join(','));
  });
  
  return csvRows.join('\n');
}

/**
 * Convert CSV to picks format
 * @param {string} csvContent - CSV content from GitHub
 * @returns {Array} Array of pick objects
 */
function csvToPicks(csvContent) {
  const lines = csvContent.split('\n');
  if (lines.length < 2) return [];
  
  const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
  const picks = [];
  
  for (let i = 1; i < lines.length; i++) {
    if (!lines[i].trim()) continue;
    
    const values = lines[i].split(',').map(v => v.trim().replace(/"/g, ''));
    const pick = {};
    
    headers.forEach((header, index) => {
      let value = values[index] || '';
      
      // Convert numeric fields
      if (['odds', 'modelConfidence'].includes(header)) {
        value = parseFloat(value) || 0;
      }
      
      pick[header] = value;
    });
    
    picks.push(pick);
  }
  
  return picks;
}

/**
 * Sync Firebase picks to GitHub repository
 * @param {Object} githubClient - GitHub client
 * @param {Object} firebaseDb - Firebase Firestore instance
 * @param {string} owner - GitHub username/organization
 * @param {string} repo - Repository name
 * @param {string} filePath - File path in repository (e.g., 'data/picks.csv')
 * @param {string} branch - Branch name (default: 'main')
 */
async function syncFirebaseToGitHub(githubClient, firebaseDb, owner, repo, filePath, branch = 'main') {
  try {
    console.log('🔄 Syncing Firebase picks to GitHub...');
    
    // Get picks from Firebase
    const picksSnapshot = await firebaseDb.collection('live_picks').get();
    const picks = [];
    picksSnapshot.forEach(doc => {
      picks.push({ id: doc.id, ...doc.data() });
    });
    
    console.log(`📊 Found ${picks.length} picks in Firebase`);
    
    // Convert to CSV
    const csvContent = picksToCSV(picks);
    
    // Get current file SHA (for update)
    let sha = null;
    try {
      const { data } = await githubClient.rest.repos.getContent({
        owner,
        repo,
        path: filePath,
        ref: branch,
      });
      sha = data.sha;
    } catch (error) {
      // File doesn't exist yet, that's OK
      console.log('📄 Creating new file...');
    }
    
    // Upload to GitHub
    const { data } = await githubClient.rest.repos.createOrUpdateFileContents({
      owner,
      repo,
      path: filePath,
      message: `Update picks data - ${new Date().toISOString()}`,
      content: Buffer.from(csvContent).toString('base64'),
      sha,
      branch,
    });
    
    console.log(`✅ Successfully synced ${picks.length} picks to GitHub`);
    console.log(`   Repository: ${owner}/${repo}`);
    console.log(`   File: ${filePath}`);
    console.log(`   Commit: ${data.commit.sha}`);
    
    return { success: true, pickCount: picks.length, commitSha: data.commit.sha };
    
  } catch (error) {
    console.error('❌ Error syncing to GitHub:', error.message);
    throw error;
  }
}

/**
 * Import picks from GitHub repository to Firebase
 * @param {Object} githubClient - GitHub client
 * @param {Object} firebaseDb - Firebase Firestore instance
 * @param {string} owner - GitHub username/organization
 * @param {string} repo - Repository name
 * @param {string} filePath - File path in repository
 * @param {string} collection - Firebase collection name (default: 'qa_picks')
 * @param {string} branch - Branch name (default: 'main')
 */
async function importGitHubToFirebase(githubClient, firebaseDb, owner, repo, filePath, collection = 'qa_picks', branch = 'main') {
  try {
    console.log('🔄 Importing picks from GitHub to Firebase...');
    
    // Get file content from GitHub
    const { data } = await githubClient.rest.repos.getContent({
      owner,
      repo,
      path: filePath,
      ref: branch,
    });
    
    // Decode content
    const csvContent = Buffer.from(data.content, 'base64').toString('utf8');
    
    // Convert to picks
    const picks = csvToPicks(csvContent);
    
    console.log(`📊 Found ${picks.length} picks in GitHub`);
    
    // Upload to Firebase
    const batch = firebaseDb.batch();
    let uploadCount = 0;
    
    for (const pick of picks) {
      if (pick.id) {
        const docRef = firebaseDb.collection(collection).doc(pick.id);
        batch.set(docRef, {
          ...pick,
          updatedAt: new Date().toISOString(),
          source: 'github-import'
        }, { merge: true });
        uploadCount++;
      }
    }
    
    await batch.commit();
    
    console.log(`✅ Successfully imported ${uploadCount} picks to Firebase`);
    return { success: true, pickCount: uploadCount };
    
  } catch (error) {
    console.error('❌ Error importing from GitHub:', error.message);
    throw error;
  }
}

/**
 * Create a GitHub repository for picks data
 * @param {Object} githubClient - GitHub client
 * @param {string} repoName - Repository name
 * @param {string} description - Repository description
 * @param {boolean} isPrivate - Whether repository should be private
 */
async function createPicksRepository(githubClient, repoName, description = 'Confident Picks Data Repository', isPrivate = true) {
  try {
    console.log(`🔄 Creating GitHub repository: ${repoName}...`);
    
    const { data } = await githubClient.rest.repos.createForAuthenticatedUser({
      name: repoName,
      description,
      private: isPrivate,
      auto_init: true,
      gitignore_template: 'Node',
    });
    
    console.log(`✅ Repository created: ${data.html_url}`);
    
    // Create initial data structure
    const initialContent = `# Confident Picks Data

This repository contains betting picks data from the Confident Picks platform.

## Files

- \`data/picks.csv\` - Current picks data
- \`archive/\` - Historical data backups
- \`analysis/\` - Performance analysis files

## Usage

This data is automatically synced from Firebase. Do not edit manually unless you know what you're doing.

## Last Updated

${new Date().toISOString()}
`;
    
    await githubClient.rest.repos.createOrUpdateFileContents({
      owner: data.owner.login,
      repo: data.name,
      path: 'README.md',
      message: 'Initial commit - Confident Picks data repository',
      content: Buffer.from(initialContent).toString('base64'),
    });
    
    // Create data directory
    await githubClient.rest.repos.createOrUpdateFileContents({
      owner: data.owner.login,
      repo: data.name,
      path: 'data/.gitkeep',
      message: 'Create data directory',
      content: Buffer.from('').toString('base64'),
    });
    
    console.log('✅ Repository structure created');
    return data;
    
  } catch (error) {
    console.error('❌ Error creating repository:', error.message);
    throw error;
  }
}

/**
 * Get repository information
 * @param {Object} githubClient - GitHub client
 * @param {string} owner - GitHub username/organization
 * @param {string} repo - Repository name
 */
async function getRepositoryInfo(githubClient, owner, repo) {
  try {
    const { data } = await githubClient.rest.repos.get({
      owner,
      repo,
    });
    
    return {
      name: data.name,
      fullName: data.full_name,
      description: data.description,
      url: data.html_url,
      isPrivate: data.private,
      createdAt: data.created_at,
      updatedAt: data.updated_at,
      stars: data.stargazers_count,
      forks: data.forks_count,
    };
  } catch (error) {
    console.error('❌ Error getting repository info:', error.message);
    throw error;
  }
}

module.exports = {
  initializeGitHubClient,
  picksToCSV,
  csvToPicks,
  syncFirebaseToGitHub,
  importGitHubToFirebase,
  createPicksRepository,
  getRepositoryInfo,
};



