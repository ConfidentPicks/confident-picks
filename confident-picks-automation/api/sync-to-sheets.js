/**
 * Vercel Serverless Function: Sync Firebase to Google Sheets
 * 
 * POST /api/sync-to-sheets
 * 
 * Syncs all picks from Firebase to Google Sheets for tracking and analysis
 */

const { initializeApp, cert } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');
const { initializeSheetsClient, syncFirebaseToSheets } = require('../lib/google-sheets');

// Initialize Firebase Admin (singleton)
let app;
let db;

function initializeFirebase() {
  if (app) return db;
  
  const credentials = {
    type: 'service_account',
    project_id: process.env.FIREBASE_PROJECT_ID,
    private_key_id: process.env.FIREBASE_PRIVATE_KEY_ID,
    private_key: process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
    client_email: process.env.FIREBASE_CLIENT_EMAIL,
    client_id: process.env.FIREBASE_CLIENT_ID,
    auth_uri: 'https://accounts.google.com/o/oauth2/auth',
    token_uri: 'https://oauth2.googleapis.com/token',
    auth_provider_x509_cert_url: 'https://www.googleapis.com/oauth2/v1/certs',
    client_x509_cert_url: `https://www.googleapis.com/robot/v1/metadata/x509/${encodeURIComponent(process.env.FIREBASE_CLIENT_EMAIL)}`,
  };
  
  app = initializeApp({
    credential: cert(credentials),
  });
  
  db = getFirestore(app);
  return db;
}

module.exports = async (req, res) => {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  const startTime = Date.now();
  
  try {
    console.log('🔄 Starting Firebase → Google Sheets sync...');
    
    // Validate environment variables
    if (!process.env.GOOGLE_SHEETS_SPREADSHEET_ID) {
      throw new Error('GOOGLE_SHEETS_SPREADSHEET_ID environment variable not set');
    }
    
    if (!process.env.FIREBASE_PROJECT_ID || !process.env.FIREBASE_PRIVATE_KEY) {
      throw new Error('Firebase credentials not properly configured');
    }
    
    // Initialize services
    const db = initializeFirebase();
    
    const credentials = {
      type: 'service_account',
      project_id: process.env.FIREBASE_PROJECT_ID,
      private_key_id: process.env.FIREBASE_PRIVATE_KEY_ID,
      private_key: process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
      client_email: process.env.FIREBASE_CLIENT_EMAIL,
      client_id: process.env.FIREBASE_CLIENT_ID,
      auth_uri: 'https://accounts.google.com/o/oauth2/auth',
      token_uri: 'https://oauth2.googleapis.com/token',
      auth_provider_x509_cert_url: 'https://www.googleapis.com/oauth2/v1/certs',
      client_x509_cert_url: `https://www.googleapis.com/robot/v1/metadata/x509/${encodeURIComponent(process.env.FIREBASE_CLIENT_EMAIL)}`,
    };
    
    const sheetsClient = initializeSheetsClient(credentials);
    
    // Perform sync
    const result = await syncFirebaseToSheets(
      sheetsClient,
      db,
      process.env.GOOGLE_SHEETS_SPREADSHEET_ID,
      process.env.GOOGLE_SHEETS_SHEET_NAME || 'Picks'
    );
    
    const duration = Date.now() - startTime;
    
    console.log(`✅ Sync completed in ${duration}ms`);
    
    return res.status(200).json({
      success: true,
      message: 'Firebase data synced to Google Sheets',
      pickCount: result.pickCount,
      duration: `${duration}ms`,
      timestamp: new Date().toISOString(),
    });
    
  } catch (error) {
    console.error('❌ Sync failed:', error);
    
    const duration = Date.now() - startTime;
    
    return res.status(500).json({
      success: false,
      error: error.message,
      duration: `${duration}ms`,
      timestamp: new Date().toISOString(),
    });
  }
};




