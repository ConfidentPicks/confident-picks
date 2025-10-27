// Check Firebase project status
const admin = require('firebase-admin');

// Initialize with service account
const serviceAccount = require('./confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  projectId: 'confident-picks-app-8-25'
});

async function checkFirebaseStatus() {
  try {
    console.log('Checking Firebase project status...');
    
    // Test Firestore connection
    const db = admin.firestore();
    const testDoc = await db.collection('test').doc('connection').get();
    console.log('✅ Firestore connection successful');
    
    // Check if we can list collections
    const collections = await db.listCollections();
    console.log(`✅ Found ${collections.length} collections`);
    
    // Try to check functions (this might not work with Admin SDK)
    console.log('❌ Cannot check Functions status with Admin SDK');
    
  } catch (error) {
    console.log('❌ Firebase connection failed:', error.message);
  }
}

checkFirebaseStatus();




