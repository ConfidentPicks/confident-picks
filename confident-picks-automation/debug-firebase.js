// Comprehensive Firebase debugging script
const https = require('https');

const projectId = 'confident-picks-app-8-25';
const region = 'us-central1';

// Test different possible function URLs and configurations
const testConfigs = [
  {
    name: 'Standard HTTPS Function',
    url: `https://${region}-${projectId}.cloudfunctions.net/test`
  },
  {
    name: 'Alternative URL Format 1',
    url: `https://${region}-${projectId}.cloudfunctions.net/helloWorld`
  },
  {
    name: 'Alternative URL Format 2', 
    url: `https://us-central1-${projectId}.cloudfunctions.net/test`
  },
  {
    name: 'HTTP (non-secure)',
    url: `http://${region}-${projectId}.cloudfunctions.net/test`
  },
  {
    name: 'Project URL Format',
    url: `https://${projectId}.cloudfunctions.net/test`
  }
];

function testUrl(config) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    
    const options = {
      method: 'GET',
      timeout: 10000,
      headers: {
        'User-Agent': 'Firebase-Functions-Test/1.0'
      }
    };
    
    const req = https.request(config.url, options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        const endTime = Date.now();
        resolve({
          name: config.name,
          url: config.url,
          status: res.statusCode,
          responseTime: endTime - startTime,
          data: data.substring(0, 1000),
          headers: res.headers,
          success: res.statusCode === 200
        });
      });
    });
    
    req.on('error', (err) => {
      reject({
        name: config.name,
        url: config.url,
        error: err.message,
        success: false
      });
    });
    
    req.on('timeout', () => {
      req.destroy();
      reject({
        name: config.name,
        url: config.url,
        error: 'Request timeout',
        success: false
      });
    });
    
    req.setTimeout(10000);
    req.end();
  });
}

async function debugFirebase() {
  console.log('🔍 Firebase Functions Debug Report');
  console.log('=====================================');
  console.log(`📋 Project ID: ${projectId}`);
  console.log(`🌍 Region: ${region}`);
  console.log(`⏰ Timestamp: ${new Date().toISOString()}`);
  console.log('');
  
  let successCount = 0;
  let totalTests = testConfigs.length;
  
  for (const config of testConfigs) {
    try {
      const result = await testUrl(config);
      const status = result.success ? '✅ SUCCESS' : '❌ FAILED';
      console.log(`${status} ${result.name}`);
      console.log(`   URL: ${result.url}`);
      console.log(`   Status: ${result.status}`);
      console.log(`   Response Time: ${result.responseTime}ms`);
      
      if (result.success) {
        console.log(`   Response: ${result.data}`);
        successCount++;
      } else {
        console.log(`   Response: ${result.data.substring(0, 200)}...`);
      }
      console.log('');
    } catch (error) {
      console.log(`❌ FAILED ${error.name}`);
      console.log(`   URL: ${error.url}`);
      console.log(`   Error: ${error.error}`);
      console.log('');
    }
  }
  
  console.log('📊 Summary');
  console.log('==========');
  console.log(`✅ Successful: ${successCount}/${totalTests}`);
  console.log(`❌ Failed: ${totalTests - successCount}/${totalTests}`);
  
  if (successCount === 0) {
    console.log('');
    console.log('🚨 DIAGNOSIS: No functions are responding');
    console.log('   Possible causes:');
    console.log('   1. Functions are not deployed');
    console.log('   2. Functions are deployed but not running');
    console.log('   3. Project configuration issue');
    console.log('   4. Authentication issue');
    console.log('   5. Wrong project ID or region');
    console.log('');
    console.log('🔧 RECOMMENDATIONS:');
    console.log('   1. Check Firebase Console manually');
    console.log('   2. Verify project ID and region');
    console.log('   3. Check if Functions service is enabled');
    console.log('   4. Try deploying a simple function');
  } else {
    console.log('');
    console.log('🎉 SUCCESS: Functions are working!');
  }
}

debugFirebase().catch(console.error);




