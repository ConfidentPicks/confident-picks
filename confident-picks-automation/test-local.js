// Test local Firebase Functions emulator
const https = require('https');

function testLocalUrl(url) {
  return new Promise((resolve, reject) => {
    const options = {
      rejectUnauthorized: false // For localhost testing
    };
    
    https.get(url, options, (res) => {
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

async function testLocalFunctions() {
  console.log('Testing local Firebase Functions emulator...');
  
  const localUrls = [
    'http://localhost:5001/confident-picks-app-8-25/us-central1/test',
    'http://localhost:5001/confident-picks-app-8-25/us-central1/healthCheck'
  ];
  
  for (const url of localUrls) {
    try {
      const result = await testLocalUrl(url);
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

testLocalFunctions();




