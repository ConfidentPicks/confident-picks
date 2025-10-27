// Test the helloWorld function specifically
const https = require('https');

function testHelloWorld() {
  return new Promise((resolve, reject) => {
    const url = 'https://us-central1-confident-picks-app-8-25.cloudfunctions.net/helloWorld';
    
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

async function testHello() {
  console.log('Testing helloWorld function...');
  
  try {
    const result = await testHelloWorld();
    console.log(`✅ ${result.url}`);
    console.log(`   Status: ${result.status}`);
    console.log(`   Response: ${result.data}`);
  } catch (error) {
    console.log(`❌ ${error.url}`);
    console.log(`   Error: ${error.error}`);
  }
}

testHello();




