// Check Firebase Functions using REST API
const https = require('https');

// Firebase project info
const projectId = 'confident-picks-app-8-25';
const region = 'us-central1';

// Test different possible function URLs
const possibleUrls = [
  `https://${region}-${projectId}.cloudfunctions.net/test`,
  `https://${region}-${projectId}.cloudfunctions.net/helloWorld`,
  `https://${region}-${projectId}.cloudfunctions.net/healthCheck`,
  `https://${region}-${projectId}.cloudfunctions.net/collectData`,
  `https://${region}-${projectId}.cloudfunctions.net/generatePicks`,
  `https://${region}-${projectId}.cloudfunctions.net/scoreGames`
];

function testUrl(url) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    
    https.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        const endTime = Date.now();
        resolve({
          url,
          status: res.statusCode,
          responseTime: endTime - startTime,
          data: data.substring(0, 500),
          headers: res.headers
        });
      });
    }).on('error', (err) => {
      reject({
        url,
        error: err.message
      });
    });
  });
}

async function checkAllFunctions() {
  console.log('🔍 Checking Firebase Functions via REST API...');
  console.log(`📋 Project: ${projectId}`);
  console.log(`🌍 Region: ${region}`);
  console.log('');
  
  for (const url of possibleUrls) {
    try {
      const result = await testUrl(url);
      const status = result.status === 200 ? '✅' : result.status === 404 ? '❌' : '⚠️';
      console.log(`${status} ${result.url}`);
      console.log(`   Status: ${result.status}`);
      console.log(`   Response Time: ${result.responseTime}ms`);
      if (result.status === 200) {
        console.log(`   Response: ${result.data}`);
      } else {
        console.log(`   Response: ${result.data.substring(0, 100)}...`);
      }
      console.log('');
    } catch (error) {
      console.log(`❌ ${error.url}`);
      console.log(`   Error: ${error.error}`);
      console.log('');
    }
  }
}

checkAllFunctions();




