// Simple test to check Firebase Functions
console.log('Testing Firebase Functions...');

const https = require('https');

function testFunction() {
  return new Promise((resolve, reject) => {
    const url = 'https://us-central1-confident-picks-app-8-25.cloudfunctions.net/test';
    
    https.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        console.log('Status:', res.statusCode);
        console.log('Response:', data.substring(0, 200));
        resolve(res.statusCode);
      });
    }).on('error', (err) => {
      console.log('Error:', err.message);
      reject(err);
    });
  });
}

testFunction().then(status => {
  if (status === 200) {
    console.log('✅ Functions are working!');
  } else {
    console.log('❌ Functions not working - Status:', status);
  }
}).catch(err => {
  console.log('❌ Connection failed:', err.message);
});




