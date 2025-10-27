// Deploy Firebase Functions without CLI
const https = require('https');
const fs = require('fs');
const path = require('path');

// Read the service account key
const serviceAccountPath = path.join(__dirname, 'confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json');
const serviceAccount = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));

// Firebase project configuration
const projectId = 'confident-picks-app-8-25';
const region = 'us-central1';

// Simple function code
const functionCode = `
const functions = require('firebase-functions');

exports.test = functions.https.onRequest((req, res) => {
  res.status(200).json({
    message: 'Firebase Functions working via direct deployment!',
    timestamp: new Date().toISOString(),
    project: '${projectId}',
    deployed: true
  });
});

exports.healthCheck = functions.https.onRequest((req, res) => {
  res.status(200).json({
    success: true,
    message: 'Health check successful',
    timestamp: new Date().toISOString(),
    status: 'operational',
    project: '${projectId}'
  });
});
`;

console.log('🚀 Firebase Functions Direct Deployment');
console.log('=====================================');
console.log(`📋 Project: ${projectId}`);
console.log(`🌍 Region: ${region}`);
console.log(`⏰ Time: ${new Date().toISOString()}`);
console.log('');

// Test the functions after deployment
async function testFunctions() {
  const testUrls = [
    `https://${region}-${projectId}.cloudfunctions.net/test`,
    `https://${region}-${projectId}.cloudfunctions.net/healthCheck`
  ];
  
  console.log('🧪 Testing deployed functions...');
  
  for (const url of testUrls) {
    try {
      const result = await new Promise((resolve, reject) => {
        https.get(url, (res) => {
          let data = '';
          res.on('data', (chunk) => data += chunk);
          res.on('end', () => {
            resolve({
              url,
              status: res.statusCode,
              data: data.substring(0, 200)
            });
          });
        }).on('error', reject);
      });
      
      if (result.status === 200) {
        console.log(`✅ ${result.url}`);
        console.log(`   Response: ${result.data}`);
      } else {
        console.log(`❌ ${result.url} - Status: ${result.status}`);
      }
    } catch (error) {
      console.log(`❌ ${url} - Error: ${error.message}`);
    }
  }
}

// Since we can't actually deploy without CLI, let's test what we have
console.log('📝 Function Code Prepared:');
console.log('--------------------------');
console.log(functionCode);
console.log('');

console.log('⚠️  NOTE: Direct deployment without Firebase CLI is not possible.');
console.log('   Firebase Functions require the Firebase CLI or Google Cloud SDK.');
console.log('   The functions need to be deployed through the official tools.');
console.log('');

console.log('🔧 ALTERNATIVE SOLUTIONS:');
console.log('1. Use Google Cloud Console to deploy functions');
console.log('2. Use Google Cloud SDK instead of Firebase CLI');
console.log('3. Use Vercel Functions (which we tried earlier)');
console.log('4. Use Netlify Functions');
console.log('5. Use Railway or Render for deployment');
console.log('');

// Test current status
testFunctions();




