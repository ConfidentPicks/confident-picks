// Test script to check Firebase Functions deployment
const https = require('https');

const testUrls = [
  'https://us-central1-confident-picks-app-8-25.cloudfunctions.net/test',
  'https://us-central1-confident-picks-app-8-25.cloudfunctions.net/healthCheck'
];

function testUrl(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        resolve({
          url,
          status: res.statusCode,
          data: data
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

async function testAllUrls() {
  console.log('Testing Firebase Functions...');
  
  for (const url of testUrls) {
    try {
      const result = await testUrl(url);
      console.log(`✅ ${url}`);
      console.log(`   Status: ${result.status}`);
      console.log(`   Response: ${result.data.substring(0, 200)}...`);
    } catch (error) {
      console.log(`❌ ${error.url}`);
      console.log(`   Error: ${error.error}`);
    }
    console.log('');
  }
}

testAllUrls();




